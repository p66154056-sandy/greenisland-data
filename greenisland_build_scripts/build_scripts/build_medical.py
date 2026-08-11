# -*- coding: utf-8 -*-
"""
產生 MEDICAL_FACILITIES.json（⑨醫療機構用）

※ 注意：這份資料「沒有」對應的原始 CSV 檔案可供程式化解析，
是依使用者提供的查詢畫面截圖，手動整理成結構化資料。
資料來源：社會經濟資料開放平台－臺東縣村里醫療機構概況統計、診所喵－台東縣綠島鄉診所
此指標為現況統計，無時間序列。
"""
import json
from common import OUTPUT_DIR

MEDICAL_FACILITIES = {
    "南寮": [],
    "中寮": [
        {"name": "安康診所", "type": "西醫診所", "depts": "不分科（一般科）"},
        {"name": "臺東縣綠島鄉衛生所", "type": "衛生所", "depts": "內科、外科、牙科"},
    ],
    "公館": [],
}


def build_medical():
    with open(f"{OUTPUT_DIR}/MEDICAL_FACILITIES.json", "w", encoding="utf-8") as f:
        json.dump(MEDICAL_FACILITIES, f, ensure_ascii=False, indent=1)
    print("MEDICAL_FACILITIES.json 完成（手動整理資料，非 CSV 來源）")
    return MEDICAL_FACILITIES


if __name__ == "__main__":
    build_medical()
