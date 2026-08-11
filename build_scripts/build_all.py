# -*- coding: utf-8 -*-
"""
一次執行所有資料處理腳本，產生完整的 data_export/ 資料夾。

使用方式：
    python3 build_all.py

注意：build_population 必須排在 build_popchange 之前執行
（popchange 的「率」需要用到 build_population 產生的 REAL_DATA.json 當分母）。
"""
from build_population import build_real_data, build_real_index
from build_county_towns import build_county_and_towns
from build_education import build_education
from build_marital import build_marital
from build_popchange import build_popchange
from build_elderly_alone import build_elderly_alone
from build_housing import build_housing
from build_tourism import build_tourism
from build_weather import build_weather
from build_medical import build_medical

if __name__ == "__main__":
    print("=== 開始產生所有資料 JSON ===")
    build_real_data()      # 必須在 build_popchange 之前（提供人口分母）
    build_real_index()
    build_county_and_towns()
    build_education()
    build_marital()
    build_popchange()      # 依賴 REAL_DATA.json
    build_elderly_alone()
    build_housing()
    build_tourism()
    build_weather()
    build_medical()
    print("=== 全部完成，輸出於 data_export/ ===")
