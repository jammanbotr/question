import streamlit as st
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
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        animation: pop-up 0.5s ease-out;
        text-align: center;
        margin: 20px 0;
    }
    
    .item-name {
        font-size: 24px;
        color: #FFD93D;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: glow 1s ease-in-out infinite alternate;
    }
    
    .score {
        font-size: 28px;
        color: #fff;
        margin: 10px 0;
        animation: bounce 0.6s ease infinite;
    }
    
    @keyframes pop-up {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #FFD93D; }
        to { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #FFD93D; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .question-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .stProgress > div > div {
        background: linear-gradient(to right, #FF6B6B, #4ECDC4);
    }
    
    .title {
        text-align: center;
        color: #2C3E50;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: title-glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes title-glow {
        from { text-shadow: 0 0 5px #4ECDC4; }
        to { text-shadow: 0 0 10px #FF6B6B; }
    }
    
    .sidebar-content {
        background: linear-gradient(135deg, #FF6B6B22, #4ECDC422);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .game-over {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        animation: fade-in 1s ease-out;
    }
    
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

# 아이템 획득 모달 함수
def show_item_modal(item, score):
    modal_html = f"""
    <div class="item-modal">
        <h2>🎉 아이템 획득! 🎉</h2>
        <div class="item-name">{item}</div>
        <div class="score">{'+' if score > 0 else ''}{score} 점</div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)

[기존 코드 그대로 유지...]

def main():
    load_css()  # CSS 로드
    st.set_page_config(page_title="JAMMANBO 문제 던전", page_icon="🎮", layout="wide")
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
                        time.sleep(1)  # 효과를 보여주기 위한 짧은 대기
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
