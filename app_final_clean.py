
[import streamlit as st
import pandas as pd
import requests
import time
import folium
from konlpy.tag import Okt
from sklearn.cluster import KMeans
import numpy as np
from streamlit_folium import st_folium

# --------------------------
# ✅ 위험어 사전 정의
# --------------------------
danger_words = ['침수', '지하차도', '하천 범람', '대피', '폭우', '차 잠김', '도로 잠김', '정전', '단수', '갇힘', '통제', '지하철 침수', '도로 유실', '지옥', '공포', '헬게이트']

# --------------------------
# ✅ 위험어 점수 함수
# --------------------------
def count_danger_words(text):
    return sum(1 for word in danger_words if word in text)

def danger_score_to_risk_level(n):
    if n == 0:
        return 1
    elif n == 1:
        return 2
    else:
        return 3

# --------------------------
# ✅ 좌표 추출 (Kakao API)
# --------------------------
KAKAO_API_KEY = "115286bcd7c3ab9e37176a29d08e25b7"

def get_lat_lng_kakao(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200 and response.json()['documents']:
        doc = response.json()['documents'][0]
        return float(doc['y']), float(doc['x'])
    return None, None

# --------------------------
# ✅ 앱 시작
# --------------------------
st.title("🚨 실시간 트윗 기반 침수 위험 지도")

query = st.text_input("📍 트윗 키워드 입력", value="침수 OR 지하차도 OR 정전")

if st.button("🚀 트윗 수집 및 분석 시작"):
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABd%2B0gEAAAAAyCgw6GhEuAK8j1ly0OMJr5lI43g%3DG0XXqIF44Ay5dvDqNWaa6Gq6MtgWtu77WNhge4pSJnbYAnPiHz력"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": f"({query}) lang:ko -is:retweet",
        "max_results": 10,
        "tweet.fields": "created_at,text"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        st.error("❌ 트윗 수집 실패")
    else:
        tweets = response.json().get("data", [])
        locations, coords, texts, risks = [], [], [], []

        okt = Okt()
        for tweet in tweets:
            text = tweet['text']
            nouns = okt.nouns(text)
            filtered_nouns = [n for n in nouns if len(n) >= 2]
            for noun in filtered_nouns:
                lat, lng = get_lat_lng_kakao(noun)
                if lat:
                    risk = danger_score_to_risk_level(count_danger_words(text))
                    locations.append((lat, lng, text, risk))
                    coords.append((lat, lng))
                    texts.append(text)
                    risks.append(risk)
                    break
            time.sleep(1.5)

        # 지도 시각화
        m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
        color_map = {1: 'green', 2: 'orange', 3: 'red'}

        for lat, lng, text, risk in locations:
            folium.CircleMarker(
                location=[lat, lng],
                radius=6,
                color=color_map[risk],
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(f"<b>위험도: {risk}</b><br>{text[:60]}...", max_width=300),
                tooltip=f"위험도 {risk}단계"
            ).add_to(m)

        st.subheader("🗺️ 위험 지역 지도")
        st_folium(m, width=700)

        df = pd.DataFrame({
            '내용': texts,
            '위험도': risks
        })
        st.subheader("📋 위험 분석 결과")
        st.dataframe(df)
]
