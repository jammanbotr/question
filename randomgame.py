import streamlit as st
import pandas as pd
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import time

# 문제 세트 정의
QUESTIONS = [
    ["소수의 곱셈 0.5 * 1.25는?", "0.625"],
    ["소수의 곱셈 1.3 * 2.1은?", "2.73"],
    ["파이리가 하루에 생수를 2.3L씩 1주일 마신다면 얼마를 마실까요?(단위는 쓰지마세요)", "16.1"],
    ["고조선의 8조법 중 현재는 (   )개의 법만이 전해지고 있다", "3"],
    ["삼국 중 전성기가 가장 빠른 나라는 어디인가요?", "백제"],
    ["당나라에서는 발해를 일컫어 OOOO이라고 불렀다", "해동성국"],
    ["공주시에서 발견된 벽돌양식의 백제 무덤은?", "무령왕릉"],
    ["양반의 집이나 관공서에서 허드렛일이나 물건을 만드는 일을 했던 조선 시대 신분은?", "천민"],
    ["해의 그림자를 이용해 시간을 잴 수 있었던 조선시대의 발명품은?", "앙부일구"],
    ["삼별초는 몽골과의 항쟁을 위해 강화도->(     ) ->탐라로 근거지를 바꾸었다", "진도"],
    ["신라 말 귀족들의 왕위 다툼으로 정치가 혼란해지자 지방에서는 (      )이 등장했다", "호족"],
    ["후백제를 세운 사람은 누구인가요?", "견훤"],
    ["고조선의 문화범위를 알 수 있는 문화유산 중 (       )식 토기가 있다", "미송리"],
    ["조선은 (          ) 정치 이념을 내세우며 세운 나라이다", "유교"],
    ["몽골의 침입으로 초조대장경이 불타고 다시 힘을 모아 만든 대장경은?", "팔만대장경"],
    ["고려 청자에 들어간 기법은 (     )기법이다", "상감"],
    ["세계 최고의 목판활자인쇄본은?", "무구정광대다라니경"],
    ["거란의 1차 침입에 거란군의 침입을 외교로 막아낸 사람은 누구인가요?", "서희"],
    ["거란의 1차 침입 후에 거란이 고려에 준 지역은 OO6주이다", "강동"],
    ["이성계가 이끄는 요동정벌군이 어느 섬에서 되돌아와 새로운 나라를 세웠는데 이 사건을 OOOOO이라 한다", "위화도회군"],
    ["한 변의 길이가 0.8인 정사각형의 넓이는?", "0.64"],
    ["밑변의 길이가 2.3이고 높이가 1.2인 삼각형의 넓이는?", "1.38"],
    ["후금이 조선과 형제과 관계를 맺고자 침입한 사건은?", "정묘호란"],
    ["병자호란 당시 인조가 피신한 곳은?", "남한산성"],
    ["진주성에서 일본군을 상대로 승리한 장군은?", "김시민"]
]

# 점수 아이템 정의
SCORE_ITEMS = [
    ("나희의 까불이 춤", 800),
    ("신영이의 화염 스카프", 700),
    ("지영이의 콜라맛 츄파츕스", 500),
    ("성율이의 침묵게임", 900),
    ("채훈이의 도마뱀 끈끈이", 7500),
    ("지홍이의 필요없어진 목발", 300),
    ("근호의 로봇청소기", 2500),
    ("나준이의 사춘기 징징", 150),
    ("도연이의 만점 수학시험지", 10000),
    ("서영이의 영혼이 깃든 축구공", 3500),
    ("주하의 옥구슬 목소리", 2000),
    ("지아의 불꽃 티볼 송구", 1700),
    ("채민이의 회복된 새끼손가락", 3300),
    ("준혁이의 분위기 끌어올려 외침", 5000),
    ("하준이의 베놈 슬라임", 1200),
    ("시윤이의 빨간 샤프", 1100),
    ("하린이의 이탈리아행 티켓", 4000),
    ("다혜의 일본행 티켓", 2200),
    ("아인이의 고장난 크롬북펜", 500),
    ("지완이의 로봇 동아리 끌차", 600),
    ("서호의 징징이", -700),
    ("연서의 청아한 플룻소리", 1900),
    ("신우의 무지개색 하키퍽", 2700)
]

