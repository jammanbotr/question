import streamlit as st
import requests

def generate_questions(subject, standard, content):
    API_KEY = 'AIzaSyBBZkZE3-CLz0DpeIDGgRTJiPSHFNVfZB4'  # 실제 API 키로 교체하세요
    API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

    prompt = f"과목: {subject}\n성취기준: {standard}\n학습내용: {content}\n\n위 정보를 바탕으로 초등학교 학생들의 탐구를 위한 질문 3개를 생성해주세요. 질문은 초등학교 학생들의 개념기반학습을 자극해서 일반화 및 원리의 상위지식으로 전이가 가능하면 좋습니다."

    try:
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            }
        )
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text'].split('\n')
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return ["질문 생성 중 오류가 발생했습니다. 다시 시도해주세요."]

st.title('초등학교 수업 탐구질문 생성기')

subjects = ['바른생활', '슬기로운 생활', '즐거운 생활', '국어', '사회', '도덕', '수학', '과학', '실과', '체육', '음악', '미술', '영어']
subject = st.selectbox('과목 선택:', subjects)

standard = st.text_input('성취기준 입력:')
content = st.text_area('학습 내용 입력:')

if st.button('탐구질문 생성하기'):
    if subject and standard and content:
        questions = generate_questions(subject, standard, content)
        st.subheader('생성된 탐구질문:')
        for i, q in enumerate(questions, 1):
            st.write(f"{i}. {q}")
    else:
        st.warning('모든 필드를 입력해주세요.')
