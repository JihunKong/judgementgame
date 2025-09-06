import streamlit as st
import os
from openai import OpenAI
import tempfile
from audio_recorder_streamlit import audio_recorder
import base64
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(
    page_title="AI 판사 모의재판",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .round-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .role-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .prosecutor-tag {
        background: #ff6b6b;
        color: white;
    }
    .defender-tag {
        background: #4ecdc4;
        color: white;
    }
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #e0e0e0;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 환경변수에서 API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OPENAI_API_KEY 환경변수를 설정해주세요!")
    st.stop()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 세션 상태 초기화
if 'rounds' not in st.session_state:
    st.session_state.rounds = [
        {'id': 1, 'prosecutor': '', 'defender': ''},
        {'id': 2, 'prosecutor': '', 'defender': ''}
    ]

if 'case_summary' not in st.session_state:
    st.session_state.case_summary = ''

if 'judge_prompt' not in st.session_state:
    st.session_state.judge_prompt = ''

if 'ai_judgment' not in st.session_state:
    st.session_state.ai_judgment = ''

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
    """GPT-4를 사용해 AI 판사 판결 생성"""
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
        return """[주장 구조]
결론: (무엇이 잘못인지 한 문장)
이유1: (규칙/권리/안전 등 가치 근거)
이유2: (피해 사실·증거)
사례/근거: (구체적 상황·시간·장소)
예상 반론 및 대응: (변호 측 주장을 미리 반박)"""
    else:
        return """[반박 구조]
핵심 반박: (검사의 결론 중 과장/오해 지점)
사실 관계: (상황 설명·맥락·의도)
책임 인정/조정: (잘못 인정 부분 + 개선 행동)
대안 제시: (피해 회복·재발 방지 방안)"""

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
1) 판정: (검사/변호 중 설득력 높은 쪽과 핵심 이유)
2) 라운드별 논리 포인트: 각 라운드에서 설득력 있었던 문장 1개씩 인용(요약)
3) 논리 피드백(검사): 강점 2개, 보완점 2개
4) 논리 피드백(변호사): 강점 2개, 보완점 2개
5) 인성 교훈: 학생 눈높이 한 문장 + 행동 지침 2가지
6) 다음 라운드 미션: 근거 강화 제안 2가지

채점 기준(요약): 근거의 구체성, 반박의 직접성, 가치언어(존중·배려·책임), 표현의 명확성.

[추가 지시: 판결 근거·타당성 피드백 & 보완 제안]
판결을 내린 뒤, 아래 형식으로 양 팀의 주장/근거를 분석하고 다음 라운드 준비를 돕는 피드백을 제시하라.

1) 판결 근거 요약(핵심 요소)
- 검사: 판결에 영향을 미친 결정적 주장/근거 2~3개를 한 줄씩 요약하고, 각 항목에 [관련성], [충분성], [논리적 연결]을 1~5로 평가 + 1문장 이유.
- 변호: 위와 동일.

2) 타당성 진단(팀별 미니 루브릭, 1~5점 + 한 줄 이유)
- 주장 명료성
- 근거의 관련성
- 근거의 충분성(구체성/신뢰도)
- 반박의 직접성(상대 핵심 주장에 정확히 대응했는가)
- 가치 언어 사용(존중·배려·책임·공정 등)

