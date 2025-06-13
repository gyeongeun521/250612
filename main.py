import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.distance import geodesic
from streamlit_folium import st_folium

# 서울시 구별 중심 좌표 (일부 예시, 필요시 더 추가 가능)
gu_centers = {
    "종로구": (37.5731, 126.9795),
    "중구": (37.5636, 126.9978),
    "용산구": (37.5324, 126.9902),
    "성동구": (37.5634, 127.0364),
    "광진구": (37.5385, 127.0823),
    "동대문구": (37.5744, 127.0402),
    "중랑구": (37.6064, 127.0927),
    "성북구": (37.5894, 127.0167),
    "강북구": (37.6396, 127.0256),
    "도봉구": (37.6688, 127.0470),
    "노원구": (37.6542, 127.0568),
    "은평구": (37.6176, 126.9227),
    "서대문구": (37.5791, 126.9368),
    "마포구": (37.5663, 126.9014),
    "양천구": (37.5169, 126.8664),
    "강서구": (37.5509, 126.8495),
    "구로구": (37.4955, 126.8878),
    "금천구": (37.4604, 126.9004),
    "영등포구": (37.5264, 126.8963),
    "동작구": (37.5124, 126.9393),
    "관악구": (37.4781, 126.9516),
    "서초구": (37.4836, 127.0326),
    "강남구": (37.5172, 127.0473),
    "송파구": (37.5146, 127.1060),
    "강동구": (37.5301, 127.1238),
}

@st.cache_data
def load_data():
    return pd.read_csv("seoul_toilets.csv")  # 업로드한 전체 파일 사용

df = load_data()
df.columns = df.columns.str.strip()  # 혹시 모를 공백 제거

st.title("🚻 서울시 공중화장실 찾기")
gu_selected = st.selectbox("서울시 구 선택", list(gu_centers.keys()))
user_location = gu_centers[gu_selected]

def find_nearest_toilets(user_location, df, n=5):
    df['거리(km)'] = df.apply(
        lambda row: geodesic(user_location, (row['Y'], row['X'])).km,
        axis=1
    )
    return df.sort_values(by='거리(km)').head(n)

nearest = find_nearest_toilets(user_location, df, 5)

# 지도 표시
m = folium.Map(location=user_location, zoom_start=14)
folium.Marker(user_location, tooltip=f"{gu_selected} 중심", icon=folium.Icon(color="blue")).add_to(m)
marker_cluster = MarkerCluster().add_to(m)

for _, row in nearest.iterrows():
    folium.Marker(
        [row['Y'], row['X']],
        popup=f"{row['건물명']}<br>개방시간: {row['개방시간']}",
        icon=folium.Icon(color="green")
    ).add_to(marker_cluster)

st.subheader("📋 가까운 공중화장실 정보")
st.dataframe(nearest[['건물명', '도로명주소', '개방시간', '거리(km)']].reset_index(drop=True))

st_folium(m, width=700, height=500)
