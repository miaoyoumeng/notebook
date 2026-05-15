#!/bin/bash
set -euo pipefail

# ---------- 配置 ----------
CRAWL_DELAY_MIN=${CRAWL_DELAY_MIN:-3}
CRAWL_DELAY_MAX=${CRAWL_DELAY_MAX:-10}
DAILY_MAX_PAGES=${DAILY_MAX_PAGES:-120}
STATE_DIR=${STATE_DIR:-${HOME}/.crawl}
OUTPUT_CSV=${OUTPUT_CSV:-${HOME}/.crawl/crawled_data.csv}
MARKDOWN_DIR=${MARKDOWN_DIR:-${HOME}/.crawl/markdown}
mkdir -p "$STATE_DIR" "$MARKDOWN_DIR"

LOG_FILE="$STATE_DIR/crawler.log"
PROCESSED_URLS_FILE="$STATE_DIR/processed_urls.txt"
DAILY_COUNT_FILE="$STATE_DIR/daily_count"
URLS_FILE="$STATE_DIR/urls_to_crawl.txt"

# ---------- 辅助函数 ----------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

random_delay() {
    delay=$(awk -v min=$CRAWL_DELAY_MIN -v max=$CRAWL_DELAY_MAX 'BEGIN{srand(); printf "%.1f", min+rand()*(max-min)}')
    log "等待 ${delay} 秒..."
    sleep "$delay"
}

check_daily_limit() {
    today=$(date +%Y-%m-%d)
    if [[ -f "$DAILY_COUNT_FILE" ]]; then
        saved_date=$(cut -d' ' -f1 "$DAILY_COUNT_FILE")
        saved_count=$(cut -d' ' -f2 "$DAILY_COUNT_FILE")
        if [[ "$saved_date" == "$today" ]]; then
            if [[ $saved_count -ge $DAILY_MAX_PAGES ]]; then
                log "今日已抓取 $saved_count 页，达到每日上限 $DAILY_MAX_PAGES，停止抓取。"
                return 1
            fi
            return 0
        fi
    fi
    echo "$today 0" > "$DAILY_COUNT_FILE"
    return 0
}

increment_daily_count() {
    today=$(date +%Y-%m-%d)
    if [[ -f "$DAILY_COUNT_FILE" ]]; then
        saved_date=$(cut -d' ' -f1 "$DAILY_COUNT_FILE")
        saved_count=$(cut -d' ' -f2 "$DAILY_COUNT_FILE")
        if [[ "$saved_date" == "$today" ]]; then
            new_count=$((saved_count + 1))
            echo "$today $new_count" > "$DAILY_COUNT_FILE"
        else
            echo "$today 1" > "$DAILY_COUNT_FILE"
        fi
    else
        echo "$today 1" > "$DAILY_COUNT_FILE"
    fi
}

mark_processed() {
    local url="$1"
    echo "$url" >> "$PROCESSED_URLS_FILE"
}

is_processed() {
    local url="$1"
    grep -Fxq "$url" "$PROCESSED_URLS_FILE" 2>/dev/null
}

# ---------- 获取所有需要抓取的 URL ----------
discover_urls() {
    if [[ -f "$URLS_FILE" ]] && [[ -s "$URLS_FILE" ]]; then
        log "使用已有的 URL 列表: $URLS_FILE"
        return
    fi
    log "正在从 https://www.stats.gov.cn/sj/ndsj/ 发现所有页面链接..."
    local map_output
    map_output=$(firecrawl map "https://www.stats.gov.cn/sj/ndsj/" --limit 500 --json 2>/dev/null)
    if [[ -z "$map_output" ]]; then
        log "错误：未发现任何 URL，请检查网络或 firecrawl 配置。"
        # exit 1
        return
    fi
    echo "$map_output" | grep -o '"url":"[^"]*"' | sed 's/"url":"//;s/"//' | grep 'stats.gov.cn' > "$URLS_FILE"
    if [[ ! -s "$URLS_FILE" ]]; then
        log "错误：未提取到有效 URL。"
        # exit 1
        return
    fi
    log "发现 $(wc -l < "$URLS_FILE") 个 URL"
}

