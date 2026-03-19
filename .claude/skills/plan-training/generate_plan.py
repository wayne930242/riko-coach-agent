#!/usr/bin/env python3
"""
generate_plan.py — 訓練飲食菜單格式化腳本

從 stdin 讀取 JSON，輸出格式良好的 Markdown 菜單檔案。

JSON 輸入結構：
{
  "plan_type": "1d" | "1w" | "1m",
  "title": "計劃名稱",
  "goal": "目標描述",
  "start_date": "YYYY-MM-DD",
  "difficulty": "初學者|中階|進階",
  "equipment": ["器材1", "器材2"],
  "workout": {
    "days": [
      {
        "name": "Day 1",
        "focus": "上半身力量",
        "warmup": "暖身描述",
        "exercises": [
          {"name": "動作名稱", "sets": "4", "reps": "8-10", "rest": "90s", "rpe": "8", "notes": "注意事項"}
        ],
        "cooldown": "收操描述",
        "is_rest": false
      }
    ],
    "progression": "漸進超負荷說明"
  },
  "diet": {
    "daily_targets": {
      "calories": 2000,
      "protein": 150,
      "carbs": 200,
      "fat": 65
    },
    "notes": "飲食原則",
    "days": [
      {
        "name": "Day 1",
        "meals": [
          {
            "type": "早餐",
            "foods": "食物描述",
            "protein": 30, "carbs": 45, "fat": 15, "calories": 435
          }
        ]
      }
    ]
  }
}

用法：echo '<json>' | uv run --no-project python generate_plan.py <output_path>
"""

import json
import sys
from datetime import date
from pathlib import Path


PLAN_TYPE_LABELS = {
    "1d": "單日計劃",
    "1w": "週計劃",
    "1m": "月計劃",
}


def format_exercise_table(exercises: list) -> str:
    if not exercises:
        return "*（休息日，建議輕度伸展）*"

    lines = [
        "| 動作 | 組數 | 次數 / 時間 | 休息 | RPE | 備註 |",
        "|------|:----:|:-----------:|:----:|:---:|------|",
    ]
    for ex in exercises:
        name  = ex.get("name", "")
        sets  = ex.get("sets", "—")
        reps  = ex.get("reps", "—")
        rest  = ex.get("rest", "—")
        rpe   = ex.get("rpe", "—")
        notes = ex.get("notes", "")
        lines.append(f"| {name} | {sets} | {reps} | {rest} | {rpe} | {notes} |")

    return "\n".join(lines)


def format_macro_bar(value: int, total: int, label: str) -> str:
    pct = round(value / total * 100) if total > 0 else 0
    filled = round(pct / 5)
    bar = "█" * filled + "░" * (20 - filled)
    return f"`{bar}` {pct}% {label}"


def format_day_workout(day: dict, idx: int) -> str:
    name    = day.get("name", f"Day {idx + 1}")
    focus   = day.get("focus", "")
    is_rest = day.get("is_rest", False)
    warmup  = day.get("warmup", "")
    cooldown = day.get("cooldown", "")
    exercises = day.get("exercises", [])

    lines = [f"### {name}：{focus}"]

    if is_rest:
        lines += ["", "> 🛋️ 休息日 — 讓肌肉充分恢復，可做輕度伸展或散步"]
        return "\n".join(lines)

    if warmup:
        lines += ["", "**暖身（5-10 分鐘）**", f"> {warmup}"]

    lines += ["", "**主要訓練**", "", format_exercise_table(exercises)]

    if cooldown:
        lines += ["", "**收操（5 分鐘）**", f"> {cooldown}"]

    return "\n".join(lines)


def format_meal_row(meal: dict) -> str:
    mtype    = meal.get("type", "")
    foods    = meal.get("foods", "")
    protein  = meal.get("protein", 0)
    carbs    = meal.get("carbs", 0)
    fat      = meal.get("fat", 0)
    calories = meal.get("calories", 0)
    return f"| {mtype} | {foods} | {protein}g | {carbs}g | {fat}g | {calories} kcal |"


