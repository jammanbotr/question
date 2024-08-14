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

# ... (이전 코드는 동일)

def create_google_calendar_links(event_info):
    try:
        base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
        event_dict = json.loads(event_info)
        
        text = event_dict.get('주제', '')
        dates = event_dict.get('일시', [])
        location = event_dict.get('위치', '')
        details = event_dict.get('설명', '')
        event_type = event_dict.get('이벤트_유형', '')
        reminder = event_dict.get('알림_설정', '기본 알림')

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

            # 알림 설정
            if reminder == "이벤트 2일 전":
                reminder_param = "&recur=RRULE:FREQ=DAILY;COUNT=1&add=YES&reminders=1440"
            elif reminder == "당일 오전 8시 45분":
                reminder_minutes = int((dt.replace(hour=8, minute=45) - dt).total_seconds() / 60)
                reminder_param = f"&recur=RRULE:FREQ=DAILY;COUNT=1&add=YES&reminders={reminder_minutes}"
            else:
                reminder_param = "&recur=RRULE:FREQ=DAILY;COUNT=1&add=YES&reminders=10"  # 기본 10분 전 알림

            params = {
                "text": text,
                "dates": f"{formatted_time}/{end_time}",
                "details": details,
                "location": location,
            }
            
            calendar_link = f"{base_url}&{urllib.parse.urlencode(params)}{reminder_param}"
            calendar_links.append(calendar_link)
        
        return calendar_links
    except Exception as e:
        st.error(f"캘린더 링크 생성 중 오류 발생: {str(e)}")
        return None

# ... (main 함수 및 나머지 코드는 동일)
