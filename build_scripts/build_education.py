# -*- coding: utf-8 -*-
"""
產生 REAL_EDU.json（④教育程度用）

來源：4_..._15歲以上人口五歲年齡組教育程度統計.csv（年資料，無月份）
原始欄位：11 個五歲年齡分組（15-19 ... 65UP）各自 9 個教育代碼欄位
（欄位代碼 E1314/E1112/E2122/E3_4_5/E6_7/E8_9/E1_2/E03/E04，由高學歷到低學歷排列）

處理邏輯：
1. 11 個五歲分組 → 合併成 6 個十歲分組（AGE_BANDS），65+ 維持獨立一組
2. CSV 的 9 個代碼欄位「由高到低」，對應到 EDU_CATS「由低到高」需要反轉
3. 每個年齡分組內，9 類人數加總後轉換成百分比（eduByYear）
4. 另外整理成「各分組 x 各類別」的10年趨勢（eduSeries），供單村多時期折線圖使用
"""
import json
from common import load_csv, roc_to_west, is_green_island, YEARS, VILLAGES, VMAP, OUTPUT_DIR

EDU_CATS = ["不識字", "自修", "國小", "國中", "高中職", "專科", "大學", "碩士", "博士"]
AGE_BANDS = ["15-24", "25-34", "35-44", "45-54", "55-64", "65+"]

# 每個十歲分組由哪幾個五歲分組合併（依 CSV 欄位區塊順序，每區塊 9 欄）
FIVE_YEAR_BLOCKS = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44",
                     "45-49", "50-54", "55-59", "60-64", "65UP"]
BAND_MERGE = {
    "15-24": ["15-19", "20-24"],
    "25-34": ["25-29", "30-34"],
    "35-44": ["35-39", "40-44"],
    "45-54": ["45-49", "50-54"],
    "55-64": ["55-59", "60-64"],
    "65+": ["65UP"],
}


def build_education():
    rows = [r for r in load_csv("4_2015年至2024年臺東縣村里15歲以上人口五歲年齡組教育程度統計.csv")
            if is_green_island(r)]

    # 每個五歲區塊在列中的起始欄位（欄位 0-5 是縣市代碼等，第 6 欄開始每 9 欄一組）
    block_start = {block: 6 + i * 9 for i, block in enumerate(FIVE_YEAR_BLOCKS)}

    # raw[village][year][block] = [9 個類別人數，CSV 原始順序（高學歷→低學歷）]
    raw = {v: {} for v in VILLAGES}
    for r in rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])  # 年資料 INFO_TIME 格式為 "104Y"（無月份）
        if y not in YEARS:
            continue
        raw[v].setdefault(y, {})
        for block in FIVE_YEAR_BLOCKS:
            s = block_start[block]
            raw[v][y][block] = [int(x) for x in r[s:s + 9]]

    result = {}
    for v in VILLAGES:
        edu_by_year = []  # [年份索引][分組索引] = 9 個百分比
        edu_series = [[[] for _ in EDU_CATS] for _ in AGE_BANDS]  # [分組][類別] = 10年序列

        for y in YEARS:
            year_bands = []
            for band in AGE_BANDS:
                # 合併對應的五歲區塊，CSV 原始順序加總
                merged = [0] * 9
                for block in BAND_MERGE[band]:
                    vals = raw[v][y][block]
                    merged = [a + b for a, b in zip(merged, vals)]
                # CSV 順序是「高學歷→低學歷」，EDU_CATS 是「低學歷→高學歷」，故反轉
                merged_reversed = merged[::-1]
                total = sum(merged_reversed)
                pct = [round(x / total * 100, 1) if total else 0 for x in merged_reversed]
                year_bands.append(pct)
            edu_by_year.append(year_bands)

        for band_idx in range(len(AGE_BANDS)):
            for cat_idx in range(len(EDU_CATS)):
                edu_series[band_idx][cat_idx] = [edu_by_year[y_i][band_idx][cat_idx] for y_i in range(10)]

        result[v] = {"eduByYear": edu_by_year, "eduSeries": edu_series}

    with open(f"{OUTPUT_DIR}/REAL_EDU.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_EDU.json 完成")
    return result


if __name__ == "__main__":
    build_education()