# ---------- 抓取单个页面（仅爬取，不提取） ----------
crawl_one_page() {
    local url="$1"
    
    # 跳过 PDF 文件
    if [[ "$url" == *.pdf ]]; then
        log "跳过 PDF: $url"
        mark_processed "$url"
        return 0
    fi
    
    log "开始抓取: $url"
    echo "开始抓取: $url"

    # 生成安全的文件名
    local safe_name
    safe_name=$(echo -n "$url" | md5)
    local md_file="$MARKDOWN_DIR/${safe_name}.md"

    # 用 firecrawl 获取页面 Markdown
    if ! firecrawl scrape --url "$url" --format markdown --only-main-content -o "$md_file" 2>/dev/null; then
        log "警告: 无法获取 $url 的内容，跳过"
        rm -f "$md_file"
        mark_processed "$url"
        return 0
    fi
    
    if [[ ! -s "$md_file" ]]; then
        log "警告: $url 内容为空，跳过"
        rm -f "$md_file"
        mark_processed "$url"
        return 0
    fi

    # 记录 URL 到文件的映射
    echo "$url" >> "$MARKDOWN_DIR/${safe_name}.url"

    mark_processed "$url"

    mark_content=$(cat $md_file)
    extracted=$(extract_fields_with_llm "$url" "$mark_content")

    if [[ -z "$extracted" ]]; then
        log "警告: 从 $url 未提取到任何数据"
        rm -f "$md_file"
        return 0
    fi

    # 3. 处理每一行（TSV）
    local line
    while IFS=$'\t' read -r time region indicator value; do
        # 跳过空行或无效行
        if [[ -z "$time" && -z "$indicator" ]]; then
            continue
        fi
        append_to_csv "$time" "$region" "$indicator" "$value" "$url"
        log "  记录: $time | $region | $indicator | $value"
    done <<< "$extracted"


    while IFS=$'\\t' read -r time region indicator value; do
        # 跳过空行或无效行
        if [[ -z "$time" && -z "$indicator" ]]; then
            continue
        fi
        append_to_csv "$time" "$region" "$indicator" "$value" "$url"
        log "  记录: $time | $region | $indicator | $value"
    done <<< "$extracted"
    increment_daily_count
    log "完成抓取: $url -> $md_file"
    return 0
}

# ---------- 主抓取循环 ----------
crawl_all() {
    discover_urls
    local count=0
    while IFS= read -r url; do
        [[ -z "$url" ]] && continue
        if is_processed "$url"; then
            log "跳过已处理: $url"
            continue
        fi
        if ! check_daily_limit; then
            log "今日额度用尽，退出循环。"
            break
        fi
        crawl_one_page "$url"
        count=$((count + 1))
        random_delay
    done < "$URLS_FILE"
    log "本轮抓取完成，共处理 $count 页。"
}
# ---------- 从页面中提取字段 ----------
extract_fields_with_llm() {
    local url="$1"
    local content="$2"
    # 调用 Agent（当前 OpenClaw 环境）来解析内容
    # 注意：这里通过 `openclaw run` 将内容传递给 LLM，并期望得到 TSV 格式的提取结果
    local prompt="请从以下内容中提取所有统计表格数据行，每行输出为 TSV 格式（Tab-Separated Values）：时间\t区域\t指标项,\t指标值。不要输出任何其他解释。如果内容中没有“区域”，就默认填写 “全国”。 其中：“指标项” 命名规则是“抓取文章的标题”和“指标项” 整理成一个指标项，整理规则：不要标题中的日期和区域，其他内容保留，并保证整理后的指标项有可读性。\n\n需要解析的内容如下：\n $content"
    result=$(claude -p "$prompt" 2>/dev/null)
    echo "${result}"
    
}

# ---------- 追加 CSV 行 ----------
append_to_csv() {
    local time_val="$1"
    local region="$2"
    local indicator="$3"
    local value="$4"
    local url="$5"
    
    # 如果 CSV 文件不存在或为空，先写入表头
    if [[ ! -f "$OUTPUT_CSV" ]] || [[ ! -s "$OUTPUT_CSV" ]]; then
        echo "时间,区域,指标项,指标值,来源网址" > "$OUTPUT_CSV"
    fi
    if [ ! -z "$indicator" ]; then
        # 转义可能存在的逗号和换行符（简单处理：用双引号包裹）
        printf "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" "$time_val" "$region" "$indicator" "$value" "$url" >> "$OUTPUT_CSV"
    fi
    
}

# ---------- 状态查看 ----------
show_status() {
    discover_urls
    local total processed today_count
    total=$(wc -l < "$URLS_FILE")
    processed=$(wc -l < "$PROCESSED_URLS_FILE" 2>/dev/null || echo 0)
    today_count=$(cut -d' ' -f2 "$DAILY_COUNT_FILE" 2>/dev/null || echo 0)
    echo "总页面数: $total"
    echo "已处理页面: $processed"
    echo "今日已抓: $today_count / $DAILY_MAX_PAGES"
    echo "剩余页面: $((total - processed))"
    echo "Markdown 文件: $(ls "$MARKDOWN_DIR"/*.md 2>/dev/null | wc -l)"
}

# ---------- 重置状态 ----------
reset_state() {
    rm -f "$PROCESSED_URLS_FILE" "$DAILY_COUNT_FILE" "$URLS_FILE"
    log "状态已重置，CSV 和 Markdown 文件不受影响。"
}

# ---------- 命令行参数 ----------
MODE="${1:-full}"
case "$MODE" in
    full|resume)
        crawl_all
        ;;
    status)
        show_status
        ;;
    reset)
        reset_state
        ;;
    *)
        echo "用法: $0 {full|resume|status|reset}"
        exit 1
        ;;
esac
