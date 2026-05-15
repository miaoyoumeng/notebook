#!/usr/bin/env python3
#-*- coding:utf-8 -*-

__author__ = 'miaoyoumeng'


import asyncio
import re
import json
from pathlib import Path
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    TextBlock,
    AssistantMessage
)
from file_config import ROOT_DIR, PROJECT_ROOT_DIR, now_iso
from roles import (ZhongShuLing, MenXiaShiZhong, ShangShuLing,
    HrShangShu, HuBuShangShu, GongBuShangShu, XingBuShangShu, BingBuShangShu, LiBuShangShu)


async def discussion_meetting(topic: str):
    history = []

    
    # print("\n=== 讨论结束 ===")

async def main():
    await discussion_meetting(topic="下单功能")

if __name__ == '__main__':

    asyncio.run(main())

    print(json.dumps(ZhongShuLing, ensure_ascii=False))
