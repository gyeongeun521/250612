import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# 데이터 불러오기
@st.cache_data
def load_data():
    # CSV에는 '건물명', '개방시간', '위도', '경도', '도로명주소'가 포함되어 있어야 합니다.
    return pd.read_csv("seoul_toilets.csv")

df = load_data()

# 주소 → 좌표 변환
def geocode_address(address):
    geolocator = Nominatim(user_agent="toilet_locator_seoul")
    location = geolocator.geocode(f"{address}, Seoul, South Korea")
    if location:
        return (location.latitude, location.longitude)
    return None

# 가장 가까운 화장실 5곳 찾기
def find_nearest_toilets(user_location, df, n=5):
    df['거리(km)'] = df.apply(
        lambda row: geodesic(user_location, (row['위도'], row['경도'])).km,
        axis=1
    )
    return df.sort_values(by='거리(km)').head(n)

# Streamlit UI
st.title("🚻 서울시 공중화장실 찾기")
st.markdown("도로명 주소를 입력하면 가까운 공중화장실 5곳을 지도에 표시합니다.")

# 지도 초기화 (서울 중심)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# 주소 입력
address = st.text_input("도로명 주소를 입력하세요:", "서울특별시 종로구 세종대로 175")

# 주소를 위도/경도로 변환
location = geocode_address(address)

if location:
    # 입력 위치 마커
    folium.Marker(
        location,
        popup="입력한 위치",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

    # 가까운 화장실 5곳 찾기
    nearest = find_nearest_toilets(location, df, 5)

    # 마커 표시
    for _, row in nearest.iterrows():
        folium.Marker(
            [row['위도'], row['경도']],
            popup=f"{row['건물명']}<br>개방시간: {row['개방시간']}",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(marker_cluster)

    # 결과 표 출력
    st.subheader("🔍 가까운 공중화장실 정보")
    st.dataframe(nearest[['건물명', '도로명주소', '개방시간', '거리(km)']].reset_index(drop=True))

# 지도 출력
st_data = st_folium(m, width=700, height=500)
