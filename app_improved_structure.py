"""
금천중학교 AI 모의재판 - 개선된 앱 구조 예시
중학생 UX 최적화를 반영한 메인 앱 구조
"""

import streamlit as st
from ui_improvements import (
    SimplifiedModeUI,
    GamificationSystem,
    TeamCollaborationTools,
    SmartTimerSystem,
    VisualFeedbackSystem,
    add_animations
)

# 페이지 설정 - 반응형 디자인
def setup_page():
    """디바이스에 따른 적응형 페이지 설정"""
    # 모바일 감지 (세션 상태나 쿼리 파라미터 활용)
    is_mobile = st.query_params.get('mobile', False)
    
    st.set_page_config(
        page_title="AI 판사 모의재판",
        page_icon="⚖️",
        layout="centered" if is_mobile else "wide",
        initial_sidebar_state="collapsed" if is_mobile else "expanded"
    )
    
    # 애니메이션 CSS 추가
    add_animations()


def initialize_session():
    """세션 상태 초기화 - 구조화된 데이터 관리"""
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = 'simple'  # 'simple' or 'advanced'
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    if 'class_start_time' not in st.session_state:
        st.session_state.class_start_time = None
    
    # 시스템 인스턴스 초기화
    if 'systems' not in st.session_state:
        st.session_state.systems = {
            'ui': SimplifiedModeUI(),
            'gamification': GamificationSystem(),
            'collaboration': TeamCollaborationTools(),
            'timer': SmartTimerSystem(),
            'feedback': VisualFeedbackSystem()
        }


def show_onboarding():
    """첫 사용자를 위한 온보딩"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; padding: 2rem; color: white; text-align: center;'>
        <h1>🎉 AI 모의재판에 오신 것을 환영합니다!</h1>
        <p style='font-size: 1.2rem;'>함께 정의로운 판결을 만들어봐요</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 오늘의 목표
        - 논리적으로 주장하기
        - 증거를 바탕으로 설득하기
        - 팀워크로 협력하기
        """)
    
    with col2:
        st.markdown("""
        ### 🏆 보상 시스템
        - 포인트 획득으로 순위 경쟁
        - 특별 배지 수집
        - 최우수 팀/개인 선정
        """)
    
    # 모드 선택
    st.markdown("### 🎮 플레이 모드 선택")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌟 간편 모드", use_container_width=True, type="primary"):
            st.session_state.app_mode = 'simple'
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("🚀 고급 모드", use_container_width=True):
            st.session_state.app_mode = 'advanced'
            st.rerun()


def run_simple_mode():
    """간편 모드 - 단계별 진행"""
    ui = st.session_state.systems['ui']
    timer = st.session_state.systems['timer']
    gamification = st.session_state.systems['gamification']
    
    # 수업 시작 시간 기록
    if st.session_state.class_start_time is None:
        st.session_state.class_start_time = time.time()
    
    elapsed_time = int((time.time() - st.session_state.class_start_time) / 60)
    
    # 진행 상황 헤더
    ui.show_progress_header(st.session_state.current_step, elapsed_time)
    
    # 현재 단계 컨텐츠
    if st.session_state.current_step == 1:
        show_team_setup()
    elif st.session_state.current_step == 2:
        show_case_understanding()
    elif st.session_state.current_step == 3:
        show_strategy_meeting()
    elif st.session_state.current_step == 4:
        show_debate_round()
    elif st.session_state.current_step == 5:
        show_ai_judgment()
    elif st.session_state.current_step == 6:
        show_results()
    
    # 하단 네비게이션
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_step > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
    
    with col2:
        # 실시간 리더보드 미니 뷰
        gamification.show_leaderboard()
    
    with col3:
        if st.session_state.current_step < 6:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.current_step += 1
                st.rerun()


def show_team_setup():
    """Step 1: 팀 구성"""
    st.markdown("## 👥 Step 1: 팀을 구성해요")
    
    collaboration = st.session_state.systems['collaboration']
    gamification = st.session_state.systems['gamification']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚔️ 검사팀")
        collaboration.show_team_dashboard('prosecutor')
        
        # 준비 완료 시 포인트
        if st.button("준비 완료!", key="pros_ready"):
            gamification.award_points('prosecutor', 'team_collaboration', 
                                     "팀 구성 완료!")
    
    with col2:
        st.markdown("### 🛡️ 변호팀")
        collaboration.show_team_dashboard('defender')
        
        if st.button("준비 완료!", key="def_ready"):
            gamification.award_points('defender', 'team_collaboration', 
                                     "팀 구성 완료!")


