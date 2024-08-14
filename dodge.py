import streamlit as st
import pandas as pd
import base64
import altair as alt

# 페이지 설정
st.set_page_config(page_title="우리반 피구 공 캐치 횟수", layout="wide")

# CSS 스타일 정의
st.markdown("""
<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 10px;
    }
    .grid-item {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 0;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        cursor: pointer;
        border-radius: 10px;
    }
    .grid-item:hover {
        background-color: #45a049;
    }
    .count {
        font-size: 14px;
        font-weight: bold;
        margin-top: 5px;
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

# 커스텀 HTML을 사용한 그리드 레이아웃
html_content = '<div class="grid-container">'
for student in students:
    html_content += f'''
    <div class="grid-item" onclick="handleClick('{student}')">
        {student}
        <div class="count" id="count-{student}">{st.session_state.counts[student]}</div>
    </div>
    '''
html_content += '</div>'

# JavaScript 함수 추가
st.markdown("""
<script>
function handleClick(student) {
    fetch(`http://localhost:8501/update_count?student=${student}`, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            document.getElementById(`count-${student}`).innerText = data.count;
        });
}
</script>
""", unsafe_allow_html=True)

# HTML 콘텐츠 렌더링
st.markdown(html_content, unsafe_allow_html=True)

# Streamlit 서버 엔드포인트 (카운트 업데이트용)
def update_count():
    student = st.experimental_get_query_params()['student'][0]
    st.session_state.counts[student] += 1
    return {"count": st.session_state.counts[student]}

# 결과 표시
st.write("## 현재 캐치 횟수")
df = pd.DataFrame(list(st.session_state.counts.items()), columns=['학생', '캐치 횟수'])

# Altair를 사용한 바 차트 (y축을 자연수로 제한)
chart = alt.Chart(df).mark_bar().encode(
    x='학생',
    y=alt.Y('캐치 횟수:Q', scale=alt.Scale(domain=(0, max(df['캐치 횟수']) + 1)), axis=alt.Axis(tickCount=max(df['캐치 횟수']) + 1)),
    color=alt.value('#4CAF50')
).properties(
    width=600,
    height=400
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
    st.experimental_set_query_params()

if __name__ == "__main__":
    main()
