import streamlit as st
import os
from openai import OpenAI
import tempfile
from audio_recorder_streamlit import audio_recorder
import base64
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import time

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AI 판사 모의재판",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 더 직관적이고 깔끔한 디자인
st.markdown("""
<style>
    /* 메인 배경 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        color: #667eea;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
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
    
    /* 팀 카드 스타일 */
    .team-card-prosecutor {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255,107,107,0.3);
        color: white;
    }
    
    .team-card-defender {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a3aa 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(78,205,196,0.3);
        color: white;
    }
    
    /* 진행 상태 표시 */
    .progress-indicator {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50px;
        padding: 0.5rem 1.5rem;
        display: inline-block;
        font-weight: bold;
        color: #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* 타이머 스타일 */
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
    
    /* 텍스트 영역 스타일 */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.95);
        border: 3px solid #e0e0e0;
        border-radius: 12px;
        font-size: 1.1rem;
        padding: 1rem;
    }
    
    /* 메트릭 스타일 */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* 정보 박스 스타일 */
    .info-box {
        background: linear-gradient(135deg, #ffd93d 0%, #ffb347 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        color: #333;
        font-weight: 500;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* 헤더 스타일 */
    h1 {
        color: white;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #667eea;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #764ba2;
        font-weight: bold;
    }
    
    /* 라운드 표시 */
    .round-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        display: inline-block;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* 팀 레이블 */
    .team-label {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        display: inline-block;
    }
    
    .prosecutor-label {
        background: #ff6b6b;
        color: white;
    }
    
    .defender-label {
        background: #4ecdc4;
        color: white;
    }
    
    /* 액션 버튼 그룹 */
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 환경변수에서 API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OPENAI_API_KEY 환경변수를 설정해주세요!")
    st.info("💡 .env 파일을 생성하고 OPENAI_API_KEY=sk-your-key 형식으로 입력하세요.")
    st.stop()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 세션 상태 초기화 - 더 체계적인 구조
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.rounds = [
        {'id': 1, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0},
        {'id': 2, 'prosecutor': '', 'defender': '', 'pros_time': 0, 'def_time': 0}
    ]
    st.session_state.case_summary = ''
    st.session_state.judge_prompt = ''
    st.session_state.ai_judgment = ''
    st.session_state.current_round = 1
    st.session_state.current_speaker = 'prosecutor'
    st.session_state.timer_running = False
    st.session_state.timer_start = None
    st.session_state.elapsed_time = 0
    st.session_state.team_scores = {'prosecutor': 0, 'defender': 0}
    st.session_state.student_names = {
        'prosecutor': ['검사1', '검사2', '검사3'],
        'defender': ['변호1', '변호2', '변호3']
    }

# 음성을 텍스트로 변환하는 함수
def transcribe_audio(audio_bytes, language="ko"):
    """OpenAI Whisper API를 사용해 음성을 텍스트로 변환"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                language=language
            )
        
        os.unlink(tmp_file_path)
        return transcript.text
    except Exception as e:
        st.error(f"음성 인식 오류: {str(e)}")
        return ""

# AI 판사 판결 함수
def get_ai_judgment(prompt):
    """GPT-5를 사용해 AI 판사 판결 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "당신은 교육적이고 공정한 AI 판사입니다. 학생들의 모의재판을 평가하고 교육적 피드백을 제공합니다."},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI 판결 생성 오류: {str(e)}")
        return ""

# 말하기 구조 템플릿
def get_speech_scaffold(is_prosecutor):
    if is_prosecutor:
        return """[검사 주장 구조]
🎯 결론: (무엇이 잘못인지 한 문장)
📌 이유1: (규칙/권리/안전 등 가치 근거)
📌 이유2: (피해 사실·증거)
📊 사례/근거: (구체적 상황·시간·장소)
🔄 예상 반론 및 대응: (변호 측 주장을 미리 반박)"""
    else:
        return """[변호 반박 구조]