def show_case_understanding():
    """Step 2: 사건 이해"""
    st.markdown("## 📖 Step 2: 사건을 이해해요")
    
    feedback = st.session_state.systems['feedback']
    
    # 사건 요약 카드 형식
    st.markdown("""
    <div style='background: white; border-radius: 20px; padding: 2rem; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
        <h3 style='color: #667eea;'>📋 오늘의 사건</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 시각적 사건 표현 (인포그래픽 스타일)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **📅 언제?**
        2024년 3월 15일
        점심시간
        """)
    
    with col2:
        st.info("""
        **📍 어디서?**
        2학년 3반 교실
        급식실 근처
        """)
    
    with col3:
        st.info("""
        **👥 누가?**
        가해자: A학생
        피해자: B학생
        목격자: 3명
        """)
    
    # 핵심 쟁점 정리
    st.markdown("### 🎯 핵심 쟁점")
    
    issues = [
        "도시락을 허락 없이 가져간 것이 잘못인가?",
        "'장난'이라는 변명이 정당한가?",
        "피해 보상은 어떻게 해야 하는가?"
    ]
    
    for i, issue in enumerate(issues, 1):
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    border-radius: 10px; padding: 1rem; margin: 0.5rem 0; color: white;'>
            <strong>쟁점 {i}</strong>: {issue}
        </div>
        """, unsafe_allow_html=True)
    
    # 이해도 체크
    if st.checkbox("✅ 사건 내용을 모두 이해했어요!"):
        st.success("훌륭해요! 다음 단계로 넘어가세요.")


def show_debate_round():
    """Step 4: 토론 진행"""
    st.markdown("## 🎤 Step 4: 토론을 시작해요")
    
    timer = st.session_state.systems['timer']
    feedback = st.session_state.systems['feedback']
    gamification = st.session_state.systems['gamification']
    
    # 실시간 타이머
    timer.show_timer_display("debate", 0)  # 실제 경과 시간 필요
    
    # 현재 발언 순서
    current_team = st.radio(
        "현재 발언 팀",
        ["⚔️ 검사팀", "🛡️ 변호팀"],
        horizontal=True,
        key="current_speaker_team"
    )
    
    # 음성 녹음 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎙️ 발언 녹음")
        
        # 음성 녹음 위젯 (실제 구현 필요)
        if st.button("🔴 녹음 시작", use_container_width=True):
            st.info("녹음 중... 🎙️")
        
        # 텍스트 입력 대안
        speech_text = st.text_area(
            "또는 텍스트로 입력하세요",
            height=150,
            placeholder="여기에 발언 내용을 입력하세요..."
        )
        
        # 실시간 품질 피드백
        if speech_text:
            feedback.show_speech_quality_indicator(speech_text)
    
    with col2:
        st.markdown("### 💡 발언 도우미")
        
        # 실시간 힌트
        hints = [
            "🎯 결론을 먼저 말하세요",
            "📊 구체적 증거를 제시하세요",
            "💎 가치어를 사용하세요",
            "🔄 상대 주장을 반박하세요"
        ]
        
        for hint in hints:
            st.info(hint)
        
        # 남은 시간 경고
        st.warning("⏰ 2분 남았어요!")


def show_results():
    """Step 6: 결과 확인"""
    st.markdown("## 🏆 Step 6: 결과를 확인해요")
    
    gamification = st.session_state.systems['gamification']
    
    # 승리 팀 발표 (애니메이션 효과)
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 20px; padding: 2rem; text-align: center; color: white;
                animation: pulse 1s infinite;'>
        <h1>🎊 변호팀 승리! 🎊</h1>
        <p style='font-size: 1.5rem;'>82점 vs 75점</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 개인 수상
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: gold; border-radius: 15px; padding: 1rem; 
                    text-align: center;'>
            <h3>🥇 최우수 발언자</h3>
            <p>변호팀 김민수</p>
            <small>논리적 구성 우수</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: silver; border-radius: 15px; padding: 1rem; 
                    text-align: center;'>
            <h3>🥈 우수 발언자</h3>
            <p>검사팀 이지은</p>
            <small>효과적 반박</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: #CD7F32; border-radius: 15px; padding: 1rem; 
                    text-align: center;'>
            <h3>🥉 장려상</h3>
            <p>변호팀 박서준</p>
            <small>가치어 활용</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 성장 그래프
    st.markdown("### 📈 나의 성장")
    
    # 레이더 차트 (실제 구현 시 plotly 활용)
    st.info("""
    논리성: ⭐⭐⭐⭐☆
    증거력: ⭐⭐⭐☆☆
    표현력: ⭐⭐⭐⭐⭐
    팀워크: ⭐⭐⭐⭐☆
    """)
    
    # 다음 수업 미션
    st.markdown("### 🎯 다음 수업 미션")
    missions = [
        "🔍 구체적 증거 3개 이상 준비하기",
        "💬 가치어 5개 이상 사용하기",
        "🤝 팀원과 역할 바꿔보기"
    ]
    
    for mission in missions:
        st.checkbox(mission, key=f"mission_{mission}")
    
    # 공유 버튼
    if st.button("📱 결과 공유하기", use_container_width=True):
        st.success("결과가 클립보드에 복사되었어요!")


# 메인 실행
def main():
    setup_page()
    initialize_session()
    
    # 온보딩 또는 메인 앱
    if st.session_state.get('show_onboarding', True):
        show_onboarding()
        if st.button("시작하기!", type="primary"):
            st.session_state.show_onboarding = False
            st.rerun()
    else:
        if st.session_state.app_mode == 'simple':
            run_simple_mode()
        else:
            # 기존 고급 모드 실행
            pass


if __name__ == "__main__":
    import time
    main()