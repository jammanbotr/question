import streamlit as st
import pandas as pd
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(
    page_title="JAMMANBO 문제 던전", 
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 로드
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
    
    * {
        font-family: 'Jua', sans-serif;
    }
    
    .item-modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        animation: fadeIn 0.5s ease-out;
    }

    .item-modal-content {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 0 50px rgba(255,255,255,0.2);
        text-align: center;
        animation: scaleIn 0.5s ease-out;
        max-width: 80%;
    }

    .sparkles {
        font-size: 24px;
        margin: 10px 0;
        animation: sparkle 1s infinite;
    }

    .item-title {
        font-size: 32px;
        color: #FFFFFF;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .item-name {
        font-size: 36px;
        color: #2C3E50;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: glow 1.5s ease-in-out infinite alternate;
        padding: 15px;
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
        margin: 20px 0;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .score {
        font-size: 42px;
        margin: 20px 0;
        animation: bounce 1s ease infinite;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        font-weight: bold;
    }
    
    .score.positive {
        color: #FFD700;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    
    .score.negative {
        color: #FF4444;
        text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
    }

    .total-score {
        font-size: 24px;
        color: white;
        margin-top: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .question-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 25px 0;
        transition: all 0.3s ease;
    }
    
    .question-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .question-text {
        font-size: 20px;
        color: #2C3E50;
        margin-bottom: 20px;
        line-height: 1.5;
        padding: 10px;
        background: rgba(78, 205, 196, 0.1);
        border-radius: 10px;
    }

    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 30px;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .title {
        text-align: center;
        color: #2C3E50;
        font-size: 40px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        animation: title-glow 2s ease-in-out infinite alternate;
        margin: 30px 0;
        padding: 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .stTextInput>div>div>input {
        font-size: 18px;
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        transition: all 0.3s ease;
    }

    .stTextInput>div>div>input:focus {
        border-color: #FF6B6B;
        box-shadow: 0 0 10px rgba(255,107,107,0.2);
    }

    .error-message {
        background: rgba(255, 68, 68, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #FF4444;
        margin: 15px 0;
    }

    .correct-answer {
        color: #2C3E50;
        font-weight: bold;
        margin-top: 10px;
    }

    .scoreboard {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
        animation: fadeIn 1s ease-out;
    }

    .score-row {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    .score-row:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .score-row.highlight {
        background: linear-gradient(45deg, #FF6B6B22, #4ECDC422);
        border: 2px solid #4ECDC4;
    }

    .game-over {
        text-align: center;
        font-size: 32px;
        color: #2C3E50;
        margin: 30px 0;
        padding: 20px;
        background: linear-gradient(45deg, #FF6B6B22, #4ECDC422);
        border-radius: 15px;
        animation: fadeIn 1s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes scaleIn {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }

    @keyframes sparkle {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }

    @keyframes glow {
        from { box-shadow: 0 0 10px rgba(255,255,255,0.8); }
        to { box-shadow: 0 0 20px rgba(255,255,255,1); }
    }

    @keyframes title-glow {
        from { text-shadow: 0 0 5px rgba(44, 62, 80, 0.1); }
        to { text-shadow: 0 0 15px rgba(44, 62, 80, 0.3); }
    }
    </style>
    """, unsafe_allow_html=True)

# 문제와 아이템 정의
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
    if 'total_score' not in st.session_state:
        st.session_state.total_score = 0
    if 'questions_answered' not in st.session_state:
        st.session_state.questions_answered = 0
    if 'game_finished' not in st.session_state:
        st.session_state.game_finished = False
    if 'used_questions' not in st.session_state:
        st.session_state.used_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = get_random_question()
    if 'scores_history' not in st.session_state:
        st.session_state.scores_history = []

def get_random_score_item():
    item, score = random.choice(SCORE_ITEMS)
    return item, score

def get_random_question():
    available_questions = [i for i in range(len(QUESTIONS)) 
                         if i not in st.session_state.used_questions]
    if not available_questions:
        return None
    question_index = random.choice(available_questions)
    st.session_state.used_questions.append(question_index)
    return question_index

def show_item_and_next_question(item, score):
    st.session_state.total_score += score
    st.session_state.questions_answered += 1
    
    st.markdown(f"""
    <div class="item-modal-backdrop">
        <div class="item-modal-content">
            <div class="item-title">✨ 특별한 아이템을 획득했습니다! ✨</div>
            <div class="sparkles">⭐️ 🌟 ⭐️</div>
            <div class="item-name">{item}</div>
            <div class="score {'positive' if score > 0 else 'negative'}">{'+' if score > 0 else ''}{score} 점</div>
            <div class="total-score">총점: {st.session_state.total_score}점</div>
            <div class="sparkles">⭐️ 🌟 ⭐️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if score > 0:
        st.balloons()
    
    time.sleep(2)
    next_question = get_random_question()
    st.session_state.current_question = next_question


def update_and_get_scoreboard(name, score):
    try:
        # 인증 정보 직접 구성
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # universe_domain 제거 (필요없는 키)
        if "universe_domain" in credentials_dict:
            del credentials_dict["universe_domain"]
        
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        gc = gspread.authorize(credentials)
        
        # 스프레드시트 열기
        sheet = gc.open_by_key(st.secrets["spreadsheet_id"]).worksheet('기록')
        
        # 새로운 점수 추가
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([name, score, current_time])
        
        # 전체 데이터 가져오기
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=['이름', '점수', '시간'])
        df['점수'] = pd.to_numeric(df['점수'])
        
        # 점수순으로 정렬
        df = df.sort_values('점수', ascending=False)
        return df.head(10)
        
    except Exception as e:
        print(f"Detailed error: {str(e)}")  # 상세 에러 출력
        st.error(f"점수 기록에 실패했습니다: {str(e)}")
        return pd.DataFrame(columns=['이름', '점수', '시간'])

def show_final_scoreboard(current_name, current_score):
    df = update_and_get_scoreboard(current_name, current_score)
    if len(df) > 0:
        st.markdown("<h2>🏆 명예의 전당 🏆</h2>", unsafe_allow_html=True)
        
        for i, row in df.iterrows():
            is_current = row['이름'] == current_name and int(row['점수']) == current_score
            st.markdown(f"""
            <div class="score-row {'highlight' if is_current else ''}">
                <span class="rank">#{i+1}</span>
                <span class="name">{row['이름']}</span>
                <span class="score">{int(row['점수'])}점</span>
            </div>
            """, unsafe_allow_html=True)

def main():
    load_css()
    init_session_state()

    st.markdown('<h1 class="title">🎮 JAMMANBO 문제 던전에 입장한 잼민이들 환영합니다 🎮</h1>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.name:
        with st.form("name_form"):
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            st.text_input("당신의 이름을 알려주세요!", key="name_input")
            st.markdown('</div>', unsafe_allow_html=True)
            submit = st.form_submit_button("다음")
            if submit and st.session_state.name_input:
                st.session_state.name = st.session_state.name_input
                st.rerun()

    elif not st.session_state.game_finished:
        if st.session_state.current_question is None:
            st.session_state.game_finished = True
            st.balloons()
            st.markdown(
                f'<div class="game-over">🎊 {st.session_state.name}님! 축하합니다!<br>최종 점수는 {st.session_state.total_score}점입니다! 🎊</div>',
                unsafe_allow_html=True
            )
            show_final_scoreboard(st.session_state.name, st.session_state.total_score)
        else:
            current_question, answer = QUESTIONS[st.session_state.current_question]
            
            st.markdown(f'<h3 class="question-title">🎯 문제 {st.session_state.questions_answered + 1}/25</h3>', unsafe_allow_html=True)
            
            with st.form(f"question_form_{st.session_state.questions_answered}"):
                st.markdown('<div class="question-card">', unsafe_allow_html=True)
                st.markdown(f"<div class='question-text'>{current_question}</div>", unsafe_allow_html=True)
                user_answer = st.text_input("", key=f"answer_input_{st.session_state.questions_answered}").strip()
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("제출", use_container_width=True)
                with col2:
                    exit_button = st.form_submit_button("던전에서 퇴장하기", use_container_width=True)
                
                if submit:
                    correct = False
                    try:
                        if '.' in answer:  # 소수점이 있는 경우
                            correct = abs(float(user_answer) - float(answer)) < 0.0001
                        else:  # 문자열인 경우
                            correct = user_answer == answer
                    except:
                        correct = user_answer == answer

                    if correct:
                        item, score = get_random_score_item()
                        show_item_and_next_question(item, score)
                        st.rerun()
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            틀렸습니다! 😢<br>
                            <span class="correct-answer">정답은 '{answer}' 입니다.</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                if exit_button:
                    st.session_state.game_finished = True
                    st.balloons()
                    st.markdown(
                        f'<div class="game-over">🎊 {st.session_state.name}님!<br>최종 점수는 {st.session_state.total_score}점입니다! 🎊</div>',
                        unsafe_allow_html=True
                    )
                    show_final_scoreboard(st.session_state.name, st.session_state.total_score)

            if not st.session_state.game_finished:
                with st.sidebar:
                    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
                    st.markdown(f"### 🏆 현재 점수: {st.session_state.total_score}")
                    st.progress(st.session_state.questions_answered / 25)
                    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.game_finished:
        if st.button("새 게임 시작하기"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
