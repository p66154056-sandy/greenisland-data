# -*- coding: utf-8 -*-
"""
共用工具函式：讀取政府開放資料 CSV 的共通邏輯
（社會經濟資料開放平台的檔案，前兩列是英文/中文欄位說明，第三列起才是資料）
"""
import csv
import re

import os

# 原始 CSV 放在 build_scripts/ 的上一層 raw_csv/ 資料夾（相對路徑，任何電腦上都能跑）
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(_THIS_DIR, "..", "raw_csv")
OUTPUT_DIR = os.path.join(_THIS_DIR, "..", "data")

YEARS = list(range(2015, 2025))
VILLAGES = ["南寮", "中寮", "公館"]
VMAP = {"南寮村": "南寮", "中寮村": "中寮", "公館村": "公館"}
VMAP_REV = {v: k for k, v in VMAP.items()}


def load_csv(filename):
    """讀取 CSV，跳過前兩列說明列，回傳資料列（list of list）"""
    path = f"{UPLOAD_DIR}/{filename}"
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    return rows[2:]


def roc_to_west(info_time):
    """民國年字串（例如 '109Y12M'、'104Y'）轉西元年整數"""
    m = re.match(r"(\d+)Y", info_time)
    return int(m.group(1)) + 1911


def is_green_island(row, town_col=3):
    return row[town_col] == "綠島鄉"


def is_december(row, time_col):
    """篩選 12 月（年底）快照資料；INFO_TIME 若無月份（如教育、出生死亡資料為 annual）則略過此檢查"""
    return row[time_col].endswith("12M")
