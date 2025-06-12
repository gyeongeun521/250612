import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium
import io

@st.cache_data
def load_data():
    csv_data = """
건물명,개방시간,Y,X,도로명주소
서울광장화장실,06:00~22:00,37.5663,126.9779,서울특별시 중구 세종대로 110
시청역화장실,24시간,37.5656,126.9784,서울특별시 중구 태평로1가
광화문지하쇼핑센터,07:00~22:00,37.5714,126.9769,서울특별시 종로구 세종대로 지하
남대문시장화장실,08:00~21:00,37.5599,126.9773,서울특별시 중구 남대문시장로 10
동대문디자인플라자화장실,09:00~23:00,37.5669,127.0094,서울특별시 중구 을지로 281
"""
    df = pd.read_csv(io.StringIO(csv_data))
    df.columns = df.columns.str.strip()  # 혹시 모를 공백 제거
    return df

df = load_data()

def geocode_address(address):
    geolocator = Nominatim(user_agent="toilet_locator_seoul")
    location = geolocator.geocode(f"{address}, Seoul, South Korea")
    if location:
        return (location.latitude, location.longitude)
    return None

def find_nearest_toilets(user_location, df, n=5):
    df['거리(km)'] = df.apply(
        lambda row: geodesic(user_location, (row['Y'], row['X'])).km,
        axis=1
    )
    return df.sort_values(by='거리(km)').head(n)

st.title("🚻 서울시 공중화장실 찾기")
st.markdown("도로명 주소를 입력하면 가까운 공중화장실 5곳을 지도에 표시합니다.")

m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

address = st.text_input("도로명 주소를 입력하세요:", "서울특별시 종로구 세종대로 175")
location = geocode_address(address)

if location:
    folium.Marker(
        location,
        popup="입력한 위치",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

    nearest = find_nearest_toilets(location, df, 5)

    for _, row in nearest.iterrows():
        folium.Marker(
            [row['Y'], row['X']],
            popup=f"{row['건물명']}<br>개방시간: {row['개방시간']}",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(marker_cluster)

    st.subheader("🔍 가까운 공중화장실 정보")
    st.dataframe(nearest[['건물명', '도로명주소', '개방시간', '거리(km)']].reset_index(drop=True))

st_folium(m, width=700, height=500)
