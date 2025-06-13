import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.title("🚻 서울시 공중화장실 찾기")

@st.cache_data
def load_data():
    df = pd.read_csv("서울시 공중화장실 위치정보.csv")
    df.columns = df.columns.str.strip()
    df.rename(columns={'위도':'Y', '경도':'X'}, inplace=True)
    df['구'] = df['도로명주소'].str.extract(r'서울특별시\s*(\S+구)')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ '서울시 공중화장실 위치정보.csv' 파일이 없습니다. 앱과 같은 폴더에 파일을 업로드해주세요.")
    st.stop()

gu_list = df['구'].dropna().unique()
selected_gu = st.selectbox("🏙️ 구 선택", sorted(gu_list))

open_filter = st.selectbox("🕒 개방 시간 필터", ['전체', '24시간', '시간제 개방'])

filtered_df = df[df['구'] == selected_gu]

if open_filter == '24시간':
    filtered_df = filtered_df[filtered_df['개방시간'].str.contains("24|24시간")]
elif open_filter == '시간제 개방':
    filtered_df = filtered_df[~filtered_df['개방시간'].str.contains("24|24시간")]

st.subheader(f"🔍 '{selected_gu}' 지역 화장실 {len(filtered_df)}개")

if not filtered_df.empty:
    center = [filtered_df['Y'].mean(), filtered_df['X'].mean()]
    m = folium.Map(location=center, zoom_start=14)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in filtered_df.iterrows():
        folium.Marker(
            [row['Y'], row['X']],
            popup=f"{row['건물명']}<br>개방시간: {row['개방시간']}",
            tooltip=row['건물명'],
            icon=folium.Icon(color="green")
        ).add_to(marker_cluster)

    st_folium(m, width=700, height=500)
    st.dataframe(filtered_df[['건물명', '도로명주소', '개방시간']].reset_index(drop=True))
else:
    st.warning("⚠️ 조건에 맞는 화장실이 없습니다.")
