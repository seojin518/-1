import streamlit as st
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
danger_words = [
    '침수', '지하차도', '하천 범람', '대피', '폭우', '차 잠김', '도로 잠김', '정전',
    '단수', '갇힘', '통제', '지하철 침수', '도로 유실', '지옥', '공포', '헬게이트'
]

# --------------------------
# ✅ 위험어 점수 함수
# --------------------------
def count_danger_words(text):
    return sum(1 for word in danger_words if word in text)

def danger_score_to_risk_level(n):
    if n == 0:
        return 1  # 안전
    elif n == 1:
        return 2  # 주의
    else:
        return 3  # 위험

# --------------------------
# ✅ 좌표 추출 (Kakao API)
# --------------------------
KAKAO_API_KEY = "115286bcd7c3ab9e37176a29d08e25b7"

def get_lat_lng_kakao(주소):
 URL = "https://dapi.kakao.com/v2/local/search/address.json "
 헤더 = {"권한 부여": f"KakaoAK {KAKAO_API_KEY}"}
 매개변수 = {"query": 주소}
 응답 = 요청.get(url, 헤더=headers, 파람=파람)
 if response.status_code == 200 이고 response.json ()['documents']:
 문서 = 응답.json ()['documents'][0]
 반환 플로트(doc['y']), 플로트(doc['x']) # 위도, 경도
 없음, 없음 반환


# --------------------------
# ✅ 스트림라이트 앱 실행
# --------------------------
st.title("🚨 실시간 트윗 기반 침수 위험 지도")

쿼리 = st.text_input (" 📍 트윗 키워드 입력", value="침수 OR 지하차도 OR 정전")

if st.button("🚀 트윗 수집 및 분석 시작"):
 BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABd%2B0gEAAAAAyCgw6GhEuAK8j1ly0OMJr5lI43g%3DG0XXQIF44Ay5dvDqNWaa6Gq6MtgWtu77WNhge4pSJnbYAnPiHz"
 헤더 = {"권한 부여": f"베어러 {BEARER_TOKEN}"}
 URL = "https://api.twitter.com/2/tweets/search/recent "
 매개변수 = {
 "query": f"{query} lang:ko -is:retweet",
 "max_results": 10,
 트윗.필드": "created_at,text"
 }

 응답 = 요청.get(url, 헤더=headers, 파람=파람)
 if response.status_code!= 200:
 st.error("❌ 트윗 수집 실패")
 그렇지 않으면:
 트윗 = 응답.json ()을 가져옵니다 ("데이터", [])
 위치, 선반, 텍스트, 위험 = [], [], [], []
 okt = okt ()

 트윗에 대한 트윗:
 텍스트 = 트윗 ['텍스트']
 명사 = okt.nouns(텍스트)
 필터링된_nouns = [명사에서 n 의 경우 렌(n) >= 2]

 필터링된_nouns의 명사에 대해:
 lat, lng = get_lat_lng_kakao(noun)
 라트 및 LNG 인 경우:
 위험 = danger_score_to_risk_level (count_danger_words(텍스트))
 위치.append((라트, LNG, 텍스트, 위험))
 latngs. append((lat, lng))
                    texts.append(text)
                    risks.append(risk)
                    break
                time.sleep(1.5)

 # 지도 시각화
 m = 폴륨.지도(위치=[37.5665, 126.9780], zoom_start=11)
 color_map = {1: '녹색', 2: 'orange', 3: '빨간색'}

 lat, lng, 텍스트, 위치 위험:
 엽록소.서클마커(
 위치=[lat, lng],
 반지름=6,
 color=color_map[위험],
 채움=참,
 채움 불투명도=0.7,
 팝업=폴륨.팝업(f"<b>위험도: {위험}//b><br>{텍스트[:60]}..., max_width=300),
 툴팁=f"위험도 {리스크}단계"
 ). add_to(m)

 세인트 서브헤더 ("🗺️ 위험 지역 지도")
 st_folium(m, 너비=700)

        # 데이터프레임 표시
 df = pd.데이터프레임({
 '내용': 텍스트,
 '위험도': 위험
        })

 세인트 서브헤더 ("📋 위험 분석 결과")
 st.dataframe(df)
