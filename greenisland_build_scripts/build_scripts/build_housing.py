# -*- coding: utf-8 -*-
"""
產生 REAL_HOUSING.json（⑧屋齡分布用）
來源：8_2015年至2019年臺東縣村里臺東縣行政區房屋屋齡統計.csv （僅 2015-2019 年，無 2020 年後資料）
7 個屋齡分組：0-10年 / 11-20年 / 21-30年 / 31-40年 / 41-50年 / 51-60年 / 61年以上
"""
import json
from common import load_csv, roc_to_west, is_green_island, VILLAGES, VMAP, OUTPUT_DIR

HOUSING_YEARS = list(range(2015, 2020))


def build_housing():
    rows = [r for r in load_csv("8_2015年至2019年臺東縣村里臺東縣行政區房屋屋齡統計.csv") if is_green_island(r)]
    data = {v: {} for v in VILLAGES}
    for r in rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        data[v][y] = [int(x) if x.strip() != "" else 0 for x in r[6:13]]

    result = {v: [data[v][y] for y in HOUSING_YEARS] for v in VILLAGES}

    with open(f"{OUTPUT_DIR}/REAL_HOUSING.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_HOUSING.json 完成")
    return result


if __name__ == "__main__":
    build_housing()
