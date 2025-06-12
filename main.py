import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

st.title("🚻 서울시 공중화장실 위치 찾기")

# CSV 파일 업로드
uploaded_file = st.file_uploader("📁 이미 업로드한 CSV 파일", type="csv")

# 도로명 주소 입력
address = st.text_input("도로명 주소를 입력하세요", "서울특별시 종로구 세종대로 175")

# 주소 → 위도/경도 변환
def geocode_address(address):
    geolocator = Nominatim(user_agent="toilet_app_korea")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

# 가장 가까운 화장실 5개 찾기
def get_nearest_toilets(user_location, toilet_df, count=5):
    toilet_df["거리(km)"] = toilet_df.apply(
        lambda row: geodesic(user_location, (row["위도"], row["경도"])).km, axis=1
    )
    return toilet_df.sort_values("거리(km)").head(count)

# 실행 조건 확인
if uploaded_file and address:
    # 데이터프레임 불러오기
    df = pd.read_csv(uploaded_file)
    
    # 필요한 컬럼 존재 여부 확인
    required_columns = {"화장실명", "도로명주소", "위도", "경도", "개방시간"}
    if not required_columns.issubset(df.columns):
        st.error(f"CSV 파일에 다음 컬럼이 포함되어야 합니다: {required_columns}")
    else:
        user_location = geocode_address(address)

        if user_location:
            nearest_df = get_nearest_toilets(user_location, df)

            # 지도 생성
            m = folium.Map(location=user_location, zoom_start=16)
            folium.Marker(
                user_location,
                tooltip="입력한 위치",
                icon=folium.Icon(color="red")
            ).add_to(m)

            # 가장 가까운 화장실 5개 지도에 표시
            for _, row in nearest_df.iterrows():
                folium.Marker(
                    location=(row["위도"], row["경도"]),
                    tooltip=row["화장실명"],
                    popup=f"""
                    📍 {row['도로명주소']}<br>
                    ⏰ {row['개방시간']}<br>
                    📏 거리: {row['거리(km)']:.2f} km
                    """,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

            # 지도와 표 출력
            st.subheader("🗺️ 화장실 위치 지도")
            st_folium(m, width=700, height=500)

            st.subheader("📋 가까운 화장실 정보")
            st.dataframe(nearest_df[["화장실명", "도로명주소", "개방시간", "거리(km)"]].reset_index(drop=True))
        else:
            st.error("입력한 주소를 찾을 수 없습니다.")
