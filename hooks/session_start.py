#!/usr/bin/env python3
"""
SessionStart Hook — 載入使用者記憶與健康概況
輸出的文字會被注入為 Claude 的 session 前置脈絡
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
PROFILE_FILE = PROJECT_DIR / "data" / "profile.md"
JOURNAL_DIR = PROJECT_DIR / "data" / "journal"


def load_profile() -> str:
    if not PROFILE_FILE.exists():
        return "（尚未建立健康檔案，請先執行 /say-hi）"
    return PROFILE_FILE.read_text(encoding="utf-8")


def load_recent_journals(days: int = 3) -> str:
    today = date.today()
    entries = []
    for i in range(days):
        d = today - timedelta(days=i)
        f = JOURNAL_DIR / f"{d.isoformat()}.md"
        if f.exists():
            content = f.read_text(encoding="utf-8")
            entries.append(f"### {d.isoformat()}\n{content}")
    if not entries:
        return "（近期無日誌記錄）"
    return "\n\n".join(entries)


def main():
    profile = load_profile()
    journals = load_recent_journals(days=3)
    today = date.today().isoformat()

    output = f"""## 📋 Session 記憶載入（{today}）

### 使用者健康檔案
{profile}

### 近 3 天日誌摘要
{journals}

---
記憶載入完成。根據以上資訊回應使用者，不需要主動提及「我載入了你的記憶」。
"""
    print(output)


if __name__ == "__main__":
    main()
