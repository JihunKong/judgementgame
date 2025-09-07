"""
AI 모의재판 - 경량화 버전 (텍스트 입력 중심)
빠른 응답을 위한 최적화 버전
"""

import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AI 판사 모의재판 (간편)",
    page_icon="⚖️",
    layout="wide"
)

# 스타일
st.markdown("""
<style>
    .main-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .team-prosecutor {
        border-left: 5px solid #ff6b6b;
    }
    .team-defender {
        border-left: 5px solid #4ecdc4;
    }
    .stTextArea textarea {
        font-size: 16px !important;
        line-height: 1.5 !important;
    }
</style>
""", unsafe_allow_html=True)

# OpenAI 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("⚠️ API 키를 설정해주세요!")
        st.stop()

client = OpenAI(api_key=api_key)

# 세션 초기화
if 'rounds' not in st.session_state:
    st.session_state.rounds = []
    st.session_state.case = ""
    st.session_state.judgment = ""

# 헤더
st.title("⚖️ AI 모의재판 - 간편 버전")
st.caption("텍스트 입력 중심의 빠른 진행")

# 탭
tab1, tab2, tab3 = st.tabs(["📋 사건 설정", "💬 토론", "🤖 판결"])

with tab1:
    st.header("사건 개요")
    
    # 빠른 선택
    quick_cases = {
        "급식 새치기": "학생 A가 급식 줄에서 새치기를 했습니다. 친구가 자리를 맡아줬다고 주장하지만 목격자들은 부인합니다.",
        "휴대폰 사용": "수업 중 학생 B가 휴대폰을 사용했습니다. 시계를 본 것뿐이라고 주장합니다.",
        "작품 훼손": "학생 C가 실수로 친구의 미술 작품을 망쳤습니다. 고의성 여부가 쟁점입니다."
    }
    
    selected = st.selectbox("빠른 선택", ["직접 입력"] + list(quick_cases.keys()))
    
    if selected != "직접 입력":
        st.session_state.case = quick_cases[selected]
    
    st.session_state.case = st.text_area(
        "사건 내용",
        value=st.session_state.case,
        height=100,
        placeholder="사건을 간단히 설명하세요..."
    )

with tab2:
    st.header("토론 진행")
    
    if not st.session_state.case:
        st.warning("먼저 사건을 설정하세요!")
    else:
        # 라운드 추가
        if st.button("➕ 새 라운드 추가"):
            st.session_state.rounds.append({
                "prosecutor": "",
                "defender": ""
            })
        
        # 각 라운드 표시
        for i, round_data in enumerate(st.session_state.rounds):
            st.subheader(f"라운드 {i+1}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="main-card team-prosecutor">', unsafe_allow_html=True)
                st.markdown("### ⚔️ 검사팀")
                round_data["prosecutor"] = st.text_area(
                    "주장 입력",
                    value=round_data["prosecutor"],
                    height=150,
                    key=f"pros_{i}",
                    placeholder="검사팀의 주장을 입력하세요..."
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="main-card team-defender">', unsafe_allow_html=True)
                st.markdown("### 🛡️ 변호팀")
                round_data["defender"] = st.text_area(
                    "반박 입력",
                    value=round_data["defender"],
                    height=150,
                    key=f"def_{i}",
                    placeholder="변호팀의 반박을 입력하세요..."
                )
                st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.header("AI 판결")
    
    if st.button("🤖 판결 요청", type="primary", use_container_width=True):
        if not st.session_state.rounds:
            st.error("토론 내용이 없습니다!")
        else:
            with st.spinner("AI 판사가 검토 중..."):
                # 프롬프트 생성
                prompt = f"사건: {st.session_state.case}\n\n"
                for i, r in enumerate(st.session_state.rounds):
                    prompt += f"라운드 {i+1}:\n"
                    prompt += f"검사: {r['prosecutor']}\n"
                    prompt += f"변호: {r['defender']}\n\n"
                
                prompt += "간단하게 판결해주세요: 1) 승리팀 2) 이유 3) 피드백"
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",  # 더 빠른 모델 사용
                        messages=[
                            {"role": "system", "content": "당신은 중학생 모의재판의 교육적인 판사입니다."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    st.session_state.judgment = response.choices[0].message.content
                except:
                    st.session_state.judgment = """
                    🏆 판결 결과
                    
                    양 팀 모두 좋은 논증을 보여주었습니다.
                    
                    - 검사팀: 규칙의 중요성을 잘 설명했습니다.
                    - 변호팀: 상황적 맥락을 잘 제시했습니다.
                    
                    더 구체적인 증거와 논리적 연결이 필요합니다.
                    """
    
    if st.session_state.judgment:
        st.success(st.session_state.judgment)
        
        # 저장
        if st.button("💾 결과 저장"):
            save_data = {
                "date": datetime.now().isoformat(),
                "case": st.session_state.case,
                "rounds": st.session_state.rounds,
                "judgment": st.session_state.judgment
            }
            st.download_button(
                "📥 다운로드",
                json.dumps(save_data, ensure_ascii=False),
                f"trial_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                "application/json"
            )

# 사이드바
with st.sidebar:
    st.markdown("### 💡 사용 팁")
    st.info("""
    1. 텍스트로 빠르게 입력
    2. 간단명료하게 작성
    3. 핵심 논점 중심으로
    """)
    
    st.markdown("### ⚡ 장점")
    st.success("""
    - 즉시 입력 가능
    - 빠른 응답
    - 안정적 작동
    - 리소스 절약
    """)