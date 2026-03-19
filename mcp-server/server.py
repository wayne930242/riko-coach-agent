"""
Coach Kai 健康助理 MCP Server

提供 Garmin 健康數據和日誌管理工具給 Claude Code 使用。
使用方式：uv run server.py
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 優先吃系統環境變數，.env 存在才補入（不覆寫）
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=False)

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL", "")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD", "")
JOURNAL_DIR = Path(__file__).parent.parent / "data" / "journal"

mcp = FastMCP("health-coach")

# ─── Garmin 工具 ───────────────────────────────────────────────

def _get_garmin_client():
    """取得 Garmin 客戶端（支援 token 快取）"""
    if not GARMIN_EMAIL or not GARMIN_PASSWORD:
        raise ValueError("請設定 GARMIN_EMAIL 和 GARMIN_PASSWORD（系統環境變數或 .env）")

    from garminconnect import Garmin

    token_dir = Path(__file__).parent / ".garmin_tokens"
    token_dir.mkdir(exist_ok=True)
    token_file = token_dir / "token.json"

    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    if token_file.exists():
        try:
            client.login(token_file)
            return client
        except Exception:
            pass

    client.login()
    client.garth.dump(str(token_file))
    return client


@mcp.tool()
def get_today_stats() -> str:
    """取得今日 Garmin 健康數據（步數、熱量、心率、壓力、Body Battery）"""
    try:
        client = _get_garmin_client()
        today = date.today().isoformat()
        stats = client.get_stats(today)

        result = {
            "日期": today,
            "步數": stats.get("totalSteps", 0),
            "步數目標": stats.get("dailyStepGoal", 10000),
            "活動消耗卡路里": stats.get("activeKilocalories", 0),
            "靜息心率": stats.get("restingHeartRate", 0),
            "最低心率": stats.get("minHeartRate", 0),
            "最高心率": stats.get("maxHeartRate", 0),
            "平均壓力指數": stats.get("averageStressLevel", 0),
            "最高壓力指數": stats.get("maxStressLevel", 0),
            "Body Battery 最高": stats.get("bodyBatteryHighestValue", 0),
            "Body Battery 最低": stats.get("bodyBatteryLowestValue", 0),
            "Body Battery 充電": stats.get("bodyBatteryChargedValue", 0),
            "Body Battery 消耗": stats.get("bodyBatteryDrainedValue", 0),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"無法取得數據：{e}"


@mcp.tool()
def get_stats_range(start_date: str, end_date: str) -> str:
    """取得指定日期範圍的每日健康數據摘要。日期格式：YYYY-MM-DD"""
    try:
        client = _get_garmin_client()
        from datetime import datetime

        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        results = []
        current = start
        while current <= end:
            d = current.isoformat()
            try:
                stats = client.get_stats(d)
                results.append({
                    "日期": d,
                    "步數": stats.get("totalSteps", 0),
                    "活動卡路里": stats.get("activeKilocalories", 0),
                    "靜息心率": stats.get("restingHeartRate", 0),
                    "平均壓力": stats.get("averageStressLevel", 0),
                    "Body Battery 最高": stats.get("bodyBatteryHighestValue", 0),
                    "Body Battery 最低": stats.get("bodyBatteryLowestValue", 0),
                })
            except Exception:
                results.append({"日期": d, "錯誤": "無法取得"})
            current += timedelta(days=1)

        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"無法取得數據：{e}"


@mcp.tool()
def get_sleep(start_date: str = "", end_date: str = "") -> str:
    """取得睡眠數據。不填日期則取今日。日期格式：YYYY-MM-DD"""
    try:
        client = _get_garmin_client()
        from datetime import datetime

        start = start_date or date.today().isoformat()
        end = end_date or start

        s = datetime.strptime(start, "%Y-%m-%d").date()
        e = datetime.strptime(end, "%Y-%m-%d").date()

        results = []
        current = s
        while current <= e:
            d = current.isoformat()
            try:
                sleep = client.get_sleep_data(d)
                daily = sleep.get("dailySleepDTO", {})
                scores = daily.get("sleepScores", {})
                results.append({
                    "日期": d,
                    "睡眠總時數（小時）": round(daily.get("sleepTimeSeconds", 0) / 3600, 1),
                    "深睡（小時）": round(daily.get("deepSleepSeconds", 0) / 3600, 1),
                    "REM（小時）": round(daily.get("remSleepSeconds", 0) / 3600, 1),
                    "淺睡（小時）": round(daily.get("lightSleepSeconds", 0) / 3600, 1),
                    "睡眠分數": scores.get("overall", {}).get("value", 0) if isinstance(scores.get("overall"), dict) else scores.get("overall", 0),
                })
            except Exception:
                results.append({"日期": d, "錯誤": "無法取得"})
            current += timedelta(days=1)

        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"無法取得睡眠數據：{e}"


@mcp.tool()
def get_recent_activities(limit: int = 10) -> str:
    """取得最近的運動活動記錄"""
    try:
        client = _get_garmin_client()
        activities = client.get_activities(0, limit)

        results = []
        for act in activities:
            results.append({
                "活動名稱": act.get("activityName", ""),
                "類型": act.get("activityType", {}).get("typeKey", ""),
                "日期": act.get("startTimeLocal", "")[:10],
                "時間（分鐘）": round(act.get("duration", 0) / 60, 1),
                "距離（公里）": round(act.get("distance", 0) / 1000, 2),
                "消耗卡路里": act.get("calories", 0),
                "平均心率": act.get("averageHR", 0),
                "最高心率": act.get("maxHR", 0),
            })

        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"無法取得活動數據：{e}"


# ─── 日誌工具 ───────────────────────────────────────────────────

@mcp.tool()
def list_journals() -> str:
    """列出所有健康日誌檔案（按日期排序）"""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(JOURNAL_DIR.glob("*.md"), reverse=True)
    if not files:
        return "目前沒有任何日誌記錄。"
    return "\n".join(f.name for f in files)


@mcp.tool()
def read_journal(date_str: str = "") -> str:
    """讀取指定日期的日誌。不填則讀今日日誌。日期格式：YYYY-MM-DD"""
    target = date_str or date.today().isoformat()
    journal_file = JOURNAL_DIR / f"{target}.md"

    if not journal_file.exists():
        return f"找不到 {target} 的日誌記錄。"

    return journal_file.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
