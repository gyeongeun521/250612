import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# --- 1. 서울시 공중화장실 데이터 불러오기 (CSV 예시) ---
@st.cache_data
def load_toilet_data():
    df = pd.read_csv("seoul_toilets.csv")  # 위도, 경도, 도로명주소, 개방시간 필수 포함
    return df.dropna(subset=["위도", "경도"])

# --- 2. 주소를 위도/경도로 변환 ---
def geocode_address(address):
    geolocator = Nominatim(user_agent="seoul_toilet_app")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else None

# --- 3. 거리 계산 및 근처 화장실 추출 ---
def find_nearest_toilets(user_location, toilet_df, count=5):
    toilet_df["거리(km)"] = toilet_df.apply(
        lambda row: geodesic(user_location, (row["위도"], row["경도"])).km, axis=1
    )
    return toilet_df.sort_values("거리(km)").head(count)

# --- Streamlit UI ---
st.title("🚻 서울시 공중화장실 찾기")
address = st.text_input("도로명 주소를 입력하세요", "서울특별시 종로구 세종대로 175")

if address:
    user_location = geocode_address(address)

    if user_location:
        st.success(f"입력한 주소의 위치: {user_location}")
        toilet_df = load_toilet_data()
        nearby_toilets = find_nearest_toilets(user_location, toilet_df)

        # 지도 생성
        m = folium.Map(location=user_location, zoom_start=16)
        folium.Marker(
            location=user_location,
            tooltip="현재 위치",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(m)

        # 주변 화장실 표시
        for _, row in nearby_toilets.iterrows():
            folium.Marker(
                location=(row["위도"], row["경도"]),
                tooltip=row["화장실명"],
                popup=f"""
                📍 주소: {row["도로명주소"]}<br>
                ⏰ 개방시간: {row["개방시간"]}<br>
                📏 거리: {row["거리(km)"]:.2f} km
                """,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        st_folium(m, width=700, height=500)

        st.subheader("📋 가까운 화장실 정보 (TOP 5)")
        st.dataframe(nearby_toilets[["화장실명", "도로명주소", "개방시간", "거리(km)"]].reset_index(drop=True))

    else:
        st.error("주소를 찾을 수 없습니다. 다시 확인해주세요.")
