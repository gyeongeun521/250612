import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title="서울시 공중화장실 지도", layout="wide")

st.title("🚻 서울시 공중화장실 찾기")
st.markdown("업로드된 데이터에서 **구를 선택**하면 해당 지역의 모든 공중화장실이 지도에 표시됩니다.")

# 이미 업로드된 CSV를 불러옴
@st.cache_data
def load_data():
    df = pd.read_csv("your_uploaded_file.csv")  # 🔁 파일 이름 수정 필요
    df.columns = df.columns.str.strip()

    # 위도/경도 컬럼명 표준화
    df.rename(columns={
        '위도': 'Y', '경도': 'X',
        'lat': 'Y', 'latitude': 'Y',
        'lon': 'X', 'longitude': 'X'
    }, inplace=True)

    # 도로명주소로 구 추출
    if '도로명주소' in df.columns:
        df['구'] = df['도로명주소'].str.extract(r'서울특별시\s*(\S+구)')
    else:
        st.error("❌ '도로명주소' 컬럼이 필요합니다.")
        st.stop()

    return df

df = load_data()

# 구 선택
gu_list = df['구'].dropna().unique().tolist()
selected_gu = st.selectbox("🏙️ 구 선택", sorted(gu_list))

# 개방 시간 필터
open_filter = st.selectbox("🕒 개방 시간 필터", ['전체', '24시간', '시간제 개방'])

filtered_df = df[df['구'] == selected_gu]

# 개방시간 필터 적용
if open_filter == '24시간':
    filtered_df = filtered_df[filtered_df['개방시간'].str.contains("24|24시간")]
elif open_filter == '시간제 개방':
    filtered_df = filtered_df[~filtered_df['개방시간'].str.contains("24|24시간")]

st.subheader(f"🔍 '{selected_gu}' 지역 화장실 {len(filtered_df)}개")

# 지도 그리기
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
else:
    st.warning("⚠️ 해당 조건에 맞는 화장실이 없습니다.")

# 표 출력
st.dataframe(filtered_df[['건물명', '도로명주소', '개방시간']].reset_index(drop=True))
