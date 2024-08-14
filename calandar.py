import streamlit as st
import pytesseract
from PIL import Image
import io
import os
import openai
from datetime import datetime
import urllib.parse
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")

# API 키가 없으면 오류 발생
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your environment or .env file.")

# API 키 설정
openai.api_key = api_key

# ... (나머지 함수들은 이전과 동일)

def main():
    st.title("공문 이미지를 Google 캘린더 이벤트로 변환")

    # API 키 확인
    if not openai.api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. 관리자에게 문의하세요.")
        return

    # ... (나머지 코드는 이전과 동일)

if __name__ == "__main__":
    main()