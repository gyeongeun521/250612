import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("seoul_toilets.csv")  # 이 파일에는 위도, 경도, 건물명, 개방시간, 주소 등이 포함되어야 합니다.

df = load_data()

# 주소 → 좌표 변환 함수
def geocode_address(address):
    geolocator = Nominatim(user_agent="toilet_locator")
    location = geolocator.geocode(f"{address}, Seoul, South Korea")
    return (location.latitude, location.longitude) if location else None

# 최근접 화장실 5개 추출 함수
def find_nearest_toilets(user_location, df, n=5):
    df["거리(km)"] = df.apply(
        lambda row: geodesic(user_location, (row["위도"], row["경도"])).km, axis=1
    )
    return df.sort_values("거리(km)").head(n)

# 스트림릿 앱 UI
st.title("🚻 서울시 공중화장실 지도")
address = st.text_input("도로명 주소를 입력하세요 (예: 서울특별시 중구 세종대로 110)", "")

if address:
    user_location = geocode_address(address)
    
    if user_location:
        st.success("주소를 성공적으로 찾았습니다.")
        
        # 가까운 화장실 5곳 찾기
        nearest = find_nearest_toilets(user_location, df)
        
        # 지도 생성
        m = folium.Map(location=user_location, zoom_start=15)
        folium.Marker(user_location, tooltip="입력 위치", icon=folium.Icon(color="blue")).add_to(m)
        
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in nearest.iterrows():
            popup_text = f"""
            <b>{row['건물명']}</b><br>
            개방시간: {row['개방시간']}<br>
            주소: {row['주소']}<br>
            거리: {row['거리(km)']:.2f}km
            """
            folium.Marker(
                location=[row["위도"], row["경도"]],
                popup=popup_text,
                icon=folium.Icon(color="green", icon="info-sign"),
            ).add_to(marker_cluster)

        # 지도 출력
        st_folium(m, width=700, height=500)

        # 표로도 보기
        st.subheader("가까운 화장실 정보")
        st.dataframe(nearest[["건물명", "개방시간", "주소", "거리(km)"]].reset_index(drop=True))
        
    else:
        st.error("주소를 찾을 수 없습니다. 다시 입력해 주세요.")