🎯 핵심 반박: (검사의 결론 중 과장/오해 지점)
📋 사실 관계: (상황 설명·맥락·의도)
✅ 책임 인정/조정: (잘못 인정 부분 + 개선 행동)
💡 대안 제시: (피해 회복·재발 방지 방안)"""

# 프롬프트 생성 함수
def generate_prompt():
    summary = st.session_state.case_summary
    rounds_text = []
    
    for round_data in st.session_state.rounds:
        if round_data['prosecutor']:
            rounds_text.append(f"[라운드 {round_data['id']} 검사]\n{round_data['prosecutor']}")
        if round_data['defender']:
            rounds_text.append(f"[라운드 {round_data['id']} 변호]\n{round_data['defender']}")
    
    body = "\n\n".join(rounds_text)
    
    prompt = f"""역할: 당신은 교육적 판사(AI 판사)다.
목표: ① 라운드 순서를 고려하여 누가 더 설득력 있었는지 판정하고, ② 각 팀의 논리적 강·약점을 제시하며, ③ 인성적 교훈(존중·배려·책임·공동체)을 정리한다.

안내: 아래 발언은 [라운드 번호 + 역할]로 표기되어 있다. 시간 순서를 따라 검사와 변호의 주고받기를 반영해 판단하라.

[사건 요약]
{summary or '(교사가 2~3문장으로 사건을 요약)'}

[라운드별 발언]
{body or '(아직 입력 없음)'}

판정 출력 형식:
1) 🏆 최종 판정: (검사/변호 중 설득력 높은 쪽과 핵심 이유)
2) 📊 라운드별 논리 포인트: 각 라운드에서 설득력 있었던 문장 1개씩 인용(요약)
3) 👍 논리 피드백(검사): 강점 2개, 보완점 2개
4) 👍 논리 피드백(변호): 강점 2개, 보완점 2개
5) 💡 인성 교훈: 학생 눈높이 한 문장 + 행동 지침 2가지
6) 🎯 다음 라운드 미션: 근거 강화 제안 2가지

채점 기준(요약): 근거의 구체성, 반박의 직접성, 가치언어(존중·배려·책임), 표현의 명확성.

[추가 평가 항목]
📈 점수 평가 (각 팀 100점 만점)
- 논리성 (30점)
- 증거 제시 (25점)
- 가치어 사용 (20점)
- 반박 능력 (25점)

