"""
유틸리티 함수 모음
게이미피케이션, 타이머, 피드백 등 핵심 기능
"""

import streamlit as st
import time
from datetime import datetime, timedelta
import json
import random

# 포인트 시스템
POINT_SYSTEM = {
    "첫_발언": 10,
    "논리적_반박": 15,
    "증거_제시": 20,
    "창의적_주장": 25,
    "팀_어시스트": 10,
    "타임_보너스": 5,  # 30초 내 응답
    "가치어_사용": 5,  # 정의, 공정, 책임 등
    "완벽한_시간관리": 10,  # 시간 내 완료
}

# 레벨 시스템
LEVEL_SYSTEM = [
    {"level": 1, "title": "🌱 법정 신입생", "min_points": 0, "max_points": 50},
    {"level": 2, "title": "📚 주니어 변호사", "min_points": 51, "max_points": 150},
    {"level": 3, "title": "⚖️ 시니어 변호사", "min_points": 151, "max_points": 300},
    {"level": 4, "title": "🌟 에이스 변호사", "min_points": 301, "max_points": 500},
    {"level": 5, "title": "👑 전설의 변호사", "min_points": 501, "max_points": 9999},
]

# 뱃지 시스템
BADGES = {
    "fire_speaker": {"icon": "🔥", "name": "불꽃 변론가", "condition": "3회 연속 발언"},
    "sniper": {"icon": "🎯", "name": "저격수", "condition": "핵심 증거로 반박 성공"},
    "defender": {"icon": "🛡️", "name": "철벽 수비", "condition": "3회 반박 방어"},
    "lightning": {"icon": "⚡", "name": "번개 응답", "condition": "10초 내 반박"},
    "mvp": {"icon": "🏆", "name": "MVP", "condition": "라운드 최고 득점"},
    "teamwork": {"icon": "🤝", "name": "팀워크 마스터", "condition": "완벽한 팀 협력"},
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

def init_gamification():
    """게이미피케이션 시스템 초기화"""
    if 'points' not in st.session_state:
        st.session_state.points = {'prosecutor': 0, 'defender': 0}
    if 'badges' not in st.session_state:
        st.session_state.badges = {'prosecutor': [], 'defender': []}
    if 'combo' not in st.session_state:
        st.session_state.combo = {'prosecutor': 0, 'defender': 0}
    if 'speech_count' not in st.session_state:
        st.session_state.speech_count = {'prosecutor': 0, 'defender': 0}

def add_points(team, point_type, amount=None):
    """포인트 추가 및 애니메이션"""
    if amount is None:
        amount = POINT_SYSTEM.get(point_type, 0)
    
    # 콤보 보너스
    if st.session_state.combo[team] >= 3:
        amount = int(amount * 1.5)
        st.balloons()
    
    st.session_state.points[team] += amount
    
    # 시각적 피드백
    st.success(f"🎯 {team} +{amount}점!")
    return amount

def check_badges(team):
    """뱃지 획득 체크"""
    badges_earned = []
    
    # 연속 발언 체크
    if st.session_state.combo[team] >= 3:
        if "fire_speaker" not in st.session_state.badges[team]:
            st.session_state.badges[team].append("fire_speaker")
            badges_earned.append(BADGES["fire_speaker"])
    
    # MVP 체크 (100점 이상)
    if st.session_state.points[team] >= 100:
        if "mvp" not in st.session_state.badges[team]:
            st.session_state.badges[team].append("mvp")
            badges_earned.append(BADGES["mvp"])
    
    return badges_earned

def get_level(points):
    """현재 레벨 확인"""
    for level in LEVEL_SYSTEM:
        if level["min_points"] <= points <= level["max_points"]:
            return level
    return LEVEL_SYSTEM[0]

def create_timer(duration_seconds, key):
    """향상된 타이머 컴포넌트"""
    placeholder = st.empty()
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        remaining = duration_seconds - elapsed
        
        if remaining <= 0:
            placeholder.error("⏰ 시간 종료!")
            st.audio("https://www.soundjay.com/misc/bell-ringing-05.wav")  # 알림음
            break
        
        # 시각적 표시
        progress = elapsed / duration_seconds
        color = "🟢" if progress < 0.5 else "🟡" if progress < 0.8 else "🔴"
        
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        
        placeholder.markdown(f"""
        <div style='text-align: center; font-size: 2rem;'>
            {color} {mins:02d}:{secs:02d}
        </div>
        """, unsafe_allow_html=True)
        
        # 30초 경고
        if remaining <= 30 and remaining > 29:
            st.warning("⚠️ 30초 남았습니다!")
        
        time.sleep(1)

def generate_ai_hint(team, round_num):
    """AI 힌트 생성"""
    hints = {
        "prosecutor": [
            "💡 구체적인 날짜와 시간을 언급하세요",
            "💡 목격자 증언을 활용하세요",
            "💡 규칙 위반의 결과를 강조하세요",
            "💡 피해자의 입장을 설명하세요"
        ],
        "defender": [
            "💡 상황의 맥락을 설명하세요",
            "💡 의도가 없었음을 강조하세요",
            "💡 개선 의지를 보여주세요",
            "💡 합리적인 대안을 제시하세요"
        ]
    }
    
    return random.choice(hints.get(team, []))

def calculate_speech_quality(text):
    """발언 품질 평가"""
    score = 0
    feedback = []
    
    # 길이 체크
    word_count = len(text.split())
    if word_count > 50:
        score += 20
        feedback.append("✅ 충분한 설명")
    else:
        feedback.append("📝 더 자세한 설명 필요")
    
    # 구조 체크
    if any(word in text for word in ["첫째", "둘째", "셋째", "첫 번째", "두 번째"]):
        score += 30
        feedback.append("✅ 체계적인 구조")
    
    # 근거 체크
    if any(word in text for word in ["증거", "목격", "사실", "왜냐하면", "때문"]):
        score += 25
        feedback.append("✅ 근거 제시")
    
    # 가치어 체크
    value_words = ["정의", "공정", "책임", "배려", "존중", "신뢰", "협력"]
    if any(word in text for word in value_words):
        score += 25
        feedback.append("✅ 가치어 사용")
    
    return score, feedback

def create_team_dashboard(team):
    """팀별 대시보드"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        points = st.session_state.points[team]
        level = get_level(points)
        st.metric("점수", f"{points}점", f"{level['title']}")
    
    with col2:
        st.metric("발언 횟수", st.session_state.speech_count[team])
    
    with col3:
        combo = st.session_state.combo[team]
        st.metric("콤보", f"x{combo}", "🔥" if combo >= 3 else "")
    
    with col4:
        badges = st.session_state.badges[team]
        badge_icons = " ".join([BADGES[b]["icon"] for b in badges[:3]])
        st.metric("뱃지", badge_icons if badge_icons else "없음")

def create_versus_display():
    """팀 대결 시각화"""
    pros_points = st.session_state.points['prosecutor']
    def_points = st.session_state.points['defender']
    total = pros_points + def_points + 1  # 0 방지
    
    pros_percent = (pros_points / total) * 100
    def_percent = (def_points / total) * 100
    
    st.markdown(f"""
    <div style='display: flex; height: 40px; border-radius: 20px; overflow: hidden;'>
        <div style='background: linear-gradient(90deg, #ff6b6b, #ff8787); 
                    width: {pros_percent}%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;
                    font-weight: bold;'>
            검사 {pros_points}점
        </div>
        <div style='background: linear-gradient(90deg, #4ecdc4, #44a3aa); 
                    width: {def_percent}%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;
                    font-weight: bold;'>
            변호 {def_points}점
        </div>
    </div>
    """, unsafe_allow_html=True)

def save_session_data():
    """세션 데이터 자동 저장"""
    save_data = {
        "timestamp": datetime.now().isoformat(),
        "case_summary": st.session_state.get('case_summary', ''),
        "rounds": st.session_state.get('rounds', []),
        "points": st.session_state.get('points', {}),
        "badges": st.session_state.get('badges', {}),
        "ai_judgment": st.session_state.get('ai_judgment', '')
    }
    
    # 로컬 스토리지에 저장 (브라우저)
    return json.dumps(save_data, ensure_ascii=False, indent=2)

def load_sample_case(case_index):
    """샘플 사건 불러오기"""
    if 0 <= case_index < len(SAMPLE_CASES):
        case = SAMPLE_CASES[case_index]
        st.session_state.case_summary = case["summary"]
        st.success(f"✅ '{case['title']}' 사건을 불러왔습니다!")
        
        # 힌트 제공
        with st.expander("💡 팀별 전략 힌트"):
            st.write(f"**검사팀 힌트:** {case['prosecutor_hint']}")
            st.write(f"**변호팀 힌트:** {case['defender_hint']}")
        
        return True
    return False

def create_quick_feedback(text, team):
    """즉각적인 AI 피드백 (간단한 규칙 기반)"""
    score, feedback = calculate_speech_quality(text)
    
    # 즉시 피드백 표시
    if score >= 80:
        st.success(f"🌟 훌륭한 발언입니다! (+{score}점)")
        add_points(team, "창의적_주장")
    elif score >= 60:
        st.info(f"👍 좋은 발언입니다! (+{score//2}점)")
        add_points(team, "논리적_반박", score//2)
    else:
        st.warning(f"💭 더 발전시킬 수 있어요! (+10점)")
        add_points(team, "첫_발언")
    
    # 상세 피드백
    for fb in feedback:
        st.write(fb)
    
    # 개선 제안
    if score < 80:
        hint = generate_ai_hint(team, st.session_state.get('current_round', 1))
        st.info(hint)
    
    return score

def format_time_korean(seconds):
    """한국어 시간 형식"""
    if seconds < 60:
        return f"{int(seconds)}초"
    else:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}분 {secs}초"