3) 구체 피드백(부족한 점과 보완 방법)
- 검사: 강점 2개 / 부족한 점 2개 / 바로 적용 가능한 보완 방법 2개
- 변호: 강점 2개 / 부족한 점 2개 / 바로 적용 가능한 보완 방법 2개
※ 보완 방법 예: 규칙 조항 번호 인용, 시간·장소·행동 수치화, 목격 진술 형식화, 예상 반론 한 문장 선제 삽입 등."""
    
    return prompt

# 메인 앱
st.title("⚖️ AI 판사 모의재판 - 라운드 기반 음성 인식")
st.markdown("### 라운드(턴)별로 검사·변호 발언을 기록하고, AI 판사가 판결과 피드백을 제공합니다.")

# 사이드바 - 설정
with st.sidebar:
    st.header("⚙️ 설정")
    language = st.radio("음성 인식 언어", ["한국어", "영어"])
    lang_code = "ko" if language == "한국어" else "en"
    
    st.markdown("---")
    st.markdown("### 📌 사용 팁")
    st.info("""
    1. 한 명씩 차례로 발언하세요
    2. 가치어(존중·배려·책임·공정) 포함
    3. "예상 반론 및 대응" 문장 사용
    4. 팀별 타이머 활용 권장
    """)

# STEP 1: 사건 요약
st.markdown("### 📋 STEP 1: 사건 요약")
col1, col2 = st.columns([3, 1])
with col1:
    st.session_state.case_summary = st.text_area(
        "사건 개요를 입력하세요",
        value=st.session_state.case_summary,
        height=100,
        placeholder="예) 쉬는 시간, A가 B의 연필을 허락 없이 가져갔다. B는 되돌려 달라 했으나 A는 웃으며 무시했다."
    )
with col2:
    if st.button("📝 샘플 불러오기", use_container_width=True):
        st.session_state.case_summary = "점심시간, A가 B의 도시락 반찬을 허락 없이 먹음. B가 항의했으나 A는 장난이라며 웃음. 다수 목격."
        if len(st.session_state.rounds) >= 2:
            st.session_state.rounds[0]['prosecutor'] = "결론: 피해자의 소유권을 침해했습니다. 이유1: 허락 없는 사용은 규칙 위반. 이유2: B는 실제 손실과 불쾌감. 사례: 점심시간, 목격 다수. 예상 반론 대응: 장난이라도 피해가 발생하면 책임이 면제되지 않음."
            st.session_state.rounds[0]['defender'] = "핵심 반박: 고의적 침해가 아니라 즉흥적 장난. 사실 관계: 한 입 먹고 곧 돌려주려 함. 책임 조정: 사과 및 보상 의사. 대안: 재발 방지 서약."
            st.session_state.rounds[1]['prosecutor'] = "반박: 사과 의사가 있었다 해도 사전 허락 부재는 핵심 문제. 재발 방지 약속은 인정하나 책임은 남음."
            st.session_state.rounds[1]['defender'] = "보완: 피해자 동의 하에 봉사활동·캠페인 참여로 회복적 조치. 상황 이해 요청."
        st.rerun()

# STEP 2: 라운드 관리
st.markdown("### 🔄 STEP 2: 라운드 관리")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("➕ 라운드 추가"):
        new_id = len(st.session_state.rounds) + 1
        st.session_state.rounds.append({'id': new_id, 'prosecutor': '', 'defender': ''})
        st.rerun()
with col2:
    if st.button("➖ 마지막 라운드 삭제"):
        if len(st.session_state.rounds) > 1:
            st.session_state.rounds.pop()
            st.rerun()
with col3:
    st.caption("💡 권장: 2~3라운드 (발언 1분 / 반박 1분 / 최종 30초)")

# 라운드별 발언 기록
st.markdown("### 🎤 라운드별 발언 기록")

for i, round_data in enumerate(st.session_state.rounds):
    with st.container():
        st.markdown(f"""
        <div class="round-card">
            <h4>🔢 라운드 {round_data['id']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # 검사 측
        with col1:
            st.markdown('<span class="role-tag prosecutor-tag">검사</span>', unsafe_allow_html=True)
            
            # 음성 녹음
            audio_bytes = audio_recorder(
                text=f"🎙️ 녹음",
                recording_color="#ff6b6b",
                neutral_color="#667eea",
                icon_size="2x",
                key=f"prosecutor_audio_{i}"
            )
            
            if audio_bytes:
                with st.spinner("음성을 텍스트로 변환 중..."):
                    text = transcribe_audio(audio_bytes, lang_code)
                    if text:
                        st.session_state.rounds[i]['prosecutor'] += " " + text if st.session_state.rounds[i]['prosecutor'] else text
                        st.success("✅ 음성 인식 완료!")
                        st.rerun()
            
            # 텍스트 입력
            st.session_state.rounds[i]['prosecutor'] = st.text_area(
                f"검사 발언 (라운드 {round_data['id']})",
                value=st.session_state.rounds[i]['prosecutor'],
                height=150,
                key=f"prosecutor_text_{i}"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📋 말하기 구조", key=f"scaffold_p_{i}"):
                    st.session_state.rounds[i]['prosecutor'] += "\n\n" + get_speech_scaffold(True)
                    st.rerun()
            with col_btn2:
                if st.button("🗑️ 지우기", key=f"clear_p_{i}"):
                    st.session_state.rounds[i]['prosecutor'] = ""
                    st.rerun()
        
        # 변호 측
        with col2:
            st.markdown('<span class="role-tag defender-tag">변호</span>', unsafe_allow_html=True)
            
            # 음성 녹음
            audio_bytes = audio_recorder(
                text=f"🎙️ 녹음",
                recording_color="#4ecdc4",
                neutral_color="#667eea",
                icon_size="2x",
                key=f"defender_audio_{i}"
            )
            
            if audio_bytes:
                with st.spinner("음성을 텍스트로 변환 중..."):
                    text = transcribe_audio(audio_bytes, lang_code)
                    if text:
                        st.session_state.rounds[i]['defender'] += " " + text if st.session_state.rounds[i]['defender'] else text
                        st.success("✅ 음성 인식 완료!")
                        st.rerun()
            
            # 텍스트 입력
            st.session_state.rounds[i]['defender'] = st.text_area(
                f"변호 발언 (라운드 {round_data['id']})",
                value=st.session_state.rounds[i]['defender'],
                height=150,
                key=f"defender_text_{i}"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📋 말하기 구조", key=f"scaffold_d_{i}"):
                    st.session_state.rounds[i]['defender'] += "\n\n" + get_speech_scaffold(False)
                    st.rerun()
            with col_btn2:
                if st.button("🗑️ 지우기", key=f"clear_d_{i}"):
                    st.session_state.rounds[i]['defender'] = ""
                    st.rerun()

st.markdown("---")

# STEP 3: AI 판사 프롬프트 및 판결
st.markdown("### 🤖 STEP 3: AI 판사 프롬프트 및 판결")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("📝 프롬프트 자동 생성", type="primary", use_container_width=True):
        st.session_state.judge_prompt = generate_prompt()
        st.success("✅ 프롬프트가 생성되었습니다!")

with col2:
    if st.button("📋 프롬프트 복사", use_container_width=True):
        st.write(st.session_state.judge_prompt)
        st.info("위 텍스트를 복사하여 사용하세요")

# 프롬프트 표시
if st.session_state.judge_prompt:
    with st.expander("생성된 프롬프트 보기", expanded=False):
        st.text_area("AI 판사 프롬프트", value=st.session_state.judge_prompt, height=400, disabled=True)

# AI 판결 요청
st.markdown("### ⚖️ AI 판사 판결")
if st.button("🤖 AI 판사에게 판결 요청", type="primary", use_container_width=True):
    if not st.session_state.judge_prompt:
        st.session_state.judge_prompt = generate_prompt()
    
    with st.spinner("AI 판사가 판결을 검토하고 있습니다..."):
        judgment = get_ai_judgment(st.session_state.judge_prompt)
        st.session_state.ai_judgment = judgment

# AI 판결 결과 표시
if st.session_state.ai_judgment:
    st.markdown("### 📜 AI 판사의 판결")
    with st.container():
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.ai_judgment)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 판결 저장
    col1, col2 = st.columns(2)
    with col1:
        # 판결 결과 다운로드
        judgment_data = {
            "case_summary": st.session_state.case_summary,
            "rounds": st.session_state.rounds,
            "judgment": st.session_state.ai_judgment,
            "timestamp": datetime.now().isoformat()
        }
        
        st.download_button(
            label="💾 판결 결과 저장 (JSON)",
            data=json.dumps(judgment_data, ensure_ascii=False, indent=2),
            file_name=f"ai_judge_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        if st.button("🔄 새로운 재판 시작"):
            for key in st.session_state.keys():
                if key not in ['rounds']:
                    del st.session_state[key]
            st.session_state.rounds = [
                {'id': 1, 'prosecutor': '', 'defender': ''},
                {'id': 2, 'prosecutor': '', 'defender': ''}
            ]
            st.session_state.case_summary = ''
            st.session_state.judge_prompt = ''
            st.session_state.ai_judgment = ''
            st.rerun()

# 하단 정보
st.markdown("---")
st.markdown("""
### 💡 수업 활용 팁
- **가치어 체크**: 존중·배려·책임·공정 중 최소 2개 포함
- **논리 구조**: "예상 반론 및 대응" 문장 필수 사용
- **시간 관리**: 팀별 타이머 표시로 공정성 확보
- **피드백 활용**: AI 판사의 피드백을 다음 라운드에 반영
""")

st.caption("Made with ❤️ for Geumcheon Middle School Students")
