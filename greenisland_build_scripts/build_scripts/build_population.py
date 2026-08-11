# -*- coding: utf-8 -*-
"""
產生 REAL_DATA.json（①男女人口／②年齡結構用）與 REAL_INDEX.json（③人口指標用）

來源 CSV：
- 1_2015年至2024年臺東縣村里人口統計.csv        （總人口/戶數/男女）
- 2_..._三段年齡組性別人口統計.csv               （幼年/青壯年/老年 x 男女）
- 2_..._五歲年齡組人口統計.csv                    （5歲一組，21組）
- 3_2015年至2024年臺東縣村里人口指標.csv          （密度/老化指數/扶養比，官方精確值）
"""
import json
from common import load_csv, roc_to_west, is_green_island, is_december, YEARS, VILLAGES, VMAP, OUTPUT_DIR


def build_real_data():
    # ---- CSV1：總人口 / 戶數 / 男女 ----
    pop_rows = [r for r in load_csv("1_2015年至2024年臺東縣村里人口統計.csv")
                if is_green_island(r) and is_december(r, 10)]
    pop = {v: {} for v in VILLAGES}
    for r in pop_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[10])
        pop[v][y] = {"household": int(r[6]), "total": int(r[7]), "male": int(r[8]), "female": int(r[9])}

    # ---- CSV2 三段年齡組性別 ----
    age3_rows = [r for r in load_csv("2_2015年至2024年臺東縣村里三段年齡組性別人口統計.csv")
                 if is_green_island(r) and is_december(r, -1)]
    age3 = {v: {} for v in VILLAGES}
    for r in age3_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        age3[v][y] = {
            "young": int(r[6]), "young_m": int(r[7]), "young_f": int(r[8]),
            "adult": int(r[9]), "adult_m": int(r[10]), "adult_f": int(r[11]),
            "old": int(r[12]), "old_m": int(r[13]), "old_f": int(r[14]),
        }

    # ---- CSV2 五歲年齡組（21 組：0-4 ... 100+）----
    age5_rows = [r for r in load_csv("2_2015年至2024年臺東縣村里五歲年齡組人口統計.csv")
                 if is_green_island(r) and is_december(r, -1)]
    age5 = {v: {} for v in VILLAGES}
    for r in age5_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        age5[v][y] = [int(x) for x in r[6:27]]

    # ---- 組裝成 REAL_DATA 結構（欄位對應現行儀表板用的命名）----
    result = {}
    for v in VILLAGES:
        total = [pop[v][y]["total"] for y in YEARS]
        male = [pop[v][y]["male"] for y in YEARS]
        female = [pop[v][y]["female"] for y in YEARS]
        household = [pop[v][y]["household"] for y in YEARS]
        young = [age3[v][y]["young"] for y in YEARS]
        adult = [age3[v][y]["adult"] for y in YEARS]
        old = [age3[v][y]["old"] for y in YEARS]

        result[v] = {
            "total": total, "male": male, "female": female, "household": household,
            "sexRatio": [round(m / f * 100) for m, f in zip(male, female)],
            "agingIndex": [round(o / y_ * 100) for o, y_ in zip(old, young)],
            "dependYoung": [round(y_ / a * 100) for y_, a in zip(young, adult)],
            "dependOld": [round(o / a * 100) for o, a in zip(old, adult)],
            "young": young, "adult": adult, "old": old,
            "young_m": [age3[v][y]["young_m"] for y in YEARS],
            "young_f": [age3[v][y]["young_f"] for y in YEARS],
            "adult_m": [age3[v][y]["adult_m"] for y in YEARS],
            "adult_f": [age3[v][y]["adult_f"] for y in YEARS],
            "old_m": [age3[v][y]["old_m"] for y in YEARS],
            "old_f": [age3[v][y]["old_f"] for y in YEARS],
            "age5": [age5[v][y] for y in YEARS],
        }

    with open(f"{OUTPUT_DIR}/REAL_DATA.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_DATA.json 完成")
    return result


def build_real_index():
    # CSV3 欄位：SEX_RATIO(6), HHSIZE(7), DENSITY(8), DEPEND_RATIO(9), YOUNG_RATIO(10), OLD_RATIO(11), AGING(12)
    # 官方 CSV3 從 2023 年起（112Y）的扶養比/老化指數精度突然變成 8~10 位小數，
    # 早期年份則只有 1 位小數；為了呈現一致性，統一四捨五入到跟早期年份相同的精度。
    idx_rows = [r for r in load_csv("3_2015年至2024年臺東縣村里人口指標.csv")
                if is_green_island(r) and is_december(r, 13)]
    raw = {v: {} for v in VILLAGES}
    for r in idx_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[13])
        raw[v][y] = {
            "density": round(float(r[8]), 2),
            "dependYoung": round(float(r[10]), 1),
            "dependOld": round(float(r[11]), 1),
            "dependTotal": round(float(r[9]), 1),
            "aging": round(float(r[12]), 1),
        }

    result = {}
    for v in VILLAGES:
        result[v] = {
            "density": [raw[v][y]["density"] for y in YEARS],
            "dependTotal": [raw[v][y]["dependTotal"] for y in YEARS],
            "dependYoung": [raw[v][y]["dependYoung"] for y in YEARS],
            "dependOld": [raw[v][y]["dependOld"] for y in YEARS],
            "aging": [raw[v][y]["aging"] for y in YEARS],
        }

    with open(f"{OUTPUT_DIR}/REAL_INDEX.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_INDEX.json 完成")
    return result


if __name__ == "__main__":
    build_real_data()
    build_real_index()
