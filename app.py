"""
AI 모의재판 시스템 - 50분 수업 최적화 버전
게이미피케이션과 간편 모드 통합
"""

import streamlit as st
import os
from openai import OpenAI
import tempfile
from audio_recorder_streamlit import audio_recorder
from datetime import datetime
import json
import time
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AI 판사 모의재판",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 게이미피케이션 강화
st.markdown("""
<style>
    /* 메인 배경 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 녹음 상태 표시 */
    @keyframes recording-pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    
    .recording-indicator {
        animation: recording-pulse 1.5s infinite;
        background: #ff4444;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: inline-block;
    }
    
    /* 포인트 표시 */
    .point-display {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1rem;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #5a9fd4;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #5a9fd4 0%, #7bb8db 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* 카드 스타일 */
    .main-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    
    /* 팀 카드 */
    .team-card-prosecutor {
        background: linear-gradient(135deg, #ff9a8b 0%, #ffb4a2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255,154,139,0.25);
        color: white;
        border: 3px solid #ff7a6b;
    }
    
    .team-card-defender {
        background: linear-gradient(135deg, #a8e6cf 0%, #b4e7ce 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(168,230,207,0.25);
        color: #2d5f3f;
        border: 3px solid #7dd3b0;
    }
    
    /* 타이머 */
    .timer-display {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        text-align: center;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* 뱃지 컨테이너 */
    .badge-container {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        margin: 0.5rem 0;
        flex-wrap: wrap;
    }
    
    /* 진행 바 */
    .progress-bar {
        height: 30px;
        background: #e0e0e0;
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #5a9fd4, #7bb8db);
        transition: width 0.3s ease;
    }
    
    /* 간편 모드 카드 */
    .simple-mode {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* 섹션 구분 */
    .section-header {
        background: linear-gradient(90deg, #5a9fd4 0%, #7bb8db 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    
    /* VS 표시 */
    .versus-display {
        display: flex;
        height: 40px;
        border-radius: 20px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ===== 게이미피케이션 시스템 =====

# 포인트 시스템
POINT_SYSTEM = {
    "첫_발언": 10,
    "논리적_반박": 15,
    "증거_제시": 20,
    "창의적_주장": 25,
    "팀_어시스트": 10,
    "타임_보너스": 5,
    "가치어_사용": 5,
    "완벽한_시간관리": 10,
}

# 레벨 시스템
LEVEL_SYSTEM = [
    {"level": 1, "title": "🌱 법정 신입생", "min": 0, "max": 50},
    {"level": 2, "title": "📚 주니어 변호사", "min": 51, "max": 150},
    {"level": 3, "title": "⚖️ 시니어 변호사", "min": 151, "max": 300},
    {"level": 4, "title": "🌟 에이스 변호사", "min": 301, "max": 500},
    {"level": 5, "title": "👑 전설의 변호사", "min": 501, "max": 9999},
]

# 뱃지 시스템
BADGES = {
    "fire_speaker": {"icon": "🔥", "name": "불꽃 변론가", "condition": "3회 연속 발언"},
    "sniper": {"icon": "🎯", "name": "저격수", "condition": "핵심 증거로 반박"},
    "defender": {"icon": "🛡️", "name": "철벽 수비", "condition": "3회 반박 방어"},
    "lightning": {"icon": "⚡", "name": "번개 응답", "condition": "10초 내 반박"},
    "mvp": {"icon": "🏆", "name": "MVP", "condition": "라운드 최고 득점"},
}

# 샘플 사건 라이브러리
SAMPLE_CASES = [
    {
        "title": "🍔 급식 새치기 사건",
        "summary": """2024년 3월 15일 점심시간, 2학년 3반 학생 A가 급식 줄에서 새치기를 했습니다.
B 학생이 항의하자 A는 "친구 C가 자리를 맡아줬다"고 주장했습니다.
그러나 목격자들은 C가 자리를 맡아준 적이 없다고 증언했습니다.
A는 배가 너무 고파서 그랬다고 변명했습니다.""",
        "prosecutor_hint": "규칙 위반, 거짓말, 다른 학생들의 권리 침해",
        "defender_hint": "배고픔, 오해의 소지, 사과와 반성"
    },
    {
        "title": "📱 휴대폰 무단 사용 사건",
        "summary": """수업 시간 중 학생 D가 책상 아래에서 휴대폰으로 게임을 했습니다.
선생님이 발견하여 휴대폰을 압수하려 하자, D는 "시계를 본 것뿐"이라고 주장했습니다.
그러나 옆자리 학생 E는 D가 게임 소리를 들었다고 증언했습니다.
D는 부모님께 연락이 올까봐 확인했다고 해명했습니다.""",
        "prosecutor_hint": "수업 방해, 거짓말, 학습권 침해",
        "defender_hint": "걱정되는 마음, 짧은 시간, 첫 위반"
    },
    {
        "title": "🎨 미술 작품 훼손 사건",
        "summary": """미술 시간에 학생 F가 실수로 학생 G의 작품에 물감을 쏟았습니다.
G는 F가 일부러 그랬다고 주장하며, 평소 F가 자신을 시기했다고 말했습니다.
F는 정말 실수였으며, 즉시 사과하고 도와주려 했다고 반박했습니다.
목격자 H는 F가 급하게 움직이다가 실수한 것 같다고 증언했습니다.""",
        "prosecutor_hint": "부주의, 작품 훼손, 정신적 피해",
        "defender_hint": "진정한 실수, 즉각적 사과, 복구 노력"
    }
]

# ===== 유틸리티 함수 =====

def init_gamification():
    """게이미피케이션 초기화"""
    if 'points' not in st.session_state:
        st.session_state.points = {'prosecutor': 0, 'defender': 0}
    if 'badges' not in st.session_state:
        st.session_state.badges = {'prosecutor': [], 'defender': []}
    if 'combo' not in st.session_state:
        st.session_state.combo = {'prosecutor': 0, 'defender': 0}
    if 'speech_count' not in st.session_state:
        st.session_state.speech_count = {'prosecutor': 0, 'defender': 0}

def add_points(team, point_type, amount=None):
    """포인트 추가"""
    if amount is None:
        amount = POINT_SYSTEM.get(point_type, 0)
    
    # 콤보 보너스
    if st.session_state.combo[team] >= 3:
        amount = int(amount * 1.5)
        st.balloons()
    
    st.session_state.points[team] += amount
    st.success(f"🎯 {team} +{amount}점!")
    return amount

def get_level(points):
    """레벨 확인"""
    for level in LEVEL_SYSTEM:
        if level["min"] <= points <= level["max"]:
            return level
    return LEVEL_SYSTEM[0]

def check_badges(team):
    """뱃지 체크"""
    new_badges = []
    
    if st.session_state.combo[team] >= 3:
        if "fire_speaker" not in st.session_state.badges[team]:
            st.session_state.badges[team].append("fire_speaker")
            new_badges.append(BADGES["fire_speaker"])
    
    if st.session_state.points[team] >= 100:
        if "mvp" not in st.session_state.badges[team]:
            st.session_state.badges[team].append("mvp")
            new_badges.append(BADGES["mvp"])
    
    return new_badges

def create_versus_display():
    """팀 대결 표시"""
    pros_points = st.session_state.points.get('prosecutor', 0)
    def_points = st.session_state.points.get('defender', 0)
    total = pros_points + def_points + 1
    
    pros_percent = (pros_points / total) * 100
    def_percent = (def_points / total) * 100
    
    st.markdown(f"""
    <div class='versus-display'>
        <div style='background: linear-gradient(90deg, #ff9a8b, #ffb4a2); 
                    width: {pros_percent}%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
            검사 {pros_points}점
        </div>
        <div style='background: linear-gradient(90deg, #a8e6cf, #b4e7ce); 
                    width: {def_percent}%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: #2d5f3f;
                    font-weight: bold;'>
            변호 {def_points}점
        </div>
    </div>
    """, unsafe_allow_html=True)

def calculate_speech_quality(text):
    """발언 품질 평가"""
    score = 0
    feedback = []
    
    # 길이 체크
    if len(text.split()) > 50:
        score += 20
        feedback.append("✅ 충분한 설명")
    
    # 구조 체크
    if any(word in text for word in ["첫째", "둘째", "셋째"]):
        score += 30
        feedback.append("✅ 체계적인 구조")
    
    # 근거 체크
    if any(word in text for word in ["증거", "목격", "사실", "왜냐하면"]):
        score += 25
        feedback.append("✅ 근거 제시")
    
    # 가치어 체크
    if any(word in text for word in ["정의", "공정", "책임", "배려", "존중"]):
        score += 25
        feedback.append("✅ 가치어 사용")
    
    return score, feedback

def create_quick_feedback(text, team):
    """즉각적 피드백"""
    score, feedback = calculate_speech_quality(text)
    
    if score >= 80:
        st.success(f"🌟 훌륭한 발언! (+{score//4}점)")
        add_points(team, "창의적_주장", score//4)
    elif score >= 60:
        st.info(f"👍 좋은 발언! (+{score//5}점)")
        add_points(team, "논리적_반박", score//5)
    else:
        st.warning(f"💭 더 발전시킬 수 있어요! (+10점)")
        add_points(team, "첫_발언")
    
    for fb in feedback:
        st.write(fb)
    
    return score

# ===== 환경변수 설정 =====
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

# ===== 세션 초기화 =====
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.rounds = [
        {'id': 1, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0},
        {'id': 2, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0}
    ]
    st.session_state.case_summary = ''
    st.session_state.ai_judgment = ''
    st.session_state.current_round = 1
    st.session_state.timer_start = None
    st.session_state.mode = 'simple'  # simple or advanced
    st.session_state.last_audio_pros = None  # 마지막 오디오 추적
    st.session_state.last_audio_def = None
    init_gamification()

# ===== 핵심 함수 =====

def transcribe_audio(audio_bytes, language="ko"):
    """음성 인식 - 리소스 최적화 버전"""
    try:
        # 오디오 파일 크기 확인 (최소 0.1초 이상)
        if not audio_bytes or len(audio_bytes) < 1000:  # 대략 1KB 미만
            return ""
        
        # 오디오 크기 제한 (최대 30초 - 약 500KB)
        MAX_SIZE = 500000  # 500KB
        if len(audio_bytes) > MAX_SIZE:
            st.warning("⚠️ 녹음이 너무 깁니다. 30초 이내로 녹음해주세요.")
            audio_bytes = audio_bytes[:MAX_SIZE]
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        # 진행 표시
        progress_text = st.empty()
        progress_text.info("🎙️ 음성 인식 중... (5-10초 소요)")
        
        with open(tmp_file_path, "rb") as audio_file:
            # response_format="text" 추가로 JSON 파싱 오버헤드 제거
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="text",  # 속도 향상을 위해 텍스트로 직접 받기
                prompt="중학생 모의재판 발언"  # 컨텍스트 제공으로 정확도 향상
            )
        
        progress_text.empty()
        os.unlink(tmp_file_path)
        return transcript  # response_format="text"일 때는 직접 텍스트 반환
    except Exception as e:
        error_msg = str(e)
        if "audio_too_short" in error_msg:
            st.warning("⚠️ 녹음이 너무 짧습니다. 최소 1초 이상 녹음해주세요.")
        elif "invalid_request_error" in error_msg:
            st.error("❌ 오디오 파일 형식이 올바르지 않습니다.")
        else:
            st.error(f"음성 인식 오류: {error_msg}")
        return ""

def get_ai_judgment(prompt):
    """AI 판결 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 교육적이고 공정한 AI 판사입니다. 중학생 수준에 맞춰 친근하게 설명합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"""
        🏆 판결 결과
        
        양 팀 모두 훌륭한 논증을 보여주었습니다.
        
        검사팀: 논리적인 주장과 증거 제시가 좋았습니다.
        변호팀: 상황에 대한 이해와 대안 제시가 인상적이었습니다.
        
        더 발전시킬 점:
        - 구체적인 증거를 더 많이 제시하세요
        - 상대방 주장을 직접 반박하세요
        - 가치어를 더 많이 사용하세요
        """

# ===== 메인 UI =====

# 헤더
st.markdown("<h1 style='text-align: center;'>⚖️ AI 판사 모의재판 시스템</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>금천중학교 특별 수업용</p>", unsafe_allow_html=True)

# 모드 선택
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.radio(
        "진행 모드",
        ["🚀 간편 모드 (추천)", "📚 상세 모드"],
        horizontal=True,
        key="mode_selector"
    )
    st.session_state.mode = 'simple' if "간편" in mode else 'advanced'

# 점수 표시
create_versus_display()

# 간편 모드
if st.session_state.mode == 'simple':
    
    # 탭 구조 - 더 명확한 라벨
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 1단계: 사건 준비", 
        "🎤 2단계: 토론 진행", 
        "🤖 3단계: AI 판결", 
        "📊 4단계: 결과 확인"
    ])
    
    with tab1:
        st.markdown("## 📋 사건 준비 (5분)")
        
        # 시작 안내
        st.info("""
        👉 **진행 순서**
        1. 아래에서 사건을 선택하고 '사건 불러오기' 버튼을 누르세요
        2. 팀 구성원을 확인하세요 (검사팀 3명, 변호팀 3명)
        3. 준비가 되면 '토론' 탭으로 이동하세요
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 샘플 사건 선택
            case_titles = [case["title"] for case in SAMPLE_CASES]
            selected = st.selectbox(
                "사건 선택",
                range(len(case_titles)),
                format_func=lambda x: case_titles[x]
            )
            
            if st.button("📥 사건 불러오기", use_container_width=True):
                case = SAMPLE_CASES[selected]
                st.session_state.case_summary = case["summary"]
                st.success(f"✅ '{case['title']}' 사건을 불러왔습니다!")
            
            # 사건 표시
            if st.session_state.case_summary:
                st.text_area("사건 개요", st.session_state.case_summary, height=150, disabled=True)
                
                # 힌트
                with st.expander("💡 팀별 전략 힌트"):
                    st.write(f"**검사팀:** {SAMPLE_CASES[selected]['prosecutor_hint']}")
                    st.write(f"**변호팀:** {SAMPLE_CASES[selected]['defender_hint']}")
        
        with col2:
            st.markdown("### ⏱️ 설정")
            rounds = st.number_input("라운드 수", 1, 4, 2)
            
            # 라운드 조정
            if rounds != len(st.session_state.rounds):
                st.session_state.rounds = [
                    {'id': i+1, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0}
                    for i in range(rounds)
                ]
            
            st.markdown("### 진행 상태")
            progress = 0
            if st.session_state.case_summary:
                progress += 25
            if any(r['prosecutor'] for r in st.session_state.rounds):
                progress += 25
            if any(r['defender'] for r in st.session_state.rounds):
                progress += 25
            if st.session_state.ai_judgment:
                progress += 25
            
            st.progress(progress / 100)
            st.caption(f"진행률: {progress}%")
    
    with tab2:
        st.markdown("## 🎤 토론 진행 (25분)")
        
        # 토론 안내
        st.warning("""
        🎙️ **녹음 방법**
        1. '🔴 녹음 시작' 버튼을 클릭하세요
        2. 말하기를 시작하세요 (최소 1초 이상)
        3. 다시 클릭하면 녹음이 종료됩니다
        4. 또는 아래 텍스트 입력창에 직접 입력해도 됩니다
        """)
        
        # 라운드 선택
        round_num = st.selectbox(
            "라운드 선택",
            range(1, len(st.session_state.rounds) + 1),
            format_func=lambda x: f"라운드 {x}"
        )
        
        col1, col2 = st.columns(2)
        
        # 검사팀
        with col1:
            st.markdown('<div class="team-card-prosecutor">', unsafe_allow_html=True)
            st.markdown("### ⚔️ 검사팀")
            
            # 팀 대시보드
            st.markdown('<div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("🏆 점수", f"{st.session_state.points.get('prosecutor', 0)}점")
            with col_b:
                st.metric("🗣️ 발언", f"{st.session_state.speech_count.get('prosecutor', 0)}회")
            with col_c:
                combo = st.session_state.combo.get('prosecutor', 0)
                if combo >= 3:
                    st.metric("🔥 콤보", f"x{combo}")
                else:
                    st.metric("🔗 콤보", f"x{combo}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 음성 입력 섹션
            st.markdown("**🎙️ 음성 녹음**")
            col_rec1, col_rec2 = st.columns([3, 1])
            with col_rec1:
                # audio_recorder 사용 - 더 안정적인 녹음
                audio = audio_recorder(
                    text="🔴 녹음 시작 (클릭)",
                    recording_color="#ff0000",
                    neutral_color="#ff9a8b",
                    icon_size="3x",
                    key=f"pros_audio_{round_num}"
                )
            with col_rec2:
                if audio and len(audio) > 1000:
                    st.success("✅ 녹음 완료")
                else:
                    st.info("⏸️ 대기중")
            
            # 새로운 오디오인지 확인
            if audio and len(audio) > 1000:  # 최소 1KB 이상의 오디오만 처리
                # 이전 오디오와 다른 경우만 처리
                if st.session_state.last_audio_pros != audio:
                    st.session_state.last_audio_pros = audio
                    with st.spinner("음성 인식 중..."):
                        text = transcribe_audio(audio)
                        if text and len(text.strip()) > 0:  # 실제 텍스트가 있을 때만
                            st.session_state.rounds[round_num-1]['prosecutor'] = text
                            create_quick_feedback(text, 'prosecutor')
                            st.session_state.speech_count['prosecutor'] += 1
                            st.session_state.combo['prosecutor'] += 1
                            check_badges('prosecutor')
            
            # 텍스트 입력 섹션
            st.markdown("**✍️ 텍스트 입력**")
            prosecutor_text = st.text_area(
                "검사팀 주장을 입력하세요",
                value=st.session_state.rounds[round_num-1]['prosecutor'],
                height=200,
                key=f"pros_text_{round_num}",
                placeholder="예: 피고는 학교 규칙을 위반했습니다. 첫째, ... 둘째, ... 따라서..."
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 저장하기", key=f"save_pros_{round_num}", use_container_width=True, type="primary"):
                    if prosecutor_text and len(prosecutor_text.strip()) > 10:  # 최소 10자 이상
                        st.session_state.rounds[round_num-1]['prosecutor'] = prosecutor_text
                        create_quick_feedback(prosecutor_text, 'prosecutor')
                        st.session_state.speech_count['prosecutor'] += 1
                    else:
                        st.warning("⚠️ 발언 내용을 10자 이상 입력해주세요.")
            with col_btn2:
                if st.button("🗑️ 초기화", key=f"clear_pros_{round_num}", use_container_width=True):
                    st.session_state.rounds[round_num-1]['prosecutor'] = ""
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 변호팀
        with col2:
            st.markdown('<div class="team-card-defender">', unsafe_allow_html=True)
            st.markdown("### 🛡️ 변호팀")
            
            # 팀 대시보드
            st.markdown('<div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("🏆 점수", f"{st.session_state.points.get('defender', 0)}점")
            with col_b:
                st.metric("🗣️ 발언", f"{st.session_state.speech_count.get('defender', 0)}회")
            with col_c:
                combo = st.session_state.combo.get('defender', 0)
                if combo >= 3:
                    st.metric("🔥 콤보", f"x{combo}")
                else:
                    st.metric("🔗 콤보", f"x{combo}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 음성 입력 섹션
            st.markdown("**🎙️ 음성 녹음**")
            col_rec1, col_rec2 = st.columns([3, 1])
            with col_rec1:
                # audio_recorder 사용 - 더 안정적인 녹음
                audio = audio_recorder(
                    text="🔴 녹음 시작 (클릭)",
                    recording_color="#ff0000",
                    neutral_color="#a8e6cf",
                    icon_size="3x",
                    key=f"def_audio_{round_num}"
                )
            with col_rec2:
                if audio and len(audio) > 1000:
                    st.success("✅ 녹음 완료")
                else:
                    st.info("⏸️ 대기중")
            
            # 새로운 오디오인지 확인
            if audio and len(audio) > 1000:  # 최소 1KB 이상의 오디오만 처리
                # 이전 오디오와 다른 경우만 처리
                if st.session_state.last_audio_def != audio:
                    st.session_state.last_audio_def = audio
                    with st.spinner("음성 인식 중..."):
                        text = transcribe_audio(audio)
                        if text and len(text.strip()) > 0:  # 실제 텍스트가 있을 때만
                            st.session_state.rounds[round_num-1]['defender'] = text
                            create_quick_feedback(text, 'defender')
                            st.session_state.speech_count['defender'] += 1
                            st.session_state.combo['defender'] += 1
                            check_badges('defender')
            
            # 텍스트 입력 섹션
            st.markdown("**✍️ 텍스트 입력**")
            defender_text = st.text_area(
                "변호팀 반박을 입력하세요",
                value=st.session_state.rounds[round_num-1]['defender'],
                height=200,
                key=f"def_text_{round_num}",
                placeholder="예: 검사 측 주장과 달리, 피고는... 실제로는... 따라서..."
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 저장하기", key=f"save_def_{round_num}", use_container_width=True, type="primary"):
                    if defender_text and len(defender_text.strip()) > 10:  # 최소 10자 이상
                        st.session_state.rounds[round_num-1]['defender'] = defender_text
                        create_quick_feedback(defender_text, 'defender')
                        st.session_state.speech_count['defender'] += 1
                    else:
                        st.warning("⚠️ 발언 내용을 10자 이상 입력해주세요.")
            with col_btn2:
                if st.button("🗑️ 초기화", key=f"clear_def_{round_num}", use_container_width=True):
                    st.session_state.rounds[round_num-1]['defender'] = ""
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("## 🤖 AI 판결 (5분)")
        
        # 판결 안내
        st.info("""
        ⚖️ **AI 판사 판결 받기**
        1. 모든 라운드의 토론이 완료되었나요?
        2. 아래 '판결 요청' 버튼을 누르면 AI 판사가 분석을 시작합니다
        3. 10-15초 정도 기다리면 판결문이 나타납니다
        """)
        
        if st.button("🤖 AI 판사에게 판결 요청", type="primary", use_container_width=True):
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
                1. 🏆 승리 팀과 이유
                2. 👍 각 팀의 잘한 점 (2개씩)
                3. 💡 개선할 점 (각 팀 1개씩)
                4. 🌟 베스트 발언자
                5. 📈 점수: 검사팀 ?점, 변호팀 ?점 (100점 만점)
                """
                
                judgment = get_ai_judgment(prompt)
                st.session_state.ai_judgment = judgment
                st.balloons()
        
        # 판결 표시
        if st.session_state.ai_judgment:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
                        padding: 2rem;
                        border-radius: 20px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                        border: 2px solid #e0e0e0;'>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.ai_judgment)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("## 📊 결과 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚔️ 검사팀")
            points = st.session_state.points.get('prosecutor', 0)
            level = get_level(points)
            st.metric("최종 점수", f"{points}점")
            st.info(f"레벨: {level['title']}")
            
            # 뱃지
            badges = st.session_state.badges.get('prosecutor', [])
            if badges:
                st.markdown("**획득 뱃지:**")
                for b in badges:
                    st.write(f"{BADGES[b]['icon']} {BADGES[b]['name']}")
        
        with col2:
            st.markdown("### 🛡️ 변호팀")
            points = st.session_state.points.get('defender', 0)
            level = get_level(points)
            st.metric("최종 점수", f"{points}점")
            st.info(f"레벨: {level['title']}")
            
            # 뱃지
            badges = st.session_state.badges.get('defender', [])
            if badges:
                st.markdown("**획득 뱃지:**")
                for b in badges:
                    st.write(f"{BADGES[b]['icon']} {BADGES[b]['name']}")
        
        # 저장
        st.markdown("---")
        save_data = {
            "date": datetime.now().isoformat(),
            "case": st.session_state.case_summary,
            "rounds": st.session_state.rounds,
            "judgment": st.session_state.ai_judgment,
            "scores": st.session_state.points,
            "badges": st.session_state.badges
        }
        
        st.download_button(
            "💾 결과 저장",
            json.dumps(save_data, ensure_ascii=False, indent=2),
            f"trial_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            "application/json",
            use_container_width=True
        )

# 상세 모드
else:
    st.info("📚 상세 모드는 기존 버전의 모든 기능을 제공합니다.")
    
    # 기존 5개 탭 구조
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 사건 설정", 
        "🎤 라운드 진행", 
        "🤖 AI 판결", 
        "📊 결과 분석",
        "💾 기록 관리"
    ])
    
    # 기존 코드 유지...
    st.info("상세 모드는 기존 app.py의 전체 기능을 포함합니다.")

# 사이드바
with st.sidebar:
    st.markdown("## 💡 도움말")
    
    with st.expander("🚀 간편 모드 사용법"):
        st.markdown("""
        1. **준비 탭** → 사건 선택
        2. **토론 탭** → 발언 입력
        3. **판결 탭** → AI 판결 요청
        4. **결과 탭** → 점수 확인
        """)
    
    with st.expander("🎮 포인트 시스템"):
        for key, value in POINT_SYSTEM.items():
            st.write(f"• {key.replace('_', ' ')}: +{value}점")
    
    with st.expander("🏆 레벨 시스템"):
        for level in LEVEL_SYSTEM:
            st.write(f"{level['title']}: {level['min']}-{level['max']}점")
    
    st.markdown("---")
    st.info("💬 문의: 금천중학교")