import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.distance import geodesic

st.set_page_config(page_title="서울시 공중화장실 지도", layout="wide")

st.title("🚻 서울시 공중화장실 지도")
st.markdown("CSV 파일을 업로드하고, 원하는 **구**와 **개방 여부**를 선택해 지도에서 공중화장실을 확인하세요.")

# CSV 파일 업로드
uploaded_file = st.file_uploader("📤 서울시 공중화장실 CSV 파일 업로드", type="csv")

@st.cache_data
def load_and_clean_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # 컬럼명 표준화
    df.rename(columns={
        '위도': 'Y', '경도': 'X',
        'lat': 'Y', 'latitude': 'Y', 'Latitude': 'Y',
        'lon': 'X', 'longitude': 'X', 'Longitude': 'X'
    }, inplace=True)

    if 'Y' not in df.columns or 'X' not in df.columns:
        st.error("❌ CSV 파일에 '위도(Y)'와 '경도(X)' 컬럼이 있어야 합니다.")
        st.stop()

    return df

if uploaded_file:
    df = load_and_clean_data(uploaded_file)

    # 구 목록 추출
    if '도로명주소' in df.columns:
        df['구'] = df['도로명주소'].str.extract(r'서울특별시\s*(\S+구)')
    else:
        st.error("❌ '도로명주소' 컬럼이 필요합니다.")
        st.stop()

    # 필터 선택
    gu_list = df['구'].dropna().unique().tolist()
    selected_gu = st.selectbox("🏙️ 구 선택", sorted(gu_list))

    open_options = ['전체', '24시간', '시간제 개방']
    open_filter = st.selectbox("🕒 개방 시간 필터", open_options)

    # 필터 적용
    filtered_df = df[df['구'] == selected_gu]

    if open_filter == '24시간':
        filtered_df = filtered_df[filtered_df['개방시간'].str.contains("24|24시간")]
    elif open_filter == '시간제 개방':
        filtered_df = filtered_df[~filtered_df['개방시간'].str.contains("24|24시간")]

    st.subheader(f"🔍 '{selected_gu}' 지역 공중화장실 - {len(filtered_df)}개")

    # 지도 시각화
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
        st.warning("⚠️ 선택한 조건에 해당하는 화장실이 없습니다.")

    # 데이터 테이블 출력
    st.dataframe(filtered_df[['건물명', '도로명주소', '개방시간']].reset_index(drop=True))
else:
    st.info("👆 CSV 파일을 먼저 업로드해주세요.")
