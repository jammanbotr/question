import streamlit as st
import pandas as pd
import base64
import altair as alt

# 페이지 설정
st.set_page_config(page_title="우리반 피구 공 캐치 횟수", layout="centered")

# CSS 스타일 정의
st.markdown("""
<style>
    div.row-widget.stButton > button {
        width: 100%;
        height: 80px;
        font-size: 20px;
        font-weight: bold;
        margin: 5px 0px;
        border-radius: 10px;
    }
    div.row-widget.stButton > button:hover {
        background-color: #45a049;
    }
    .student-count {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin-top: -5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 제목
st.title("우리반 피구 공 캐치 횟수")

# 학생 명단
students = ["피카츄", "라이츄", "파이리", "꼬부기", "버터플", "야도란", "피존투", "또가스"]

# 세션 상태 초기화
if 'counts' not in st.session_state:
    st.session_state.counts = {student: 0 for student in students}

# 학생별 버튼 생성
for student in students:
    if st.button(f"{student}", key=f"btn_{student}"):
        st.session_state.counts[student] += 1
    st.markdown(f"<p class='student-count'>{st.session_state.counts[student]}</p>", unsafe_allow_html=True)

# 결과 표시
st.write("## 현재 캐치 횟수")
df = pd.DataFrame(list(st.session_state.counts.items()), columns=['학생', '캐치 횟수'])

# Altair를 사용한 바 차트 (y축을 자연수로 제한)
chart = alt.Chart(df).mark_bar().encode(
    x='학생',
    y=alt.Y('캐치 횟수:Q', scale=alt.Scale(domain=(0, max(df['캐치 횟수']) + 1)), axis=alt.Axis(tickCount=max(df['캐치 횟수']) + 1)),
    color=alt.value('#4CAF50')
).properties(
    width='container',
    height=300
)

st.altair_chart(chart, use_container_width=True)

# CSV 파일 생성 함수
def get_csv():
    return df.to_csv(index=False).encode('utf-8')

# 하단에 완료와 리셋 버튼 배치
col1, col2 = st.columns(2)
with col1:
    if st.button("완료", key="complete_btn"):
        csv = get_csv()
        b64 = base64.b64encode(csv).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="피구_공_캐치_횟수.csv">결과 다운로드 (CSV)</a>'
        st.markdown(href, unsafe_allow_html=True)

with col2:
    if st.button("리셋", key="reset_btn"):
        for student in students:
            st.session_state.counts[student] = 0
        st.experimental_rerun()

# Streamlit 실행을 위한 메인 함수
def main():
    pass

if __name__ == "__main__":
    main()
