# -*- coding: utf-8 -*-
"""
產生 LU_AREA_DATA.json（⑩土地利用卡片，各分類面積比較用）

來源：
- 10_綠島國土利用調查107.csv
- 10_綠島國土利用調查112.csv
（欄位 area_ha 為使用者已經算好的各圖徵面積，單位公頃）

處理邏輯：
- 每份檔案裡，面積最大的一筆是「外圍海域」（LCODE_C1=04 水利利用土地底下，但實際是海面，
  不是陸地上的水利設施），予以排除，否則會讓其他 8 類的變化完全看不出來
- 排除後，依 LCODE_C1（9大分類）加總面積
"""
import csv
import json
from common import UPLOAD_DIR, OUTPUT_DIR


def aggregate(fname):
    path = f"{UPLOAD_DIR}/{fname}"
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header, data_rows = rows[0], rows[1:]
    c1_idx = header.index("LCODE_C1")
    area_idx = header.index("area_ha")

    max_row = max(data_rows, key=lambda r: float(r[area_idx]))
    print(f"  {fname} 排除最大筆（外圍海域）：LCODE_C1={max_row[c1_idx]}, area_ha={max_row[area_idx]}")

    agg = {}
    for r in data_rows:
        if r is max_row:
            continue
        c1 = r[c1_idx]
        area = float(r[area_idx])
        agg[c1] = agg.get(c1, 0) + area
    return {k: round(v, 2) for k, v in agg.items()}


def build_landuse_area():
    result = {
        "107": aggregate("10_綠島國土利用調查107.csv"),
        "112": aggregate("10_綠島國土利用調查112.csv"),
    }
    with open(f"{OUTPUT_DIR}/LU_AREA_DATA.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("LU_AREA_DATA.json 完成")
    return result


if __name__ == "__main__":
    build_landuse_area()