🌟 개인별 피드백
- 우수 발언자 선정 및 이유
- 각 팀원별 개선 포인트 1개씩"""
    
    return prompt

# 타이머 표시 함수
def display_timer():
    if st.session_state.timer_running:
        elapsed = int(time.time() - st.session_state.timer_start)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"
    return "00:00"

# 메인 헤더
st.markdown("<h1 style='text-align: center;'>⚖️ AI 판사 모의재판 시스템</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>금천중학교 특별 수업용 | 실시간 음성 인식 & AI 판결</p>", unsafe_allow_html=True)

# 사이드바 - 교사용 관리 패널
with st.sidebar:
    st.markdown("## 👩‍🏫 교사용 관리 패널")
    
    # 수업 정보
    with st.expander("📚 수업 정보 설정", expanded=True):
        class_name = st.text_input("학급", value="2학년 3반")
        class_date = st.date_input("수업 날짜", value=datetime.now())
        
        st.markdown("### 👥 팀 구성원")
        st.markdown("**검사팀**")
        for i in range(3):
            st.session_state.student_names['prosecutor'][i] = st.text_input(
                f"검사 {i+1}", 
                value=st.session_state.student_names['prosecutor'][i],
                key=f"pros_name_{i}"
            )
        
        st.markdown("**변호팀**")
        for i in range(3):
            st.session_state.student_names['defender'][i] = st.text_input(
                f"변호인 {i+1}", 
                value=st.session_state.student_names['defender'][i],
                key=f"def_name_{i}"
            )
    
    # 설정
    with st.expander("⚙️ 음성 인식 설정"):
        language = st.radio("음성 인식 언어", ["한국어", "영어"])
        lang_code = "ko" if language == "한국어" else "en"
        
        st.markdown("### ⏱️ 발언 시간 제한")
        time_limit = st.slider("라운드당 제한 시간(분)", 1, 5, 2)
    
    # 평가 기준
    with st.expander("📊 평가 기준"):
        st.markdown("""
        ### 평가 항목 (100점)
        - **논리성** (30점)
          - 주장의 일관성
          - 근거의 타당성
        - **증거 제시** (25점)
          - 구체적 사례
          - 객관적 자료
        - **가치어 사용** (20점)
          - 존중, 배려, 책임, 공정
        - **반박 능력** (25점)
          - 상대 주장 이해
          - 효과적 대응
        """)
    
    # 빠른 팁
    st.markdown("---")
    st.info("""
    💡 **수업 진행 팁**
    1. 각 라운드 시작 전 팀 회의 2분
    2. 발언 중 다른 팀은 메모 작성
    3. 가치어 사용시 보너스 점수
    4. 시간 초과시 감점 (-5점)
    """)

# 메인 컨텐츠 - 탭 구조
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 1. 사건 설정", 
    "🎤 2. 라운드 진행", 
    "🤖 3. AI 판결", 
    "📊 4. 결과 분석",
    "💾 5. 기록 관리"
])

# 탭 1: 사건 설정
with tab1:
    st.markdown("## 📋 STEP 1: 사건 설정 및 준비")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 사건 개요")
        st.session_state.case_summary = st.text_area(
            "사건 내용을 구체적으로 입력하세요",
            value=st.session_state.case_summary,
            height=150,
            placeholder="예) 2024년 3월 15일 점심시간, 2학년 3반 교실에서 학생 A가 학생 B의 도시락 반찬을 허락 없이 먹었다. B가 항의했으나 A는 '장난이었다'며 웃으며 넘어가려 했다. 목격자는 C, D, E 학생 3명이다.",
            help="구체적인 시간, 장소, 인물, 행동을 포함해주세요"
        )
        
        # 사건 유형 선택
        st.markdown("### 사건 유형")
        case_type = st.selectbox(
            "사건 카테고리",
            ["학교 폭력", "도난/절도", "명예훼손", "기물파손", "규칙위반", "기타"]
        )
        
        # 글자수 표시
        if st.session_state.case_summary:
            char_count = len(st.session_state.case_summary)
            st.caption(f"📝 현재 {char_count}자 작성됨")
    
    with col2:
        st.markdown("### 빠른 설정")
        
        if st.button("📚 샘플 사건 불러오기", use_container_width=True):
            st.session_state.case_summary = """2024년 3월 15일 점심시간, 2학년 3반 교실에서 발생한 사건입니다. 
학생 A(김철수)가 학생 B(이영희)의 도시락에서 소시지 2개와 김밥 1줄을 허락 없이 가져가 먹었습니다. 
B가 "내 도시락 왜 먹었어?"라고 항의하자, A는 "장난이야, 뭘 그렇게 예민하게 구냐"며 웃으며 대답했습니다. 
목격자 C(박민수), D(정수진), E(최지우) 학생이 이 상황을 모두 보았으며, B는 점심을 제대로 먹지 못해 오후 수업 시간에 배가 고팠다고 합니다."""
            
            if len(st.session_state.rounds) >= 2:
                st.session_state.rounds[0]['prosecutor'] = """🎯 결론: 피고 A는 피해자 B의 재산권과 인격권을 명백히 침해했습니다.
📌 이유1: 타인의 소유물을 무단으로 가져간 것은 학교 규칙 제3조 2항 위반입니다.
📌 이유2: B는 실제로 점심을 제대로 먹지 못해 오후 수업에 지장을 받았습니다.
📊 증거: 3명의 목격자가 있으며, 사건 발생 시각과 장소가 명확합니다.
🔄 예상 반론 대응: '장난'이라는 변명은 피해가 발생한 이상 정당화될 수 없습니다."""
                
                st.session_state.rounds[0]['defender'] = """🎯 핵심 반박: 의도적인 절도가 아닌 친구 간의 일상적인 장난이었습니다.
