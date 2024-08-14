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

# (이전 코드는 동일)

def main():
    st.title("공문 이미지를 Google 캘린더 이벤트로 변환")

    if not api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. Streamlit Secrets에서 'OPENAI_API_KEY'를 설정해주세요.")
        return

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
                    analyzed_info = analyze_text_with_ai(extracted_text)
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
