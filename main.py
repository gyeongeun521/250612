import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

st.title("🚻 서울시 공중화장실 찾기")

uploaded_file = st.file_uploader("서울시 공중화장실 CSV 파일을 업로드하세요", type="csv")

address = st.text_input("도로명 주소를 입력하세요", "서울특별시 종로구 세종대로 175")

# 주소 → 좌표
def geocode_address(address):
    geolocator = Nominatim(user_agent="seoul_toilet_app")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else None

# 거리순 정렬
def find_nearest_toilets(user_location, df, count=5):
    df["거리(km)"] = df.apply(
        lambda row: geodesic(user_location, (row["위도"], row["경도"])).km, axis=1
    )
    return df.sort_values("거리(km)").head(count)

# 실행 조건: 주소 입력 + 파일 업로드
if address and uploaded_file:
    user_location = geocode_address(address)

    if user_location:
        df = pd.read_csv(uploaded_file)
        df = df.dropna(subset=["위도", "경도"])
        nearest = find_nearest_toilets(user_location, df)

        # 지도 생성
        m = folium.Map(location=user_location, zoom_start=16)
        folium.Marker(user_location, tooltip="현재 위치", icon=folium.Icon(color="red")).add_to(m)

        for _, row in nearest.iterrows():
            folium.Marker(
                location=(row["위도"], row["경도"]),
                tooltip=row["화장실명"],
                popup=f"""📍 주소: {row["도로명주소"]}<br>
                ⏰ 개방시간: {row["개방시간"]}<br>
                📏 거리: {row["거리(km)"]:.2f} km""",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        st_folium(m, width=700, height=500)
        st.dataframe(nearest[["화장실명", "도로명주소", "개방시간", "거리(km)"]].reset_index(drop=True))

    else:
        st.error("입력한 주소를 찾을 수 없습니다.")
elif not uploaded_file:
    st.warning("먼저 공중화장실 CSV 파일을 업로드해주세요.")
