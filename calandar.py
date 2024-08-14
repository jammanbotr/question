import streamlit as st
import easyocr
from PIL import Image
from openai import OpenAI
from datetime import datetime, timedelta
import urllib.parse
import numpy as np
import time
import json
import re

# Streamlit Secrets에서 API 키 가져오기
def get_api_key():
    return st.secrets["OPENAI_API_KEY"]

# OpenAI 클라이언트 초기화
def init_openai_client():
    api_key = get_api_key()
    return OpenAI(api_key=api_key)

# 사용할 모델 설정
MODEL_NAME = "gpt-4o-mini"

@st.cache_resource
def load_ocr():
    try:
        with st.spinner('OCR 모델을 로딩 중입니다. 잠시만 기다려주세요...'):
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.1)
            reader = easyocr.Reader(['ko', 'en'], gpu=False)
            progress_bar.empty()
            return reader
    except Exception as e:
        st.error(f"OCR 모델 로딩 중 오류 발생: {str(e)}")
        return None

def extract_text_from_image(image):
    reader = load_ocr()
    if reader is None:
        return None
    try:
        result = reader.readtext(np.array(image))
        text = ' '.join([res[1] for res in result])
        return text
    except Exception as e:
        st.error(f"이미지에서 텍스트 추출 중 오류 발생: {str(e)}")
        return None

def clean_json_string(json_string):
    json_string = re.sub(r'```json\s*|\s*```', '', json_string)
    json_string = json_string.strip()
    json_string = json_string[json_string.find('{'):json_string.rfind('}')+1]
    return json_string

def analyze_text_with_ai(client, text):
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "다음 텍스트에서 이벤트 정보를 추출해주세요. 주제, 일시(여러 개 가능), 위치, 설명을 JSON 형식으로 반환해주세요. 일시는 반드시 'YYYY년 MM월 DD일 HH:MM' 형식으로 제공해주세요. 현재 연도를 기준으로 합니다. 일시가 여러 개인 경우 배열로 반환해주세요. JSON만 반환하고 다른 텍스트는 포함하지 마세요."},
                {"role": "user", "content": text}
            ]
        )
        return clean_json_string(completion.choices[0].message.content.strip())
    except Exception as e:
        st.error(f"AI 분석 중 오류 발생: {str(e)}")
        return None

def create_google_calendar_links(event_info):
    try:
        base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
        event_dict = json.loads(event_info)
        
        text = event_dict.get('주제', '')
        dates = event_dict.get('일시', [])
        location = event_dict.get('위치', '')
        details = event_dict.get('설명', '')

        if isinstance(dates, str):
            dates = [dates]  # 단일 날짜를 리스트로 변환

        calendar_links = []
        
        for date in dates:
            try:
                dt = datetime.strptime(date, "%Y년 %m월 %d일 %H:%M")
            except ValueError:
                dt = datetime.now() + timedelta(days=7)
            
            formatted_time = dt.strftime("%Y%m%dT%H%M%S")
            end_time = (dt + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")

            params = {
                "text": text,
                "dates": f"{formatted_time}/{end_time}",
                "details": details,
                "location": location,
            }
            
            calendar_links.append(f"{base_url}&{urllib.parse.urlencode(params)}")
        
        return calendar_links
    except Exception as e:
        st.error(f"캘린더 링크 생성 중 오류 발생: {str(e)}")
        return None

def main():
    st.title("공문 이미지를 Google 캘린더 이벤트로 변환")

    # API 키 확인
    api_key = get_api_key()
    if not api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. Streamlit Secrets에서 'OPENAI_API_KEY'를 설정해주세요.")
        return

    # OpenAI 클라이언트 초기화
    client = init_openai_client()

    st.info(f"현재 사용 중인 AI 모델: {MODEL_NAME}")

    uploaded_file = st.file_uploader("공문 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='업로드된 이미지', use_column_width=True)

        if st.button("이미지 분석 및 링크 생성"):
            with st.spinner('이미지를 분석 중입니다...'):
                extracted_text = extract_text_from_image(image)
                if extracted_text:
                    st.text("추출된 텍스트:")
                    st.text(extracted_text)
                    analyzed_info = analyze_text_with_ai(client, extracted_text)
                    if analyzed_info:
                        st.subheader("분석 결과")
                        st.json(analyzed_info)

                        calendar_links = create_google_calendar_links(analyzed_info)
                        if calendar_links:
                            st.subheader("Google 캘린더 링크")
                            for i, link in enumerate(calendar_links, 1):
                                st.markdown(f"{i}. [Google 캘린더에 이벤트 {i} 추가]({link})")
                            
                            # 모든 일정 한 번에 추가하는 버튼
                            st.markdown("""
                            <button onclick="addAllEvents()">모든 일정 추가</button>
                            <script>
                            function addAllEvents() {
                                const links = [
                                    %s
                                ];
                                links.forEach((link, index) => {
                                    setTimeout(() => {
                                        window.open(link, '_blank');
                                    }, index * 1000);
                                });
                            }
                            </script>
                            """ % ','.join([f"'{link}'" for link in calendar_links]), unsafe_allow_html=True)
                        else:
                            st.error("캘린더 링크 생성에 실패했습니다.")
                    else:
                        st.error("AI 분석에 실패했습니다.")
                else:
                    st.error("이미지에서 텍스트를 추출하지 못했습니다.")

if __name__ == "__main__":
    main()
