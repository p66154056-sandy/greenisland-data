# -*- coding: utf-8 -*-
"""
產生 REAL_POPCHANGE.json（⑥人口增減用）

來源：
- 6_..._出生統計.csv
- 6_..._死亡統計.csv
- 6_..._人口消長統計.csv （鄉內遷入/遷出、官方社會增加人數等）

計算邏輯：
- 社會增加＝遷入人口數－遷出人口數（自行計算，非官方公布的 SOCIAL_INC_CNT，
  因官方數字與遷入減遷出有微小落差，詳見儀表板 i 說明）
- 總增加＝自然增加＋（自行計算的）社會增加
- 鄉內遷徙淨增＝鄉內遷入－鄉內遷出
- 各項「率」＝該項人數 ÷ 當年人口 × 1000（千分比），人口數需先跑過 build_population.py
  產生 REAL_DATA.json 後才能算
"""
import json
from common import load_csv, roc_to_west, is_green_island, is_december, YEARS, VILLAGES, VMAP, OUTPUT_DIR


def build_popchange():
    born_rows = [r for r in load_csv("6_2015年至2024年臺東縣村里出生統計.csv") if is_green_island(r)]
    dead_rows = [r for r in load_csv("6_2015年至2024年臺東縣村里死亡統計.csv") if is_green_island(r)]
    change_rows = [r for r in load_csv("6_2015年至2024年臺東縣村里人口消長統計.csv")
                   if is_green_island(r)]  # 此檔為年資料（INFO_TIME 無月份），不需篩 12M

    born = {v: {} for v in VILLAGES}
    for r in born_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        born[v][y] = int(r[6])  # BORN_CNT

    dead = {v: {} for v in VILLAGES}
    for r in dead_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        dead[v][y] = int(r[6])  # DEAD_CNT

    change = {v: {} for v in VILLAGES}
    for r in change_rows:
        v = VMAP[r[5]]
        y = roc_to_west(r[-1])
        change[v][y] = {
            "nature": int(r[6]),          # 自然增加人數（官方，= 出生-死亡，僅供對照）
            "entry_p": int(r[9]),         # 遷入人口數
            "exit_p": int(r[10]),         # 遷出人口數
            "entry_addr": int(r[11]),     # 鄉鎮區內住址變更之遷入人口數
            "exit_addr": int(r[12]),      # 鄉鎮區內住址變更之遷出人口數
        }

    # 讀取 REAL_DATA.json 取得人口數（算「率」的分母）；請先執行 build_population.py
    with open(f"{OUTPUT_DIR}/REAL_DATA.json", encoding="utf-8") as f:
        real_data = json.load(f)

    result = {}
    for v in VILLAGES:
        b = [born[v][y] for y in YEARS]
        d = [dead[v][y] for y in YEARS]
        nature = [bb - dd for bb, dd in zip(b, d)]
        entry_p = [change[v][y]["entry_p"] for y in YEARS]
        exit_p = [change[v][y]["exit_p"] for y in YEARS]
        social = [i - o for i, o in zip(entry_p, exit_p)]  # 自行計算（非官方數字，詳見說明）
        entry_addr = [change[v][y]["entry_addr"] for y in YEARS]
        exit_addr = [change[v][y]["exit_addr"] for y in YEARS]
        intra = [i - o for i, o in zip(entry_addr, exit_addr)]
        total = [n + s for n, s in zip(nature, social)]
        pop = real_data[v]["total"]

        def rate(arr):
            return [round(val / p * 1000, 2) if p else None for val, p in zip(arr, pop)]

        result[v] = {
            "born": b, "dead": d, "nature": nature,
            "entry_p": entry_p, "exit_p": exit_p, "social": social,
            "entry_addr": entry_addr, "exit_addr": exit_addr, "intra": intra,
            "total": total,
            "birthRate": rate(b), "deathRate": rate(d),
            "entryRate": rate(entry_p), "exitRate": rate(exit_p),
            "natureRate": rate(nature), "socialRate": rate(social),
            "intraRate": rate(intra), "totalRate": rate(total),
        }

    with open(f"{OUTPUT_DIR}/REAL_POPCHANGE.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("REAL_POPCHANGE.json 完成")
    return result


if __name__ == "__main__":
    build_popchange()
