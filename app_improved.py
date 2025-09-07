"""
AI 모의재판 시스템 - 개선된 버전
50분 수업에 최적화된 구조와 게이미피케이션 적용
"""

import streamlit as st
import os
from openai import OpenAI
import tempfile
from audio_recorder_streamlit import audio_recorder
from datetime import datetime
import json
import time
from utils import (
    init_gamification, add_points, check_badges, get_level,
    create_team_dashboard, create_versus_display, save_session_data,
    load_sample_case, create_quick_feedback, format_time_korean,
    SAMPLE_CASES, generate_ai_hint
)

# 페이지 설정
st.set_page_config(
    page_title="AI 판사 모의재판",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS - 개선된 스타일
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 게이미피케이션 요소 */
    .point-display {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1rem;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .badge-container {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        margin: 0.5rem 0;
    }
    
    .timer-warning {
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* 간소화된 UI */
    .simple-mode {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        height: 30px;
        background: #e0e0e0;
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# 환경변수/시크릿 처리
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("⚠️ OPENAI_API_KEY가 설정되지 않았습니다!")
        st.info("💡 Streamlit Cloud Settings > Secrets에서 설정하세요.")
        st.stop()

# OpenAI 클라이언트
client = OpenAI(api_key=api_key)

# 세션 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.mode = 'simple'  # simple or advanced
    st.session_state.rounds = [
        {'id': 1, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0},
        {'id': 2, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0}
    ]
    st.session_state.case_summary = ''
    st.session_state.ai_judgment = ''
    st.session_state.current_round = 1
    st.session_state.current_phase = 'setup'  # setup, debate, judgment, review
    st.session_state.timer_active = False
    st.session_state.start_time = None
    st.session_state.round_time_limit = 150  # 2.5분
    init_gamification()

# 음성 인식 함수
def transcribe_audio(audio_bytes, language="ko"):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        
        os.unlink(tmp_file_path)
        return transcript.text
    except Exception as e:
        st.error(f"음성 인식 오류: {str(e)}")
        return ""

# AI 판결 생성
def get_ai_judgment(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 교육적이고 공정한 AI 판사입니다. 중학생 수준에 맞춰 친근하고 이해하기 쉽게 설명합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        # 폴백: 간단한 템플릿 판결
        return f"""
        🏆 판결 결과
        
        양 팀 모두 훌륭한 논증을 보여주었습니다.
        
        검사팀: 논리적인 주장과 증거 제시가 좋았습니다.
        변호팀: 상황에 대한 이해와 대안 제시가 인상적이었습니다.
        
        더 발전시킬 점:
        - 구체적인 증거를 더 많이 제시하세요
        - 상대방 주장을 직접 반박하세요
        - 가치어를 더 많이 사용하세요
        
        오류: {str(e)}
        """

# 메인 헤더
st.markdown("<h1 style='text-align: center;'>⚖️ AI 판사 모의재판</h1>", unsafe_allow_html=True)

# 진행 모드 선택
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.radio(
        "진행 모드",
        ["🚀 간편 모드 (추천)", "⚙️ 상세 모드"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.mode = 'simple' if "간편" in mode else 'advanced'

# 현재 점수 표시
create_versus_display()

# 진행 상태 표시
phases = {
    'setup': '📋 준비',
    'debate': '🎤 토론',
    'judgment': '🤖 판결',
    'review': '📊 결과'
}

phase_cols = st.columns(4)
for i, (key, label) in enumerate(phases.items()):
    with phase_cols[i]:
        if st.session_state.current_phase == key:
            st.success(f"**{label}**")
        else:
            st.info(label)

st.markdown("---")

# 간편 모드
if st.session_state.mode == 'simple':
    
    # 현재 단계에 따른 UI
    if st.session_state.current_phase == 'setup':
        st.markdown("## 📋 STEP 1: 사건 준비 (5분)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 샘플 사건 선택
            case_titles = [case["title"] for case in SAMPLE_CASES]
            selected = st.selectbox(
                "오늘의 사건 선택",
                range(len(case_titles)),
                format_func=lambda x: case_titles[x]
            )
            
            if st.button("📥 사건 불러오기", use_container_width=True):
                load_sample_case(selected)
                st.success("✅ 사건을 불러왔습니다!")
            
            # 사건 내용 표시
            if st.session_state.case_summary:
                st.text_area(
                    "사건 개요",
                    st.session_state.case_summary,
                    height=150,
                    disabled=True
                )
        
        with col2:
            st.markdown("### ⏱️ 설정")
            round_count = st.number_input("라운드 수", 1, 4, 2)
            round_time = st.slider("라운드 시간(분)", 1, 5, 2)
            
            st.markdown("### 👥 팀 확인")
            st.write("🔴 검사팀: 3명")
            st.write("🔵 변호팀: 3명")
            
            if st.button("▶️ 토론 시작!", use_container_width=True, type="primary"):
                if st.session_state.case_summary:
                    st.session_state.current_phase = 'debate'
                    st.session_state.start_time = time.time()
                    st.rerun()
                else:
                    st.error("먼저 사건을 선택하세요!")
    
    elif st.session_state.current_phase == 'debate':
        st.markdown("## 🎤 STEP 2: 토론 진행 (25분)")
        
        # 타이머 표시
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            remaining = (25 * 60) - elapsed  # 25분
            if remaining > 0:
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                if remaining < 300:  # 5분 미만
                    st.warning(f"⏰ 남은 시간: {mins:02d}:{secs:02d}")
                else:
                    st.info(f"⏱️ 남은 시간: {mins:02d}:{secs:02d}")
            else:
                st.error("⏰ 시간 종료! AI 판결로 이동하세요.")
        
        # 현재 라운드
        round_num = st.session_state.current_round
        st.markdown(f"### 🔢 라운드 {round_num}")
        
        col1, col2 = st.columns(2)
        
        # 검사팀
        with col1:
            st.markdown("#### ⚔️ 검사팀")
            create_team_dashboard('prosecutor')
            
            # 음성 입력
            audio = audio_recorder(
                text="🎙️ 녹음",
                recording_color="#ff6b6b",
                neutral_color="#667eea",
                icon_size="2x",
                key=f"pros_audio_{round_num}"
            )
            
            if audio:
                with st.spinner("음성 인식 중..."):
                    text = transcribe_audio(audio)
                    if text:
                        st.session_state.rounds[round_num-1]['prosecutor'] = text
                        score = create_quick_feedback(text, 'prosecutor')
                        st.session_state.speech_count['prosecutor'] += 1
                        st.session_state.combo['prosecutor'] += 1
                        badges = check_badges('prosecutor')
                        if badges:
                            st.balloons()
                            for badge in badges:
                                st.success(f"{badge['icon']} {badge['name']} 획득!")
            
            # 텍스트 입력
            prosecutor_text = st.text_area(
                "검사 발언",
                value=st.session_state.rounds[round_num-1]['prosecutor'],
                height=150,
                key=f"pros_text_{round_num}"
            )
            
            if st.button("💾 저장", key=f"save_pros_{round_num}"):
                st.session_state.rounds[round_num-1]['prosecutor'] = prosecutor_text
                if prosecutor_text:
                    create_quick_feedback(prosecutor_text, 'prosecutor')
        
        # 변호팀
        with col2:
            st.markdown("#### 🛡️ 변호팀")
            create_team_dashboard('defender')
            
            # 음성 입력
            audio = audio_recorder(
                text="🎙️ 녹음",
                recording_color="#4ecdc4",
                neutral_color="#667eea",
                icon_size="2x",
                key=f"def_audio_{round_num}"
            )
            
            if audio:
                with st.spinner("음성 인식 중..."):
                    text = transcribe_audio(audio)
                    if text:
                        st.session_state.rounds[round_num-1]['defender'] = text
                        score = create_quick_feedback(text, 'defender')
                        st.session_state.speech_count['defender'] += 1
                        st.session_state.combo['defender'] += 1
                        badges = check_badges('defender')
                        if badges:
                            st.balloons()
                            for badge in badges:
                                st.success(f"{badge['icon']} {badge['name']} 획득!")
            
            # 텍스트 입력
            defender_text = st.text_area(
                "변호 발언",
                value=st.session_state.rounds[round_num-1]['defender'],
                height=150,
                key=f"def_text_{round_num}"
            )
            
            if st.button("💾 저장", key=f"save_def_{round_num}"):
                st.session_state.rounds[round_num-1]['defender'] = defender_text
                if defender_text:
                    create_quick_feedback(defender_text, 'defender')
        
        # 라운드 네비게이션
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if round_num > 1:
                if st.button("◀️ 이전 라운드"):
                    st.session_state.current_round -= 1
                    st.rerun()
        
        with col2:
            st.markdown(f"<center>라운드 {round_num} / {len(st.session_state.rounds)}</center>", unsafe_allow_html=True)
        
        with col3:
            if round_num < len(st.session_state.rounds):
                if st.button("다음 라운드 ▶️"):
                    st.session_state.current_round += 1
                    st.session_state.combo['prosecutor'] = 0
                    st.session_state.combo['defender'] = 0
                    st.rerun()
            else:
                if st.button("🤖 AI 판결 요청", type="primary"):
                    st.session_state.current_phase = 'judgment'
                    st.rerun()
    
    elif st.session_state.current_phase == 'judgment':
        st.markdown("## 🤖 STEP 3: AI 판결 (5분)")
        
        # 판결 생성
        if not st.session_state.ai_judgment:
            with st.spinner("AI 판사가 신중하게 검토 중입니다..."):
                # 프롬프트 생성
                prompt = f"""
                중학생 모의재판을 평가해주세요.
                
                [사건 개요]
                {st.session_state.case_summary}
                
                [토론 내용]
                """
                
                for i, round_data in enumerate(st.session_state.rounds):
                    if round_data['prosecutor'] or round_data['defender']:
                        prompt += f"\n라운드 {i+1}:\n"
                        if round_data['prosecutor']:
                            prompt += f"검사: {round_data['prosecutor']}\n"
                        if round_data['defender']:
                            prompt += f"변호: {round_data['defender']}\n"
                
                prompt += """
                
                다음 형식으로 판결해주세요:
                1. 🏆 승리 팀과 이유 (간단히)
                2. 👍 각 팀의 잘한 점 (2개씩)
                3. 💡 개선할 점 (각 팀 1개씩)
                4. 🌟 베스트 발언자
                5. 📈 점수: 검사팀 ?점, 변호팀 ?점 (100점 만점)
                """
                
                judgment = get_ai_judgment(prompt)
                st.session_state.ai_judgment = judgment
        
        # 판결 표시
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 2rem;
                    border-radius: 20px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);'>
        """, unsafe_allow_html=True)
        
        st.markdown(st.session_state.ai_judgment)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("📊 결과 분석 보기", use_container_width=True):
            st.session_state.current_phase = 'review'
            st.rerun()
    
    elif st.session_state.current_phase == 'review':
        st.markdown("## 📊 STEP 4: 결과 분석 (5분)")
        
        # 최종 점수
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚔️ 검사팀")
            points = st.session_state.points['prosecutor']
            level = get_level(points)
            st.metric("최종 점수", f"{points}점")
            st.info(f"레벨: {level['title']}")
            
            # 뱃지 표시
            badges = st.session_state.badges['prosecutor']
            if badges:
                st.markdown("획득 뱃지:")
                badge_text = " ".join([f"{BADGES[b]['icon']} {BADGES[b]['name']}" for b in badges])
                st.markdown(badge_text)
        
        with col2:
            st.markdown("### 🛡️ 변호팀")
            points = st.session_state.points['defender']
            level = get_level(points)
            st.metric("최종 점수", f"{points}점")
            st.info(f"레벨: {level['title']}")
            
            # 뱃지 표시
            badges = st.session_state.badges['defender']
            if badges:
                st.markdown("획득 뱃지:")
                badge_text = " ".join([f"{BADGES[b]['icon']} {BADGES[b]['name']}" for b in badges])
                st.markdown(badge_text)
        
        # 저장 옵션
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 결과 저장", use_container_width=True):
                data = save_session_data()
                st.download_button(
                    "📥 다운로드",
                    data,
                    f"mock_trial_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    "application/json"
                )
        
        with col2:
            if st.button("🔄 새 재판 시작", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key != 'initialized':
                        del st.session_state[key]
                st.session_state.initialized = False
                st.rerun()

# 사이드바 - 도움말
with st.sidebar:
    st.markdown("## 💡 빠른 도움말")
    
    with st.expander("🚀 간편 모드 사용법"):
        st.markdown("""
        1. **사건 선택** → 샘플 사건 선택
        2. **토론 시작** → 버튼 클릭
        3. **발언 입력** → 음성 또는 텍스트
        4. **AI 판결** → 모든 라운드 완료 후
        5. **결과 확인** → 점수와 피드백
        """)
    
    with st.expander("🎮 포인트 시스템"):
        st.markdown("""
        - 첫 발언: +10점
        - 논리적 반박: +15점
        - 증거 제시: +20점
        - 창의적 주장: +25점
        - 가치어 사용: +5점
        - 콤보 보너스: x1.5
        """)
    
    with st.expander("🏆 레벨 시스템"):
        st.markdown("""
        - Lv.1 🌱 법정 신입생 (0-50점)
        - Lv.2 📚 주니어 변호사 (51-150점)
        - Lv.3 ⚖️ 시니어 변호사 (151-300점)
        - Lv.4 🌟 에이스 변호사 (301-500점)
        - Lv.5 👑 전설의 변호사 (501점+)
        """)
    
    st.markdown("---")
    st.info("💬 문의: 금천중학교 교사")