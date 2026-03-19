---
name: plan-training
description: 生成個人化訓練飲食菜單。支援單日（1d）、週計劃（1w）、月計劃（1m）。根據健康檔案、Garmin 數據，由健身教練和營養師合作規劃，並用腳本輸出格式化 Markdown 菜單。
argument-hint: [1d|1w|1m]
allowed-tools: Read Glob Bash Agent mcp__health-coach__get_today_stats mcp__health-coach__get_stats_range mcp__health-coach__get_recent_activities mcp__health-coach__get_sleep
---

# 生成訓練飲食菜單

使用者輸入：`$ARGUMENTS`

## 步驟 1：解析參數

從 `$ARGUMENTS` 判斷計劃類型：
- `1d` 或 `day` → 單日計劃
- `1w` 或 `week` 或空白 → 週計劃（預設）
- `1m` 或 `month` → 月計劃（以 4 週結構呈現）

若參數不清楚，詢問使用者。

## 步驟 2：讀取使用者資料

1. 用 Read 工具讀取 `data/profile.md`
   - 若不存在，告知使用者先執行 `/say-hi`，停止
2. 用 MCP 工具取得近期健康數據：
   - `get_today_stats`：今日狀態
   - `get_recent_activities`：最近運動記錄（了解目前實際水平）
   - `get_sleep`：最近睡眠（評估恢復狀態）

## 步驟 3：委派訓練計劃

用 Agent 工具呼叫 `fitness-coach`，傳入：

```
請根據以下資料，設計一份 [計劃類型] 的訓練計劃，輸出為 JSON 格式。

【使用者資料】
[profile.md 全文]

【近期 Garmin 數據】
[活動記錄摘要]

【JSON 格式要求】
回傳 workout 物件，包含：
- days: 陣列，每天包含：
  - name: "Day 1" 或 "週一" 等
  - focus: 訓練重點（如"上半身力量"、"有氧"、"休息"）
  - is_rest: true/false
  - warmup: 暖身說明（字串）
  - exercises: 陣列，每個動作包含 name、sets、reps、rest、rpe、notes
  - cooldown: 收操說明（字串）
- progression: 漸進超負荷原則說明

注意：
- 依據 Body Battery 和睡眠狀態調整強度
- 考慮使用者的舊傷和器材限制
- 難度標記為：初學者 / 中階 / 進階
```

## 步驟 4：委派飲食計劃

用 Agent 工具呼叫 `nutritionist`，傳入：

```
請根據以下資料，設計一份 [計劃類型] 的飲食計劃，輸出為 JSON 格式。

【使用者資料】
[profile.md 全文]

【訓練計劃摘要】
[步驟 3 的運動量和強度摘要]

【JSON 格式要求】
回傳 diet 物件，包含：
- daily_targets: { calories, protein, carbs, fat }（數字，單位 g / kcal）
- notes: 飲食原則（一段話）
- days: 陣列，每天包含：
  - name: "Day 1" 或 "週一"
  - meals: 陣列，每餐包含：
    - type: "早餐" | "午餐" | "晚餐" | "點心"
    - foods: 具體食物和份量（字串）
    - protein、carbs、fat、calories（數字）

注意：
- 根據使用者的飲食取得便利性（外食 / 自煮）給實際可執行的建議
- 考慮飲食限制和過敏
- 配合訓練日 vs 休息日調整碳水
```

## 步驟 5：組合 JSON 並執行腳本

將兩個 agent 的回傳結果組合成完整 JSON：

```json
{
  "plan_type": "[1d|1w|1m]",
  "title": "[使用者名稱] 的 [類型] 訓練飲食計劃",
  "goal": "[從 profile 取得的目標]",
  "start_date": "[今天日期 YYYY-MM-DD]",
  "difficulty": "[難度]",
  "equipment": ["[器材列表]"],
  "workout": { ... },
  "diet": { ... }
}
```

決定輸出路徑：`data/plans/YYYY-MM-DD-[1d|1w|1m].md`

用 Bash 工具執行腳本（注意 JSON 用單引號包覆、特殊字元跳脫）：

```bash
echo '<JSON 內容>' | uv run --no-project python .claude/skills/plan-training/generate_plan.py data/plans/<檔名>
```

## 步驟 6：告知使用者

腳本執行成功後，用 Coach Kai 語氣告訴使用者：

> 「你的 [類型] 菜單出爐了！已儲存到 `data/plans/[檔名]`。
>
> 重點摘要：
> - 🏋️ 訓練：[1-2 句重點]
> - 🥗 飲食：每日目標 [熱量] kcal，蛋白質 [g]g
>
> 有任何想調整的地方，直接說就好！」
