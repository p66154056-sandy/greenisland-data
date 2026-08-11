# -*- coding: utf-8 -*-
"""
產生 REAL_ELDERLY_ALONE.json（⑦獨居老人用）
來源：7_2020年臺東縣村里行政區獨居老人分析統計.csv （僅 2020 年單一次調查，無時間序列）
"""
import json
from common import load_csv, is_green_island, VILLAGES, VMAP, OUTPUT_DIR


def build_elderly_alone():
    rows = [r for r in load_csv("7_2020年臺東縣村里行政區獨居老人分析統計.csv") if is_green_island(r)]
    result = {}
    for r in rows:
        v = VMAP[r[5]]
        def n(x):
            return int(x) if x.strip() != "" else 0
        result[v] = {
            "young": [n(r[9]), n(r[10])],    # 65-74 [男, 女]
            "middle": [n(r[11]), n(r[12])],  # 75-84 [男, 女]
            "old": [n(r[13]), n(r[14])],     # 85以上 [男, 女]
        }
    with open(f"{OUTPUT_DIR}/REAL_ELDERLY_ALONE.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_ELDERLY_ALONE.json 完成")
    return result


if __name__ == "__main__":
    build_elderly_alone()