def format_day_diet(day: dict, idx: int) -> str:
    name  = day.get("name", f"Day {idx + 1}")
    meals = day.get("meals", [])

    total_p = sum(m.get("protein", 0) for m in meals)
    total_c = sum(m.get("carbs", 0) for m in meals)
    total_f = sum(m.get("fat", 0) for m in meals)
    total_k = sum(m.get("calories", 0) for m in meals)

    lines = [
        f"#### {name}",
        "",
        "| 餐次 | 食物 | 蛋白質 | 碳水 | 脂肪 | 熱量 |",
        "|------|------|:------:|:----:|:----:|:----:|",
    ]
    for meal in meals:
        lines.append(format_meal_row(meal))

    lines += [
        f"| **合計** | | **{total_p}g** | **{total_c}g** | **{total_f}g** | **{total_k} kcal** |",
    ]

    return "\n".join(lines)


def build_markdown(data: dict) -> str:
    plan_type  = data.get("plan_type", "1w")
    title      = data.get("title", "訓練飲食菜單")
    goal       = data.get("goal", "")
    start_date = data.get("start_date", date.today().isoformat())
    difficulty = data.get("difficulty", "")
    equipment  = data.get("equipment", [])
    workout    = data.get("workout", {})
    diet       = data.get("diet", {})
    type_label = PLAN_TYPE_LABELS.get(plan_type, plan_type)

    # ── 目錄 ──────────────────────────────────────────────────
    sections = []
    toc = ["## 目錄", ""]

    # ── 標頭 ──────────────────────────────────────────────────
    header = [
        f"# {title}",
        "",
        f"> **類型**：{type_label}　**開始日期**：{start_date}",
        f"> **目標**：{goal}",
    ]
    if difficulty:
        header.append(f"> **難度**：{difficulty}")
    if equipment:
        header.append(f"> **器材**：{', '.join(equipment)}")
    header += ["", "---", ""]
    sections.append("\n".join(header))

    # ── 訓練部分 ───────────────────────────────────────────────
    toc.append("- [訓練計劃](#訓練計劃)")
    workout_section = ["## 訓練計劃", ""]

    workout_days = workout.get("days", [])
    for i, day in enumerate(workout_days):
        workout_section.append(format_day_workout(day, i))
        workout_section.append("")

    progression = workout.get("progression", "")
    if progression:
        workout_section += [
            "### 漸進超負荷原則",
            "",
            f"> {progression}",
            "",
        ]

    sections.append("\n".join(workout_section))

    # ── 飲食部分 ───────────────────────────────────────────────
    toc.append("- [飲食計劃](#飲食計劃)")
    diet_section = ["## 飲食計劃", ""]

    targets = diet.get("daily_targets", {})
    if targets:
        cal = targets.get("calories", 0)
        p   = targets.get("protein", 0)
        c   = targets.get("carbs", 0)
        f   = targets.get("fat", 0)
        diet_section += [
            "### 每日巨量營養素目標",
            "",
            f"**總熱量目標：{cal} kcal**",
            "",
            format_macro_bar(p * 4, cal, f"蛋白質 {p}g"),
            format_macro_bar(c * 4, cal, f"碳水化合物 {c}g"),
            format_macro_bar(f * 9, cal, f"脂肪 {f}g"),
            "",
        ]

    diet_notes = diet.get("notes", "")
    if diet_notes:
        diet_section += [f"> 💡 {diet_notes}", ""]

    diet_days = diet.get("days", [])
    if diet_days:
        diet_section.append("### 每日菜單")
        diet_section.append("")
        for i, day in enumerate(diet_days):
            diet_section.append(format_day_diet(day, i))
            diet_section.append("")

    sections.append("\n".join(diet_section))

    # ── 目錄插入 ───────────────────────────────────────────────
    toc_str  = "\n".join(toc) + "\n\n---\n\n"
    all_text = sections[0] + toc_str + "\n\n".join(sections[1:])
    all_text += f"\n\n---\n*由 Coach Kai 於 {date.today().isoformat()} 自動生成*\n"

    return all_text


def main():
    if len(sys.argv) < 2:
        print("用法：echo '<json>' | python generate_plan.py <output_path>", file=sys.stderr)
        sys.exit(1)

    output_path = Path(sys.argv[1])

    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗：{e}", file=sys.stderr)
        sys.exit(1)

    content = build_markdown(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"✅ 菜單已儲存：{output_path}")


if __name__ == "__main__":
    main()
