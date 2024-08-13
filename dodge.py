import streamlit as st
import pandas as pd
import base64

# 페이지 설정
st.set_page_config(page_title="우리반 피구 공 캐치 횟수", layout="wide")

# 제목
st.title("우리반 피구 공 캐치 횟수")

# 학생 명단
students = ["피카츄", "라이츄", "파이리", "꼬부기", "버터플", "야도란", "피존투", "또가스"]

# 세션 상태 초기화
if 'counts' not in st.session_state:
    st.session_state.counts = {student: 0 for student in students}

# 2열 레이아웃 생성
col1, col2 = st.columns(2)

# 첫 번째 열에 학생 버튼 배치
with col1:
    for student in students[:4]:
        if st.button(f"{student} 캐치!", key=f"btn_{student}"):
            st.session_state.counts[student] += 1

# 두 번째 열에 나머지 학생 버튼 배치
with col2:
    for student in students[4:]:
        if st.button(f"{student} 캐치!", key=f"btn_{student}"):
            st.session_state.counts[student] += 1

# 결과 표시
st.write("## 현재 캐치 횟수")
df = pd.DataFrame(list(st.session_state.counts.items()), columns=['학생', '캐치 횟수'])
st.dataframe(df)

# 바 차트 표시
st.bar_chart(df.set_index('학생'))

# CSV 파일 생성 함수
def get_csv():
    return df.to_csv(index=False).encode('utf-8')

# 완료 버튼
if st.button("완료", key="complete_btn"):
    csv = get_csv()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="피구_공_캐치_횟수.csv">결과 다운로드 (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)

# 리셋 버튼
if st.button("리셋", key="reset_btn"):
    for student in students:
        st.session_state.counts[student] = 0
    st.experimental_rerun()

# Streamlit 실행을 위한 메인 함수
def main():
    # 여기에 추가적인 Streamlit 설정이나 로직을 넣을 수 있습니다.
    pass

if __name__ == "__main__":
    main()
