import streamlit as st
import pandas as pd
import numpy as np

st.title("Streamlit 요소 예시 페이지")

st.header("1. 텍스트 요소")
st.write("일반 텍스트")
st.markdown("**마크다운** 텍스트")

st.header("2. 위젯")
if st.button("버튼 클릭"):
    st.write("버튼이 클릭되었습니다!")

name = st.text_input("이름 입력")
st.write(f"안녕하세요, {name}!")

age = st.slider("나이", 0, 100, 25)
st.write(f"선택한 나이: {age}")

option = st.selectbox("선택하세요", ["옵션1", "옵션2", "옵션3"])
st.write(f"선택한 옵션: {option}")

st.header("3. 레이아웃")
with st.sidebar:
    st.write("사이드바")

col1, col2 = st.columns(2)
with col1:
    st.write("컬럼 1")
with col2:
    st.write("컬럼 2")

tab1, tab2 = st.tabs(["탭1", "탭2"])
with tab1:
    st.write("탭1 내용")
with tab2:
    st.write("탭2 내용")

st.header("4. 데이터 표시")
df = pd.DataFrame(np.random.randn(10, 3), columns=['A', 'B', 'C'])
st.dataframe(df)
st.line_chart(df)

st.header("5. 미디어")
st.image("https://via.placeholder.com/300", caption="샘플 이미지")

st.header("6. 상태 관리")
if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button("카운트 증가"):
    st.session_state.count += 1

st.write(f"카운트: {st.session_state.count}")
