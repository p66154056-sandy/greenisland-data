# -*- coding: utf-8 -*-
"""
產生 REAL_MARITAL.json（⑤婚姻狀況用）

來源：
- 5_2_2015年至2018年...婚姻狀況統計.csv （2015-2018，4 類：M1未婚/M2有偶/M3離婚/M4喪偶，無同性欄位）
- 5_1_2019年至2024年...婚姻狀況統計.csv （2019-2024，7 類：多了 M5有偶同性/M6離婚同性/M7喪偶同性，
  因 2019/5/24 同婚專法上路，官方統計自此才有同性欄位）

2015-2018 年同性各項一律視為 0（當時法律上不存在同性有偶/離婚/喪偶登記）。
"""
import json
from common import load_csv, roc_to_west, is_green_island, YEARS, VILLAGES, VMAP, OUTPUT_DIR

KEYS = ["single", "married_hetero", "married_homo", "divorced_hetero", "divorced_homo", "widowed_hetero", "widowed_homo"]


def build_marital():
    early_rows = [r for r in load_csv("5_2_2015年至2018年臺東縣村里15歲以上人口婚姻狀況統計.csv")
                  if is_green_island(r)]
    late_rows = [r for r in load_csv("5_1_2019年至2024年臺東縣村里15歲以上人口婚姻狀況統計.csv")
                 if is_green_island(r)]

    data = {v: {} for v in VILLAGES}

    for r in early_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        data[v][y] = {
            "single": int(r[6]), "married_hetero": int(r[7]), "married_homo": 0,
            "divorced_hetero": int(r[8]), "divorced_homo": 0,
            "widowed_hetero": int(r[9]), "widowed_homo": 0,
        }

    for r in late_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        data[v][y] = {
            "single": int(r[6]),
            "married_hetero": int(r[7]), "married_homo": int(r[8]),
            "divorced_hetero": int(r[9]), "divorced_homo": int(r[10]),
            "widowed_hetero": int(r[11]), "widowed_homo": int(r[12]),
        }

    result = {}
    for v in VILLAGES:
        result[v] = {k: [data[v][y][k] for y in YEARS] for k in KEYS}

    with open(f"{OUTPUT_DIR}/REAL_MARITAL.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_MARITAL.json 完成")
    return result


if __name__ == "__main__":
    build_marital()
