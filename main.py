# app.py

import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.title("🚻 서울시 공중화장실 위치 표시기")

# 사용자 입력
address = st.text_input("도로명 주소를 입력하세요", "서울특별시 중구 세종대로 110")

# 주소를 좌표로 변환
if address:
    geolocator = Nominatim(user_agent="public_toilet_locator")
    location = geolocator.geocode(address)

    if location:
        lat, lon = location.latitude, location.longitude
        st.success(f"위치: {lat:.6f}, {lon:.6f}")

        # 지도 생성
        m = folium.Map(location=[lat, lon], zoom_start=17)
        folium.Marker(
            [lat, lon],
            tooltip="입력한 주소",
            popup=address,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

        # 지도 출력
        st_folium(m, width=700, height=500)

    else:
        st.error("주소를 찾을 수 없습니다. 정확한 도로명 주소를 입력해주세요.")
