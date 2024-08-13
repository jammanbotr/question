import streamlit as st
import requests

def generate_questions(subject, standard, content):
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("API 키가 설정되지 않았습니다. 관리자에게 문의하세요.")
        return []

    API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    
    prompt = f"""
    과목: {subject}
    성취기준: {standard}
    학습내용: {content}

    위 정보를 바탕으로 5-6학년 초등학생들이 이해하기 쉬운 탐구질문 3개를 만들어주세요. 
    질문은 간단하고 명확해야 하며, 학생들의 호기심을 자극할 수 있어야 합니다.
    각 질문 앞에 번호를 붙이지 말고, 질문만 작성해주세요.
    """

    try:
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            }
        )
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = response.json()
        questions = data['candidates'][0]['content']['parts'][0]['text'].split('\n')
        return [q.strip() for q in questions if q.strip()]
    except requests.RequestException as e:
        st.error(f"API 요청 중 오류 발생: {e}")
    except KeyError as e:
        st.error(f"응답 데이터 처리 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"예상치 못한 오류 발생: {e}")
    
    return ["질문 생성 중 오류가 발생했습니다. 다시 시도해주세요."]

# Streamlit 앱 코드
st.title('초등학교 수업 탐구질문 생성기')

subjects = ['바른생활', '슬기로운 생활', '즐거운 생활', '국어', '사회', '도덕', '수학', '과학', '실과', '체육', '음악', '미술', '영어']
subject = st.selectbox('과목 선택:', subjects)

standard = st.text_input('성취기준 입력:')
content = st.text_area('학습 내용 입력:')

if st.button('탐구질문 생성하기'):
    if subject and standard and content:
        questions = generate_questions(subject, standard, content)
        if questions:
            st.subheader('생성된 탐구질문:')
            for i, q in enumerate(questions, 1):
                st.write(f"{i}. {q}")
    else:
        st.warning('모든 필드를 입력해주세요.')