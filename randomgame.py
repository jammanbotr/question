import streamlit as st

# 반드시 다른 st 명령어보다 먼저 실행
st.set_page_config(page_title="JAMMANBO 문제 던전", page_icon="🎮", layout="wide")

import pandas as pd
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import time

# CSS 스타일 정의
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
    
    * {
        font-family: 'Jua', sans-serif;
    }
    
    .item-modal {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0,0,0,0.4);
        animation: pop-up 0.7s ease-out;
        text-align: center;
        margin: 30px 0;
        border: 3px solid #FFD700;
    }
    
    .item-title {
        font-size: 32px;
        color: #FFFFFF;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .item-name {
        font-size: 36px;
        color: #FFD700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        animation: glow 1.5s ease-in-out infinite alternate;
        padding: 15px;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .score {
        font-size: 42px;
        color: #fff;
        margin: 20px 0;
        animation: bounce 1s ease infinite;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
    }
    
    .score.positive {
        color: #FFD700;
    }
    
    .score.negative {
        color: #FF4444;
    }
    
    @keyframes pop-up {
        0% { transform: scale(0); opacity: 0; }
        70% { transform: scale(1.1); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #FFD700; }
        to { text-shadow: 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #FFD700; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    
    .question-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin: 25px 0;
        border: 2px solid #4ECDC4;
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
    
    .stProgress > div > div {
        background: linear-gradient(to right, #FF6B6B, #4ECDC4);
        height: 20px;
        border-radius: 10px;
    }
    
    .title {
        text-align: center;
        color: #2C3E50;
        font-size: 40px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        animation: title-glow 2s ease-in-out infinite alternate;
        margin: 30px 0;
    }
    
    @keyframes title-glow {
        from { text-shadow: 0 0 10px #4ECDC4; }
        to { text-shadow: 0 0 20px #FF6B6B; }
    }
    
    .sidebar-content {
        background: linear-gradient(135deg, #FF6B6B22, #4ECDC422);
        padding: 20px;
        border-radius: 15px;
        margin-top: 30px;
        border: 2px solid rgba(78, 205, 196, 0.3);
    }
    
    .game-over {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 32px;
        animation: fade-in 1.5s ease-out;
        border: 4px solid #FFD700;
        margin: 40px 0;
    }
    
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .question-title {
        font-size: 28px;
        color: #2C3E50;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 문제 세트와 점수 아이템 정의는 이전과 동일

def show_item_modal(item, score):
    score_class = "positive" if score > 0 else "negative"
    modal_html = f"""
    <div class="item-modal">
        <div class="item-title">🎉 특별한 아이템을 획득했습니다! 🎉</div>
        <div class="item-name">{item}</div>
        <div class="score {score_class}">{'+' if score > 0 else ''}{score} 점</div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)
    # 아이템 표시 시간을 3초로 증가
    time.sleep(3)

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
            update_spreadsheet(st.session_state.name, st.session_state.total_score)
            st.balloons()
            st.markdown(
                f'<div class="game-over">🎊 {st.session_state.name}님! 축하합니다!<br>최종 점수는 {st.session_state.total_score}점입니다! 🎊</div>',
                unsafe_allow_html=True
            )
        else:
            current_question, answer = QUESTIONS[st.session_state.current_question]
            
            st.markdown(f'<h3 class="question-title">🎯 문제 {st.session_state.questions_answered + 1}/25</h3>', unsafe_allow_html=True)
            
            with st.form("question_form"):
                st.markdown('<div class="question-card">', unsafe_allow_html=True)
                st.write(current_question)
                user_answer = st.text_input("답을 입력하세요:", key="answer_input").strip()
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("다음", use_container_width=True)
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
                        st.session_state.total_score += score
                        st.session_state.questions_answered += 1
                        
                        # 화려한 효과와 함께 아이템 획득 표시
                        show_item_modal(item, score)
                        if score > 0:
                            st.balloons()
                        
                        # 다음 문제 설정
                        next_question = get_random_question()
                        st.session_state.current_question = next_question
                        st.rerun()
                    else:
                        st.error("틀렸습니다! 다시 도전해보세요! 😢")
                        
                if exit_button:
                    st.session_state.game_finished = True
                    update_spreadsheet(st.session_state.name, st.session_state.total_score)
                    st.balloons()
                    st.markdown(
                        f'<div class="game-over">🎊 {st.session_state.name}님!<br>최종 점수는 {st.session_state.total_score}점입니다! 🎊</div>',
                        unsafe_allow_html=True
                    )

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
    
