import streamlit as st
import pandas as pd
import base64
import io
import matplotlib.pyplot as plt

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
for student, count in st.session_state.counts.items():
    st.write(f"{student}: {count}")

# PNG 이미지 생성 함수
def create_png():
    fig, ax = plt.subplots(figsize=(10, 6))
    students = list(st.session_state.counts.keys())
    counts = list(st.session_state.counts.values())
    ax.bar(students, counts)
    ax.set_ylabel('캐치 횟수')
    ax.set_title('우리반 피구 공 캐치 횟수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# 완료 버튼
if st.button("완료", key="complete_btn"):
    png = create_png()
    st.image(png)
    b64 = base64.b64encode(png.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="피구_공_캐치_횟수.png">결과 다운로드 (PNG)</a>'
    st.markdown(href, unsafe_allow_html=True)
# 결과 표시
st.write("## 현재 캐치 횟수")
for student, count in st.session_state.counts.items():
    st.write(f"{student}: {count}")
