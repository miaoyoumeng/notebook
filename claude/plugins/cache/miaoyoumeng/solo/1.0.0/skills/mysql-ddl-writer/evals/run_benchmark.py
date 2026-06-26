#!/usr/bin/env python3
"""mysql-ddl-writer benchmark runner - validates assertions against generated DDL files."""

import json
import re
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# mysql-ddl-writer/evals -> mysql-ddl-writer -> office (project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
BASE_DIR = os.path.join(PROJECT_ROOT, "mysql-ddl-writer")
EVALS_FILE = os.path.join(BASE_DIR, "evals", "evals.json")


def read_ddl(file_path: str) -> str:
    """Read DDL file content."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r") as f:
        return f.read()


def count_pattern(text: str, pattern: str) -> int:
    """Count occurrences of a pattern in text."""
    return len(re.findall(pattern, text, re.IGNORECASE))


def extract_create_tables(text: str) -> list[str]:
    """Extract individual CREATE TABLE blocks."""
    blocks = re.split(r"CREATE TABLE IF NOT EXISTS", text, flags=re.IGNORECASE)
    result = []
    for block in blocks[1:]:  # skip preamble
        result.append("CREATE TABLE IF NOT EXISTS" + block)
    return result


def get_table_names(text: str) -> list[str]:
    """Extract table names from DDL."""
    return re.findall(r"CREATE TABLE IF NOT EXISTS `(\w+)`", text)


def check_snake_case(text: str) -> bool:
    """Check all table names and column names use snake_case."""
    table_names = get_table_names(text)
    for name in table_names:
        if not re.match(r"^[a-z][a-z0-9_]*$", name):
            return False
    for block in extract_create_tables(text):
        cols = re.findall(r"`(\w+)`", block)
        for col in cols:
            if col.upper() in ("BIGINT", "UNSIGNED", "NOT", "NULL", "AUTO_INCREMENT",
                               "DEFAULT", "CURRENT_TIMESTAMP", "ON", "UPDATE", "VARCHAR",
                               "TEXT", "INT", "TINYINT", "DATETIME", "DECIMAL", "JSON",
                               "PRIMARY", "KEY", "UNIQUE", "COMMENT", "ENGINE", "CHARSET",
                               "COLLATE", "COMMENT", "INDEX", "IF", "EXISTS", "TABLE"):
                continue
            if not re.match(r"^[a-z][a-z0-9_]*$", col):
                return False
    return True


def check_audit_fields(block: str) -> bool:
    """Check a CREATE TABLE block has audit fields."""
    return ("is_deleted" in block and "created_at" in block and "updated_at" in block)


def check_bigint_pk(block: str) -> bool:
    """Check id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT."""
    return bool(re.search(r"`id`\s+BIGINT\s+UNSIGNED\s+NOT\s+NULL\s+AUTO_INCREMENT", block, re.IGNORECASE))


def check_innodb_utf8mb4(block: str) -> bool:
    """Check ENGINE=InnoDB and CHARSET=utf8mb4."""
    return ("ENGINE=InnoDB" in block and "utf8mb4" in block)


def check_comments(block: str) -> bool:
    """Check all columns have COMMENT."""
    # Count column definitions and COMMENT clauses
    cols = re.findall(r"`\w+`\s+\w+", block)
    comments = re.findall(r"COMMENT\s+'[^']*'", block, re.IGNORECASE)
    # Filter out table-level COMMENT for column check
    col_defs = [c for c in cols if c.strip().lower().startswith(
        ("`id`", "`name`", "`title`", "`content`", "`status`", "`description`",
         "`phone`", "`email`", "`nickname`", "`sort_order`", "`points_required`",
         "`stock`", "`daily_limit`", "`category_id`", "`user_id`", "`product_id`",
         "`product_name`", "`points_spent`", "`order_id`", "`buyer_id`",
         "`total_amount`", "`pay_amount`", "`shipping_fee`", "`discount_amount`",
         "`order_no`", "`product_price`", "`product_spec`", "`product_image`",
         "`quantity`", "`subtotal`", "`shipping_company`", "`shipping_no`",
         "`ship_time`", "`sign_time`", "`refund_amount`", "`reason`",
         "`reviewer_id`", "`review_time`", "`rating`", "`images`",
         "`is_additional`", "`pay_method`", "`pay_status`", "`pay_time`",
         "`level_code`", "`level_name`", "`points_threshold`", "`valid_days`",
         "`benefits`", "`current_level`", "`total_points`", "`expire_time`",
         "`before_level`", "`after_level`", "`change_reason`", "`benefit_type`",
         "`usage_time`", "`register_time`", "`permissions`", "`role_id`",
         "`tag_id`", "`article_id`", "`parent_id`", "`view_count`",
         "`like_count`", "`comment_count`", "`collect_count`", "`cover_image`",
         "`author_id`", "`usage_count`", "`content`", "`follower_id`",
         "`followee_id`", "`opinion`", "`is_deleted`", "`created_at`", "`updated_at`",
         "`role`", "`result`", "`is_deleted`"))]
    # Simple check: every column def line should have COMMENT
    lines = block.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("`") and not stripped.startswith("--"):
            if "COMMENT" not in stripped.upper() and "PRIMARY KEY" not in stripped.upper():
                return False
    return True


def run_assertion(name: str, text: str, check_func, **kwargs) -> dict:
    """Run a single assertion."""
    try:
        passed = check_func(text, **kwargs)
        return {"name": name, "passed": bool(passed)}
    except Exception as e:
        return {"name": name, "passed": False, "error": str(e)}


def eval_positive_1(text: str, file_path: str) -> list[dict]:
    """Assertions for Eval 1: 积分商城."""
    results = []
    # 1. output_file_exists
    results.append(run_assertion("output_file_exists", text,
        lambda t, **k: os.path.exists(file_path) and os.path.getsize(file_path) > 0))
    # 2. contains_create_table (>= 2)
    results.append(run_assertion("contains_create_table", text,
        lambda t, **k: count_pattern(t, r"CREATE TABLE IF NOT EXISTS") >= 2))
    # 3. snake_case_naming
    results.append(run_assertion("snake_case_naming", text,
        lambda t, **k: check_snake_case(t)))
    # 4. bigint_auto_increment_pk
    blocks = extract_create_tables(text)
    all_pk = all(check_bigint_pk(b) for b in blocks)
    results.append({"name": "bigint_auto_increment_pk", "passed": all_pk})
    # 5. audit_fields_present
    all_audit = all(check_audit_fields(b) for b in blocks)
    results.append({"name": "audit_fields_present", "passed": all_audit})
    # 6. comments_on_tables_and_columns
    all_comments = all(check_comments(b) for b in blocks)
    results.append({"name": "comments_on_tables_and_columns", "passed": all_comments})
    # 7. innodb_utf8mb4
    all_engine = all(check_innodb_utf8mb4(b) for b in blocks)
    results.append({"name": "innodb_utf8mb4", "passed": all_engine})
    # 8. no_physical_foreign_keys
    results.append(run_assertion("no_physical_foreign_keys", text,
        lambda t, **k: count_pattern(t, r"FOREIGN\s+KEY") == 0))
    # 9. soft_delete_field
    all_soft = all(bool(re.search(r"`?is_deleted`?\s+TINYINT", b, re.IGNORECASE)) for b in blocks)
    results.append({"name": "soft_delete_field", "passed": all_soft})
    return results


def eval_positive_2(text: str, file_path: str) -> list[dict]:
    """Assertions for Eval 2: 用户管理系统."""
    results = []
    results.append(run_assertion("output_file_exists", text,
        lambda t, **k: os.path.exists(file_path) and os.path.getsize(file_path) > 0))
    results.append(run_assertion("three_tables_present", text,
        lambda t, **k: count_pattern(t, r"CREATE TABLE IF NOT EXISTS") >= 3))
    results.append(run_assertion("no_foreign_key_constraint", text,
        lambda t, **k: count_pattern(t, r"FOREIGN\s+KEY") == 0))
    results.append(run_assertion("all_fields_not_null_with_default", text,
        lambda t, **k: "NULL" not in t.replace("NOT NULL", "").replace("DEFAULT", "")))
    results.append(run_assertion("phone_email_indexed", text,
        lambda t, **k: bool(re.search(r"(UNIQUE\s+KEY|KEY).*?(phone|email)", t, re.IGNORECASE))))
    # Bridge table check
    tables = get_table_names(text)
    has_bridge = any("user" in t and "role" in t for t in tables)
    results.append({"name": "many_to_many_bridge_table", "passed": has_bridge})
    blocks = extract_create_tables(text)
    all_engine = all(check_innodb_utf8mb4(b) for b in blocks)
    results.append({"name": "innodb_utf8mb4", "passed": all_engine})
    return results


def eval_positive_3(text: str, file_path: str) -> list[dict]:
    """Assertions for Eval 3: 会员等级体系."""
    results = []
    tables = get_table_names(text)
    blocks = extract_create_tables(text)

    results.append({"name": "level_config_table_exists",
        "passed": any("level" in t or "grade" in t for t in tables)})
    results.append({"name": "user_level_table_exists",
        "passed": any("user" in t and "level" in t for t in tables)})
    results.append({"name": "level_change_log_exists",
        "passed": any(("log" in t or "history" in t) and "level" in t for t in tables)})
    # TINYINT for status/level columns
    results.append({"name": "tinyint_for_status",
        "passed": bool(re.search(r"`?(level|status)`?\s+TINYINT", text, re.IGNORECASE))})
    # ENUM comment on TINYINT
    tinyint_comments = re.findall(r"TINYINT.*?COMMENT\s+'([^']*)'", text, re.IGNORECASE)
    has_enum_comment = any(re.search(r"\d+-", c) for c in tinyint_comments)
    results.append({"name": "enum_comment_on_tinyint", "passed": has_enum_comment})
    results.append(run_assertion("no_enum_type", text,
        lambda t, **k: count_pattern(t, r"\bENUM\b") == 0))
    all_engine = all(check_innodb_utf8mb4(b) for b in blocks)
    results.append({"name": "innodb_utf8mb4", "passed": all_engine})
    all_audit = all(check_audit_fields(b) for b in blocks)
    results.append({"name": "audit_fields_present", "passed": all_audit})
    return results


def eval_positive_5(text: str, file_path: str) -> list[dict]:
    """Assertions for Eval 5: 订单管理系统."""
    results = []
    tables = get_table_names(text)
    blocks = extract_create_tables(text)

    results.append({"name": "order_table_exists",
        "passed": any("order" in t for t in tables)})
    results.append({"name": "order_item_snapshot_exists",
        "passed": any("order" in t and ("item" in t or "snapshot" in t) for t in tables)})
    # DECIMAL for amount, no FLOAT/DOUBLE
    results.append({"name": "decimal_for_amount",
        "passed": bool(re.search(r"`?(amount|price)`?\s+DECIMAL", text, re.IGNORECASE))})
    results.append({"name": "tinyint_for_order_status",
        "passed": bool(re.search(r"`?status`?\s+TINYINT", text, re.IGNORECASE))})
    # UNIQUE KEY on order no
    results.append({"name": "unique_key_on_order_no",
        "passed": bool(re.search(r"UNIQUE\s+KEY.*?(order_no|order.*no)", text, re.IGNORECASE))})
    results.append(run_assertion("no_float_double", text,
        lambda t, **k: count_pattern(t, r"\bFLOAT\b") + count_pattern(t, r"\bDOUBLE\b") == 0))
    all_engine = all(check_innodb_utf8mb4(b) for b in blocks)
    results.append({"name": "innodb_utf8mb4", "passed": all_engine})
    all_audit = all(check_audit_fields(b) for b in blocks)
    results.append({"name": "audit_fields_present", "passed": all_audit})
    results.append(run_assertion("no_physical_foreign_keys", text,
        lambda t, **k: count_pattern(t, r"FOREIGN\s+KEY") == 0))
    return results


def eval_positive_7(text: str, file_path: str) -> list[dict]:
    """Assertions for Eval 7: 内容平台."""
    results = []
    tables = get_table_names(text)
    blocks = extract_create_tables(text)

    results.append({"name": "article_table_exists",
        "passed": any(t in ("article", "post", "content") for t in tables)})
    results.append({"name": "comment_table_exists",
        "passed": any("comment" in t for t in tables)})
    results.append({"name": "tag_table_exists",
        "passed": any("tag" in t for t in tables)})
    # Bridge table for article-tag
    has_bridge = any("article" in t and "tag" in t for t in tables)
    results.append({"name": "article_tag_bridge_table", "passed": has_bridge})
    # Follower relation
    has_follower = "follower_id" in text and "followee_id" in text
    results.append({"name": "follower_relation_table", "passed": has_follower})
    results.append(run_assertion("multiple_tables_created", text,
        lambda t, **k: count_pattern(t, r"CREATE TABLE IF NOT EXISTS") >= 5))
    all_engine = all(check_innodb_utf8mb4(b) for b in blocks)
    results.append({"name": "innodb_utf8mb4", "passed": all_engine})
    all_audit = all(check_audit_fields(b) for b in blocks)
    results.append({"name": "audit_fields_present", "passed": all_audit})
    results.append(run_assertion("no_physical_foreign_keys", text,
        lambda t, **k: count_pattern(t, r"FOREIGN\s+KEY") == 0))
    results.append(run_assertion("snake_case_naming", text,
        lambda t, **k: check_snake_case(t)))
    return results


EVAL_MAP = {
    1: eval_positive_1,
    2: eval_positive_2,
    3: eval_positive_3,
    5: eval_positive_5,
    7: eval_positive_7,
}

OUTPUT_FILE_MAP = {
    1: "data/ddl/points-mall.sql",
    2: "data/ddl/ddl.sql",
    3: "data/ddl/member-level.sql",
    5: "data/ddl/order-system.sql",
    7: "data/ddl/content-platform.sql",
}


def main():
    with open(EVALS_FILE, "r") as f:
        evals_data = json.load(f)

    total_passed = 0
    total_failed = 0
    total_assertions = 0

    for eval_case in evals_data["evals"]:
        eval_id = eval_case["id"]
        prompt = eval_case["prompt"]

        # Skip negative test cases (should_trigger: false)
        if not eval_case.get("should_trigger", True):
            print(f"\n{'='*60}")
            print(f"Eval #{eval_id}: [NEGATIVE TEST] 跳过（should_trigger=false）")
            print(f"Prompt: {prompt[:80]}...")
            print(f"Result: N/A (验证 skill 不被触发，需人工确认)")
            continue

        if eval_id not in EVAL_MAP:
            print(f"\nEval #{eval_id}: 未实现验证逻辑，跳过")
            continue

        output_rel = OUTPUT_FILE_MAP[eval_id]
        output_abs = os.path.join(PROJECT_ROOT, output_rel)
        output_abs = os.path.normpath(output_abs)

        print(f"\n{'='*60}")
        print(f"Eval #{eval_id}")
        print(f"Prompt: {prompt[:100]}...")
        print(f"Output: {output_abs}")

        if not os.path.exists(output_abs):
            print(f"  [FAIL] 输出文件不存在: {output_abs}")
            for a in eval_case.get("assertions", []):
                print(f"    ❌ {a['name']}: 文件不存在")
                total_failed += 1
                total_assertions += 1
            continue

        text = read_ddl(output_abs)
        results = EVAL_MAP[eval_id](text, output_abs)

        case_passed = 0
        case_failed = 0
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            icon = "✅" if r["passed"] else "❌"
            print(f"    {icon} {r['name']}: {status}")
            if r.get("error"):
                print(f"       Error: {r['error']}")
            if r["passed"]:
                case_passed += 1
            else:
                case_failed += 1

        total_passed += case_passed
        total_failed += case_failed
        total_assertions += case_passed + case_failed
        print(f"  小计: {case_passed}/{case_passed + case_failed} 通过")

    # Negative tests summary
    print(f"\n{'='*60}")
    print("负向测试用例 (should_trigger=false)")
    print("  Eval #4: ORM 模型导出 DDL - 应不触发 skill (需人工确认)")
    print("  Eval #6: ALTER TABLE 加字段 - 应不触发 skill (需人工确认)")
    print("  Eval #8: 从数据库导出表结构 - 应不触发 skill (需人工确认)")

    print(f"\n{'='*60}")
    print(f"Benchmark 总结:")
    print(f"  通过: {total_passed}")
    print(f"  失败: {total_failed}")
    print(f"  总计: {total_assertions}")
    if total_assertions > 0:
        print(f"  通过率: {total_passed / total_assertions * 100:.1f}%")


if __name__ == "__main__":
    main()