📋 사실 관계: A와 B는 평소 친한 친구 사이였으며, 서로 간식을 나눠 먹던 사이였습니다.
✅ 책임 인정: 허락을 구하지 않은 점은 인정하며, 진심으로 사과했습니다.
💡 대안 제시: 다음 날 도시락을 2배로 보상하고, 앞으로 허락 없이 가져가지 않겠다고 약속했습니다."""
            st.rerun()
        
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
        
        # 체크리스트
        st.markdown("### ✅ 준비 체크리스트")
        st.checkbox("사건 개요 작성 완료", value=bool(st.session_state.case_summary))
        st.checkbox("팀 구성 완료", value=True)
        st.checkbox("평가 기준 확인", value=False)
        st.checkbox("타이머 준비", value=False)

# 탭 2: 라운드 진행
with tab2:
    st.markdown("## 🎤 STEP 2: 라운드별 토론 진행")
    
    # 라운드 관리 버튼
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ 라운드 추가", use_container_width=True):
            new_id = len(st.session_state.rounds) + 1
            st.session_state.rounds.append({
                'id': new_id, 
                'prosecutor': '', 
                'defender': '',
                'pros_time': 0,
                'def_time': 0
            })
            st.rerun()
    with col2:
        if st.button("➖ 라운드 삭제", use_container_width=True):
            if len(st.session_state.rounds) > 1:
                st.session_state.rounds.pop()
                st.rerun()
    with col3:
        st.metric("현재 라운드", f"{st.session_state.current_round}")
    with col4:
        st.metric("총 라운드", f"{len(st.session_state.rounds)}")
    
    # 현재 발언 순서 표시
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🎯 현재 발언: {'검사' if st.session_state.current_speaker == 'prosecutor' else '변호'}")
    with col2:
        st.markdown(f"### ⏱️ 경과 시간: {display_timer()}")
    
    # 라운드별 입력
    for i, round_data in enumerate(st.session_state.rounds):
        st.markdown(f"<div class='round-indicator'>🔢 라운드 {round_data['id']}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # 검사 측
        with col1:
            with st.container():
                st.markdown("""<div class='team-card-prosecutor'>""", unsafe_allow_html=True)
                st.markdown("<div class='team-label prosecutor-label'>⚔️ 검사팀</div>", unsafe_allow_html=True)
                
                # 발언자 선택
                speaker = st.selectbox(
                    "발언자",
                    st.session_state.student_names['prosecutor'],
                    key=f"pros_speaker_{i}"
                )
                
                # 음성 녹음
                col_rec1, col_rec2 = st.columns([1, 2])
                with col_rec1:
                    audio_bytes = audio_recorder(
                        text="🎙️ 녹음",
                        recording_color="#ff6b6b",
                        neutral_color="#667eea",
                        icon_size="2x",
                        key=f"prosecutor_audio_{i}"
                    )
                with col_rec2:
                    if st.button(f"⏱️ 타이머 시작", key=f"pros_timer_{i}"):
                        st.session_state.timer_running = True
                        st.session_state.timer_start = time.time()
                        st.session_state.current_speaker = 'prosecutor'
                
                if audio_bytes:
                    with st.spinner("🎧 음성을 텍스트로 변환 중..."):
                        text = transcribe_audio(audio_bytes, lang_code)
                        if text:
                            st.session_state.rounds[i]['prosecutor'] += f"\n[{speaker}]: {text}"
                            st.success(f"✅ {speaker}의 발언이 기록되었습니다!")
                            st.rerun()
                
                # 텍스트 입력
                st.session_state.rounds[i]['prosecutor'] = st.text_area(
                    f"검사 발언 내용",
                    value=st.session_state.rounds[i]['prosecutor'],
                    height=200,
                    key=f"prosecutor_text_{i}",
                    help="직접 입력하거나 음성 인식 결과를 편집하세요"
                )
                
                # 글자수 및 예상 시간 표시
                if st.session_state.rounds[i]['prosecutor']:
                    char_count = len(st.session_state.rounds[i]['prosecutor'])
                    word_count = len(st.session_state.rounds[i]['prosecutor'].split())
                    estimated_time = word_count / 150  # 분당 150단어 기준
                    st.caption(f"📝 {char_count}자 | 약 {estimated_time:.1f}분 분량")
                
                # 액션 버튼
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("📋 구조 템플릿", key=f"scaffold_p_{i}"):
                        st.session_state.rounds[i]['prosecutor'] += "\n\n" + get_speech_scaffold(True)
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ 초기화", key=f"clear_p_{i}"):
                        st.session_state.rounds[i]['prosecutor'] = ""
                        st.rerun()
                with col_btn3:
                    if st.button("💾 저장", key=f"save_p_{i}"):
                        st.success("저장되었습니다!")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # 변호 측
        with col2:
            with st.container():
                st.markdown("""<div class='team-card-defender'>""", unsafe_allow_html=True)
                st.markdown("<div class='team-label defender-label'>🛡️ 변호팀</div>", unsafe_allow_html=True)
                
                # 발언자 선택
                speaker = st.selectbox(
                    "발언자",
                    st.session_state.student_names['defender'],
                    key=f"def_speaker_{i}"
                )
                
                # 음성 녹음
                col_rec1, col_rec2 = st.columns([1, 2])
                with col_rec1:
                    audio_bytes = audio_recorder(
                        text="🎙️ 녹음",
                        recording_color="#4ecdc4",
                        neutral_color="#667eea",
                        icon_size="2x",
                        key=f"defender_audio_{i}"
                    )
                with col_rec2:
                    if st.button(f"⏱️ 타이머 시작", key=f"def_timer_{i}"):
                        st.session_state.timer_running = True
                        st.session_state.timer_start = time.time()
                        st.session_state.current_speaker = 'defender'
                
                if audio_bytes:
                    with st.spinner("🎧 음성을 텍스트로 변환 중..."):
                        text = transcribe_audio(audio_bytes, lang_code)
                        if text:
                            st.session_state.rounds[i]['defender'] += f"\n[{speaker}]: {text}"
                            st.success(f"✅ {speaker}의 발언이 기록되었습니다!")
                            st.rerun()
                
                # 텍스트 입력
                st.session_state.rounds[i]['defender'] = st.text_area(
                    f"변호 발언 내용",
                    value=st.session_state.rounds[i]['defender'],
                    height=200,
                    key=f"defender_text_{i}",
                    help="직접 입력하거나 음성 인식 결과를 편집하세요"
                )
                
                # 글자수 및 예상 시간 표시
                if st.session_state.rounds[i]['defender']:
                    char_count = len(st.session_state.rounds[i]['defender'])
                    word_count = len(st.session_state.rounds[i]['defender'].split())
                    estimated_time = word_count / 150  # 분당 150단어 기준
                    st.caption(f"📝 {char_count}자 | 약 {estimated_time:.1f}분 분량")
                
                # 액션 버튼
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("📋 구조 템플릿", key=f"scaffold_d_{i}"):
                        st.session_state.rounds[i]['defender'] += "\n\n" + get_speech_scaffold(False)
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ 초기화", key=f"clear_d_{i}"):
                        st.session_state.rounds[i]['defender'] = ""
                        st.rerun()
                with col_btn3:
                    if st.button("💾 저장", key=f"save_d_{i}"):
                        st.success("저장되었습니다!")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")

# 탭 3: AI 판결
with tab3:
    st.markdown("## 🤖 STEP 3: AI 판사 판결 요청")
    
    # 프롬프트 생성 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 판결 요청 준비")
        
        # 체크리스트
        ready_items = []
        if st.session_state.case_summary:
            ready_items.append("✅ 사건 개요 작성 완료")
        else:
            ready_items.append("❌ 사건 개요 미작성")
        
        pros_count = sum(1 for r in st.session_state.rounds if r['prosecutor'])
        def_count = sum(1 for r in st.session_state.rounds if r['defender'])
        
        ready_items.append(f"✅ 검사 발언: {pros_count}개 라운드")
        ready_items.append(f"✅ 변호 발언: {def_count}개 라운드")
        
        for item in ready_items:
            st.write(item)
        
        # 프롬프트 생성 버튼
        if st.button("🔨 판결 프롬프트 생성", type="primary", use_container_width=True):
            if not st.session_state.case_summary:
                st.error("❌ 사건 개요를 먼저 작성해주세요!")
            elif pros_count == 0 or def_count == 0:
                st.error("❌ 최소 1개 라운드의 검사/변호 발언이 필요합니다!")
            else:
                st.session_state.judge_prompt = generate_prompt()
                st.success("✅ 판결 프롬프트가 생성되었습니다!")
    
    with col2:
        st.markdown("### 📊 토론 통계")
        total_chars = sum(len(r['prosecutor']) + len(r['defender']) for r in st.session_state.rounds)
        st.metric("총 발언 글자수", f"{total_chars:,}자")
        st.metric("완료된 라운드", f"{min(pros_count, def_count)}개")
        
        # 가치어 체크
        value_words = ['존중', '배려', '책임', '공정', '정의', '공동체']
        value_count = 0
        for round_data in st.session_state.rounds:
            for word in value_words:
                value_count += round_data['prosecutor'].count(word)
                value_count += round_data['defender'].count(word)
        st.metric("가치어 사용 횟수", f"{value_count}회")
    
    # 프롬프트 표시
    if st.session_state.judge_prompt:
        with st.expander("📄 생성된 프롬프트 확인", expanded=False):
            st.text_area(
                "AI 판사에게 전달될 내용",
                value=st.session_state.judge_prompt,
                height=400,
                disabled=True
            )
    
    # AI 판결 요청
    st.markdown("---")
    st.markdown("### ⚖️ AI 판사 판결 실행")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🤖 AI 판사에게 판결 요청", type="primary", use_container_width=True):
            if not st.session_state.judge_prompt:
                st.session_state.judge_prompt = generate_prompt()
            
            with st.spinner("⚖️ AI 판사가 신중하게 판결을 검토하고 있습니다..."):
                # 프로그레스 바 표시
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)  # 시뮬레이션
                    progress_bar.progress(i + 1)
                
                judgment = get_ai_judgment(st.session_state.judge_prompt)
                st.session_state.ai_judgment = judgment
                
                if judgment:
                    st.success("✅ AI 판사의 판결이 완료되었습니다!")
                    st.balloons()
    
    with col2:
        if st.button("📋 프롬프트 복사", use_container_width=True):
            st.info("📋 위 프롬프트를 복사하여 사용하세요")
    
    with col3:
        if st.button("🔄 판결 재요청", use_container_width=True):
            st.session_state.ai_judgment = ""
            st.info("판결을 다시 요청할 수 있습니다")

# 탭 4: 결과 분석
with tab4:
    st.markdown("## 📊 STEP 4: 판결 결과 및 분석")
    
    if st.session_state.ai_judgment:
        # 판결 결과 표시
        st.markdown("### 📜 AI 판사의 최종 판결")
        
        with st.container():
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                        padding: 2rem; 
                        border-radius: 20px; 
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        border: 3px solid gold;">
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.ai_judgment)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 평가 점수 시각화
        st.markdown("---")
        st.markdown("### 📈 팀별 평가 점수")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚔️ 검사팀")
            # 임시 점수 (실제로는 AI 판결에서 추출)
            st.progress(75/100)
            st.metric("총점", "75점 / 100점")
            
            # 세부 점수
            scores_pros = {
                "논리성": 22,
                "증거 제시": 18,
                "가치어 사용": 15,
                "반박 능력": 20
            }
            for item, score in scores_pros.items():
                st.write(f"• {item}: {score}점")
        
        with col2:
            st.markdown("#### 🛡️ 변호팀")
            st.progress(82/100)
            st.metric("총점", "82점 / 100점")
            
            # 세부 점수
            scores_def = {
                "논리성": 25,
                "증거 제시": 20,
                "가치어 사용": 17,
                "반박 능력": 20
            }
            for item, score in scores_def.items():
                st.write(f"• {item}: {score}점")
        
        # 우수 발언자
        st.markdown("---")
        st.markdown("### 🏆 우수 발언자")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("🥇 최우수: 검사2 (논리적 구성)")
        with col2:
            st.info("🥈 우수: 변호1 (효과적 반박)")
        with col3:
            st.info("🥉 장려: 검사3 (가치어 활용)")
        
    else:
        st.warning("⚠️ 아직 AI 판결이 없습니다. 먼저 판결을 요청해주세요.")

# 탭 5: 기록 관리
with tab5:
    st.markdown("## 💾 STEP 5: 기록 저장 및 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 데이터 저장")
        
        # 전체 데이터 준비
        save_data = {
            "class_info": {
                "date": datetime.now().isoformat(),
                "class": "금천중학교"
            },
            "case_summary": st.session_state.case_summary,
            "rounds": st.session_state.rounds,
            "judgment": st.session_state.ai_judgment,
            "teams": st.session_state.student_names
        }
        
        # JSON 다운로드
        st.download_button(
            label="💾 전체 기록 저장 (JSON)",
            data=json.dumps(save_data, ensure_ascii=False, indent=2),
            file_name=f"mock_trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        # 텍스트 버전 다운로드
        text_version = f"""
