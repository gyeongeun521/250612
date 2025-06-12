import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

st.title("🚻 서울시 공중화장실 찾기 (Folium 지도)")

uploaded_file = st.file_uploader("서울시 공중화장실 CSV 업로드", type="csv")

address = st.text_input("도로명 주소를 입력하세요", "서울특별시 종로구 세종대로 175")

# 주소를 위도/경도로 변환
def geocode_address(addr):
    geolocator = Nominatim(user_agent="seoul_toilet_app")
    location = geolocator.geocode(addr)
    return (location.latitude, location.longitude) if location else None

# 가장 가까운 N개 화장실 반환
def get_nearest(df, user_loc, n=5):
    df["거리(km)"] = df.apply(lambda row: geodesic(user_loc, (row["위도"], row["경도"])).km, axis=1)
    return df.sort_values("거리(km)").head(n)

# 본격 실행
if uploaded_file and address:
    df = pd.read_csv(uploaded_file)

    # 필수 컬럼 확인
    required_columns = {"화장실명", "건물명", "도로명주소", "위도", "경도", "개방시간"}
    if not required_columns.issubset(df.columns):
        st.error(f"CSV에 다음 컬럼이 있어야 해요: {required_columns}")
    else:
        user_loc = geocode_address(address)

        if user_loc:
            nearest = get_nearest(df, user_loc)

            # 지도 만들기
            m = folium.Map(location=user_loc, zoom_start=16)
            folium.Marker(user_loc, tooltip="입력한 위치", icon=folium.Icon(color="red")).add_to(m)

            for _, row in nearest.iterrows():
                folium.Marker(
                    location=(row["위도"], row["경도"]),
                    tooltip=row["화장실명"],
                    popup=folium.Popup(f"""
                    🚻 <b>{row['화장실명']}</b><br>
                    🏢 건물명: {row['건물명']}<br>
                    📍 주소: {row['도로명주소']}<br>
                    ⏰ 개방시간: {row['개방시간']}<br>
                    📏 거리: {row['거리(km)']:.2f} km
                    """, max_width=300),
                    icon=folium.Icon(color="blue")
                ).add_to(m)

            # 지도 출력
            st.subheader("🗺️ 지도에서 가까운 공중화장실 보기")
            st_folium(m, width=700, height=500)

            # 표 출력
            st.subheader("📋 가까운 공중화장실 5곳 정보")
            st.dataframe(
                nearest[["화장실명", "건물명", "도로명주소", "개방시간", "거리(km)"]].reset_index(drop=True)
            )
        else:
            st.error("❌ 입력한 주소를 찾을 수 없습니다. 좀 더 구체적으로 입력해보세요.")
else:
    st.info("CSV 파일을 업로드하고 도로명 주소를 입력하면 결과가 표시됩니다.")
