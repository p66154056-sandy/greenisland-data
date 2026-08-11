# -*- coding: utf-8 -*-
"""
產生 REAL_TOURISM.json（⑫觀光人次用，不分村里，全綠島單一數字）
來源：
- 12_..._月份.csv （含「總計(Total)」列需排除）
- 12_..._年份.csv
資料來源：交通部觀光署觀光統計資料庫
"""
import json
import re
from common import load_csv, OUTPUT_DIR, YEARS


def parse_roc_year(s):
    m = re.match(r"\d+\((\d{4})\)", s)
    return int(m.group(1)) if m else None


def build_tourism():
    monthly_rows = load_csv("12_2015年至2024年綠島觀光遊憩據點人次統計_月份.csv")
    yearly_rows = load_csv("12_2015年至2024年綠島觀光遊憩據點人次統計_年份.csv")

    monthly = {y: [None] * 12 for y in YEARS}
    for r in monthly_rows:
        y = parse_roc_year(r[0])
        if y is None or y not in monthly:
            continue  # 跳過「總計(Total)」列
        m = int(r[1])
        monthly[y][m - 1] = int(r[2])

    yearly = {}
    for r in yearly_rows:
        y = parse_roc_year(r[0])
        if y is None:
            continue
        yearly[y] = int(r[1])

    result = {
        "monthly": {str(y): monthly[y] for y in YEARS},
        "yearly": [yearly[y] for y in YEARS],
    }

    with open(f"{OUTPUT_DIR}/REAL_TOURISM.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_TOURISM.json 完成")
    return result


if __name__ == "__main__":
    build_tourism()