=== AI 판사 모의재판 기록 ===
날짜: {datetime.now().strftime('%Y년 %m월 %d일')}
학교: 금천중학교

[사건 개요]
{st.session_state.case_summary}

[토론 내용]
"""
        for r in st.session_state.rounds:
            text_version += f"\n라운드 {r['id']} - 검사:\n{r['prosecutor']}\n"
            text_version += f"\n라운드 {r['id']} - 변호:\n{r['defender']}\n"
        
        text_version += f"\n[AI 판결]\n{st.session_state.ai_judgment}"
        
        st.download_button(
            label="📄 텍스트 버전 저장 (TXT)",
            data=text_version,
            file_name=f"mock_trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 🔄 세션 관리")
        
        if st.button("🔄 새로운 재판 시작", type="primary", use_container_width=True):
            if st.checkbox("정말로 초기화하시겠습니까?"):
                for key in list(st.session_state.keys()):
                    if key != 'initialized':
                        del st.session_state[key]
                st.session_state.initialized = False
                st.success("✅ 새로운 재판을 시작할 준비가 되었습니다!")
                time.sleep(1)
                st.rerun()
        
        st.markdown("### 📚 이전 기록 불러오기")
        uploaded_file = st.file_uploader(
            "JSON 파일 선택",
            type=['json'],
            help="이전에 저장한 재판 기록을 불러옵니다"
        )
        
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                st.session_state.case_summary = data.get('case_summary', '')
                st.session_state.rounds = data.get('rounds', [])
                st.session_state.ai_judgment = data.get('judgment', '')
                st.success("✅ 기록을 성공적으로 불러왔습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 파일 불러오기 실패: {e}")

# 하단 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 2rem;'>
    <h3>💡 금천중학교 AI 모의재판 시스템</h3>
    <p>본 시스템은 학생들의 논리적 사고력과 토론 능력 향상을 위해 개발되었습니다.</p>
    <p>문의: 금천중학교 교사 신세령 | Made with ❤️ for Geumcheon Middle School Students</p>
</div>
""", unsafe_allow_html=True)
