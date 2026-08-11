# -*- coding: utf-8 -*-
"""
產生 COUNTY_DATA.json（全縣平均，③人口指標多時期比較線用）
與 ALL_TOWNS_DATA.json（16 鄉鎮 + 各村里，③比較對象選擇器用）

計算邏輯（全縣或全鄉平均，並非村里數字的簡單平均）：
- density：轄下所有村里「總人口」加總 ÷「反推面積」加總（面積 = 該村人口 ÷ 該村密度）
- household：轄下所有村里「戶數」的平均值
- aging / dependYoung / dependOld / dependTotal：轄下所有村里「幼年/青壯年/老年人口」
  加總後，用加總後的人數重新計算比例（不是各村比例的平均）
"""
import json
from common import load_csv, roc_to_west, is_december, YEARS, OUTPUT_DIR


def build_county_and_towns():
    pop_rows = [r for r in load_csv("1_2015年至2024年臺東縣村里人口統計.csv") if is_december(r, 10)]
    age3_rows = [r for r in load_csv("2_2015年至2024年臺東縣村里三段年齡組性別人口統計.csv") if is_december(r, -1)]
    idx_rows = [r for r in load_csv("3_2015年至2024年臺東縣村里人口指標.csv") if is_december(r, 13)]

    # key: (TOWN, VILLAGE, year)
    pop_by = {}
    for r in pop_rows:
        pop_by[(r[3], r[5], roc_to_west(r[10]))] = {"total": int(r[7]), "household": int(r[6])}

    age_by = {}
    for r in age3_rows:
        age_by[(r[3], r[5], roc_to_west(r[-1]))] = {"young": int(r[6]), "adult": int(r[9]), "old": int(r[12])}

    density_by = {}
    for r in idx_rows:
        try:
            density_by[(r[3], r[5], roc_to_west(r[13]))] = float(r[8])
        except ValueError:
            pass

    towns = sorted(set(k[0] for k in pop_by))

    def compute_avg(keys_villages):
        """keys_villages: list of (town, village) tuples -> 回傳該群組的年度平均統計"""
        total_pop = [0] * 10
        total_house = [0] * 10
        total_area = [0.0] * 10
        total_young = [0] * 10
        total_adult = [0] * 10
        total_old = [0] * 10
        n = [0] * 10
        for i, y in enumerate(YEARS):
            for town, village in keys_villages:
                p = pop_by.get((town, village, y))
                a = age_by.get((town, village, y))
                d = density_by.get((town, village, y))
                if not p or not a:
                    continue
                n[i] += 1
                total_pop[i] += p["total"]
                total_house[i] += p["household"]
                total_young[i] += a["young"]
                total_adult[i] += a["adult"]
                total_old[i] += a["old"]
                if d and d > 0:
                    total_area[i] += p["total"] / d
        return {
            "density": [round(total_pop[i] / total_area[i], 2) if total_area[i] > 0 else None for i in range(10)],
            "household": [round(total_house[i] / n[i], 1) if n[i] else None for i in range(10)],
            "aging": [round(total_old[i] / total_young[i] * 100, 2) if total_young[i] else None for i in range(10)],
            "dependYoung": [round(total_young[i] / total_adult[i] * 100, 2) if total_adult[i] else None for i in range(10)],
            "dependOld": [round(total_old[i] / total_adult[i] * 100, 2) if total_adult[i] else None for i in range(10)],
            "dependTotal": [round((total_young[i] + total_old[i]) / total_adult[i] * 100, 2) if total_adult[i] else None for i in range(10)],
        }

    def village_series(town, village):
        result = {"density": [], "household": [], "aging": [], "dependYoung": [], "dependOld": [], "dependTotal": []}
        for y in YEARS:
            p = pop_by.get((town, village, y))
            a = age_by.get((town, village, y))
            d = density_by.get((town, village, y))
            if not p or not a:
                for k in result:
                    result[k].append(None)
                continue
            result["density"].append(d)
            result["household"].append(p["household"])
            result["aging"].append(round(a["old"] / a["young"] * 100, 2) if a["young"] else None)
            result["dependYoung"].append(round(a["young"] / a["adult"] * 100, 2) if a["adult"] else None)
            result["dependOld"].append(round(a["old"] / a["adult"] * 100, 2) if a["adult"] else None)
            result["dependTotal"].append(round((a["young"] + a["old"]) / a["adult"] * 100, 2) if a["adult"] else None)
        return result

    # ---- 全縣平均 ----
    all_village_keys = sorted(set((k[0], k[1]) for k in pop_by))
    county_data = compute_avg(all_village_keys)
    with open(f"{OUTPUT_DIR}/COUNTY_DATA.json", "w", encoding="utf-8") as f:
        json.dump(county_data, f, ensure_ascii=False, indent=1)
    print("COUNTY_DATA.json 完成")

    # ---- 16 鄉鎮 + 各村里 ----
    all_towns_data = {}
    for town in towns:
        villages_in_town = sorted(set(k[1] for k in pop_by if k[0] == town))
        village_data = {}
        for village in villages_in_town:
            vs = village_series(town, village)
            # 若某村某年缺資料則整體排除該村（維持跟現行資料一致的「完整年份才收錄」原則）
            if all(v is not None for v in vs["density"]):
                village_data[village] = vs
        avg = compute_avg([(town, v) for v in villages_in_town])
        all_towns_data[town] = {"villages": village_data, "avg": avg}

    with open(f"{OUTPUT_DIR}/ALL_TOWNS_DATA.json", "w", encoding="utf-8") as f:
        json.dump(all_towns_data, f, ensure_ascii=False, indent=1)
    print("ALL_TOWNS_DATA.json 完成，共", len(towns), "個鄉鎮")

    return county_data, all_towns_data


if __name__ == "__main__":
    build_county_and_towns()
