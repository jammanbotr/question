import streamlit as st
import easyocr
from PIL import Image
import openai
from datetime import datetime
import urllib.parse
import numpy as np
import time
import json

# Streamlit Secrets에서 API 키 가져오기
api_key = st.secrets["OPENAI_API_KEY"]

# OpenAI API 키 설정
openai.api_key = api_key

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

def analyze_text_with_ai(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "다음 텍스트에서 이벤트 정보를 추출해주세요. 주제, 일시, 위치, 설명을 JSON 형식으로 반환해주세요."},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        st.error(f"AI 분석 중 오류 발생: {str(e)}")
        return None

def create_google_calendar_link(event_info):
    try:
        base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
        
        event_dict = json.loads(event_info)
        
        text = event_dict.get('주제', '')
        start_time = event_dict.get('일시', '')
        location = event_dict.get('위치', '')
        details = event_dict.get('설명', '')
        
        try:
            dt = datetime.strptime(start_time, "%Y년 %m월 %d일 %H:%M")
            formatted_time = dt.strftime("%Y%m%dT%H%M%S")
        except:
            formatted_time = ""

        # 프롬프트 분석 결과에서 알람 시간이 2일 전이라고 가정
        reminder_days_before = 2
        reminder_minutes_before_event = reminder_days_before * 24 * 60

        params = {
            "text": text,
            "dates": f"{formatted_time}/{formatted_time}",
            "details": details,
            "location": location,
            "trp": "true",  # 반복 설정이 있을 경우
            "reminder": f"{reminder_minutes_before_event}",  # 알람을 2일 전으로 설정
        }

        return f"{base_url}&{urllib.parse.urlencode(params)}"
    except Exception as e:
        st.error(f"캘린더 링크 생성 중 오류 발생: {str(e)}")
        return None

def main():
    st.title("공문 이미지를 Google 캘린더 이벤트로 변환")

    if not api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. Streamlit Secrets에서 'OPENAI_API_KEY'를 설정해주세요.")
        return

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
                    analyzed_info = analyze_text_with_ai(extracted_text)
                    if analyzed_info:
                        st.subheader("분석 결과")
                        st.json(analyzed_info)

                        calendar_link = create_google_calendar_link(analyzed_info)
                        if calendar_link:
                            st.subheader("Google 캘린더 링크")
                            st.markdown(f"[Google 캘린더에 이벤트 추가]({calendar_link})")
                        else:
                            st.error("캘린더 링크 생성에 실패했습니다.")
                    else:
                        st.error("AI 분석에 실패했습니다.")
                else:
                    st.error("이미지에서 텍스트를 추출하지 못했습니다.")

if __name__ == "__main__":
    main()