def init_session_state():
    if 'name' not in st.session_state:
        st.session_state.name = ''
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'total_score' not in st.session_state:
        st.session_state.total_score = 0
    if 'questions_answered' not in st.session_state:
        st.session_state.questions_answered = 0
    if 'game_finished' not in st.session_state:
        st.session_state.game_finished = False
    if 'used_questions' not in st.session_state:
        st.session_state.used_questions = set()

def get_random_score_item():
    item, score = random.choice(SCORE_ITEMS)
    return item, score

def get_random_question():
    available_questions = [i for i in range(len(QUESTIONS)) if i not in st.session_state.used_questions]
    if not available_questions:
        st.session_state.used_questions.clear()
        available_questions = list(range(len(QUESTIONS)))
    
    question_index = random.choice(available_questions)
    st.session_state.used_questions.add(question_index)
    return question_index

def update_spreadsheet(name, score):
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        spreadsheet_id = '1TYZ4ZXkwcL5_-ITxYyC081ruKS7vRJr2X7j1D4P-lnE'
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(spreadsheet_id).worksheet('기록')
        
        # 새로운 기록 추가
        sheet.append_row(['', name, score])
        
        # 점수순으로 정렬
        records = sheet.get_all_values()[1:]  # 헤더 제외
        records.sort(key=lambda x: float(x[2]), reverse=True)
        
        # 순위 업데이트
        for i, record in enumerate(records, 1):
            record[0] = i
        
        # 시트 업데이트
        sheet.clear()
        sheet.append_row(['순위', '이름', '기록'])  # 헤더 다시 추가
        sheet.append_rows(records)
        
    except Exception as e:
        st.error(f"기록 저장 중 오류가 발생했습니다: {str(e)}")

def main():
    st.set_page_config(page_title="JAMMANBO 문제 던전", page_icon="🎮", layout="wide")
    init_session_state()

    st.title("🎮 JAMMANBO 문제 던전에 입장한 잼민이들 환영합니다 🎮")
    st.markdown("---")

    if not st.session_state.name:
        with st.form("name_form"):
            st.text_input("당신의 이름을 알려주세요!", key="name_input")
            submit = st.form_submit_button("다음")
            if submit and st.session_state.name_input:
                st.session_state.name = st.session_state.name_input
                st.rerun()

    elif not st.session_state.game_finished:
        st.session_state.current_question = get_random_question()
        current_question, answer = QUESTIONS[st.session_state.current_question]
        
        st.markdown(f"### 🎯 문제 {st.session_state.questions_answered + 1}/25")
        
        with st.form("question_form"):
            st.write(current_question)
            user_answer = st.text_input("답을 입력하세요:", key="answer_input")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("다음", use_container_width=True)
            with col2:
                exit_button = st.form_submit_button("던전에서 퇴장하기", use_container_width=True)
            
            if submit:
                if user_answer == answer:
                    item, score = get_random_score_item()
                    st.session_state.total_score += score
                    if score > 0:
                        st.success(f"정답입니다! 🎉 {item}을(를) 획득했습니다! (+{score}점)")
                    else:
                        st.warning(f"정답입니다! 😱 하지만 {item}을(를) 획득했습니다... ({score}점)")
                    
                    st.session_state.questions_answered += 1
                    
                    if st.session_state.questions_answered >= 25:
                        st.session_state.game_finished = True
                        update_spreadsheet(st.session_state.name, st.session_state.total_score)
                        st.balloons()
                        st.success(f"🎊 {st.session_state.name}님! 축하합니다! 최종 점수는 {st.session_state.total_score}점입니다! 🎊")
                else:
                    st.error("틀렸습니다! 다시 도전해보세요! 😢")
                    
            if exit_button:
                st.session_state.game_finished = True
                update_spreadsheet(st.session_state.name, st.session_state.total_score)
                st.balloons()
                st.success(f"🎊 {st.session_state.name}님! 최종 점수는 {st.session_state.total_score}점입니다! 🎊")

        if not st.session_state.game_finished:
            st.sidebar.markdown(f"### 🏆 현재 점수: {st.session_state.total_score}")
            st.sidebar.progress(st.session_state.questions_answered / 25)

    if st.session_state.game_finished:
        if st.button("새 게임 시작하기"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
