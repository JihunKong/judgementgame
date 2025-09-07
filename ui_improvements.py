"""
금천중학교 AI 모의재판 - UX 개선 컴포넌트
중학생 사용자 경험 최적화를 위한 UI 개선 모듈
"""

import streamlit as st
import time
from datetime import datetime, timedelta
import json

class SimplifiedModeUI:
    """단순화된 진행 모드 - 중학생 친화적 단계별 인터페이스"""
    
    def __init__(self):
        self.steps = [
            {"id": 1, "name": "팀 구성", "icon": "👥", "time": 3},
            {"id": 2, "name": "사건 이해", "icon": "📖", "time": 5},
            {"id": 3, "name": "작전 회의", "icon": "💭", "time": 5},
            {"id": 4, "name": "토론 진행", "icon": "🎤", "time": 25},
            {"id": 5, "name": "AI 판결", "icon": "⚖️", "time": 7},
            {"id": 6, "name": "결과 확인", "icon": "🏆", "time": 5}
        ]
        
    def show_progress_header(self, current_step, elapsed_time):
        """진행 상황 헤더 - 시각적으로 명확한 현재 위치 표시"""
        col1, col2, col3 = st.columns([2, 6, 2])
        
        with col1:
            # 남은 시간 표시 (색상 변화)
            remaining = 50 - elapsed_time
            color = "🟢" if remaining > 10 else "🟡" if remaining > 5 else "🔴"
            st.metric(f"{color} 남은 시간", f"{remaining}분")
        
        with col2:
            # 단계별 진행 인디케이터
            progress_html = self._create_step_indicator(current_step)
            st.markdown(progress_html, unsafe_allow_html=True)
        
        with col3:
            # 도움말 버튼
            if st.button("❓ 도움말", key="help_btn"):
                self.show_contextual_help(current_step)
    
    def _create_step_indicator(self, current_step):
        """시각적 단계 표시기 생성"""
        html = "<div style='display: flex; justify-content: space-between; align-items: center;'>"
        
        for step in self.steps:
            if step['id'] < current_step:
                # 완료된 단계
                html += f"""
                <div style='text-align: center; opacity: 0.5;'>
                    <div style='background: #4CAF50; color: white; border-radius: 50%; 
                                width: 40px; height: 40px; display: flex; 
                                align-items: center; justify-content: center; margin: 0 auto;'>
                        ✓
                    </div>
                    <small>{step['name']}</small>
                </div>
                """
            elif step['id'] == current_step:
                # 현재 단계 (애니메이션 효과)
                html += f"""
                <div style='text-align: center;'>
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; border-radius: 50%; width: 50px; height: 50px; 
                                display: flex; align-items: center; justify-content: center; 
                                margin: 0 auto; animation: pulse 2s infinite;'>
                        {step['icon']}
                    </div>
                    <strong>{step['name']}</strong>
                </div>
                """
            else:
                # 미래 단계
                html += f"""
                <div style='text-align: center; opacity: 0.3;'>
                    <div style='background: #E0E0E0; color: #999; border-radius: 50%; 
                                width: 40px; height: 40px; display: flex; 
                                align-items: center; justify-content: center; margin: 0 auto;'>
                        {step['icon']}
                    </div>
                    <small>{step['name']}</small>
                </div>
                """
            
            # 연결선 (마지막 제외)
            if step['id'] < len(self.steps):
                html += "<div style='flex-grow: 1; height: 2px; background: #E0E0E0; margin: 20px 5px;'></div>"
        
        html += "</div>"
        return html
    
    def show_contextual_help(self, current_step):
        """단계별 맞춤 도움말"""
        help_content = {
            1: {
                "title": "팀 구성 단계",
                "tips": [
                    "각자의 강점을 파악하고 역할을 나누세요",
                    "주 발언자, 자료 조사원, 시간 관리자를 정하세요",
                    "팀 이름을 정하면 더 재미있어요!"
                ]
            },
            2: {
                "title": "사건 이해 단계",
                "tips": [
                    "누가, 언제, 어디서, 무엇을, 왜 했는지 파악하세요",
                    "핵심 쟁점을 3개 이내로 정리하세요",
                    "우리 팀의 입장을 명확히 하세요"
                ]
            },
            3: {
                "title": "작전 회의 단계",
                "tips": [
                    "상대팀이 할 수 있는 주장을 예상해보세요",
                    "우리의 핵심 근거 3가지를 준비하세요",
                    "가치어(존중, 배려, 책임 등)를 활용하세요"
                ]
            },
            4: {
                "title": "토론 진행 단계",
                "tips": [
                    "차분하고 명확하게 말하세요",
                    "상대 주장을 잘 듣고 메모하세요",
                    "시간을 지켜가며 발언하세요"
                ]
            },
            5: {
                "title": "AI 판결 단계",
                "tips": [
                    "AI 판사는 논리성과 증거를 중시해요",
                    "가치어 사용 횟수도 평가됩니다",
                    "양팀 모두에게 교육적 피드백을 제공해요"
                ]
            },
            6: {
                "title": "결과 확인 단계",
                "tips": [
                    "승패보다 배운 점이 더 중요해요",
                    "AI 피드백을 잘 읽고 다음에 개선하세요",
                    "팀원들과 서로 격려해주세요"
                ]
            }
        }
        
        step_help = help_content.get(current_step, {})
        with st.expander(f"💡 {step_help.get('title', '도움말')}", expanded=True):
            for tip in step_help.get('tips', []):
                st.info(f"• {tip}")


class GamificationSystem:
    """게이미피케이션 시스템 - 포인트, 배지, 리더보드"""
    
    def __init__(self):
        if 'points' not in st.session_state:
            st.session_state.points = {'prosecutor': 0, 'defender': 0}
        if 'badges' not in st.session_state:
            st.session_state.badges = {'prosecutor': [], 'defender': []}
        if 'achievements' not in st.session_state:
            st.session_state.achievements = []
    
    def award_points(self, team, action, context=""):
        """포인트 부여 및 시각적 피드백"""
        point_values = {
            'first_speak': 10,
            'use_value_word': 5,
            'effective_rebuttal': 15,
            'complete_on_time': 10,
            'team_collaboration': 5,
            'use_evidence': 8,
            'clear_argument': 12
        }
        
        points = point_values.get(action, 0)
        st.session_state.points[team] += points
        
        # 시각적 피드백
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); 
                        border-radius: 20px; padding: 1rem; text-align: center; 
                        animation: slideIn 0.5s;'>
                <h2 style='color: white; margin: 0;'>🎯 +{points} 포인트!</h2>
                <p style='color: white; margin: 0.5rem 0;'>{context}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 효과음 대체 (시각적 효과)
        time.sleep(0.5)
        st.balloons()
        
        # 배지 체크
        self.check_badges(team)
    
    def check_badges(self, team):
        """배지 획득 조건 체크"""
        badges = {
            'speed_demon': {'name': '⚡ 스피드 데몬', 'condition': '30초 내 첫 발언', 'points': 20},
            'value_master': {'name': '💎 가치어 마스터', 'condition': '가치어 5회 사용', 'points': 25},
            'team_player': {'name': '🤝 팀 플레이어', 'condition': '팀원 3회 지원', 'points': 30},
            'evidence_pro': {'name': '📊 증거 전문가', 'condition': '구체적 증거 3개 제시', 'points': 35},
            'logic_king': {'name': '🧠 논리왕', 'condition': '완벽한 논리 구조', 'points': 40}
        }
        
        # 새로운 배지 획득 시
        new_badge = None  # 실제 조건 체크 로직 필요
        if new_badge:
            st.session_state.badges[team].append(new_badge)
            self.show_badge_animation(new_badge)
    
    def show_badge_animation(self, badge):
        """배지 획득 애니메이션"""
        placeholder = st.empty()
        for i in range(3):
            placeholder.markdown(f"""
            <div style='text-align: center; font-size: {20 + i*10}px; 
                        opacity: {0.3 + i*0.3}; transition: all 0.3s;'>
                {badge['name']}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.3)
        
        st.success(f"🎊 새로운 배지 획득! {badge['name']}")
    
    def show_leaderboard(self):
        """실시간 리더보드"""
        st.markdown("""
        <div style='background: white; border-radius: 20px; padding: 1.5rem; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h3 style='text-align: center; color: #667eea;'>🏆 실시간 순위</h3>
        </div>
        """, unsafe_allow_html=True)
        
        teams = [
            {'name': '검사팀', 'score': st.session_state.points['prosecutor'], 'color': '#ff6b6b'},
            {'name': '변호팀', 'score': st.session_state.points['defender'], 'color': '#4ecdc4'}
        ]
        teams.sort(key=lambda x: x['score'], reverse=True)
        
        for idx, team in enumerate(teams):
            medal = ["🥇", "🥈"][idx]
            progress = team['score'] / 200  # 최대 200점 기준
            
            st.markdown(f"""
            <div style='display: flex; align-items: center; margin: 1rem 0;'>
                <div style='font-size: 2rem; margin-right: 1rem;'>{medal}</div>
                <div style='flex-grow: 1;'>
                    <strong>{team['name']}</strong>
                    <div style='background: #f0f0f0; border-radius: 10px; height: 30px; 
                                position: relative; overflow: hidden;'>
                        <div style='background: {team['color']}; width: {progress*100}%; 
                                    height: 100%; border-radius: 10px; transition: width 0.5s;
                                    display: flex; align-items: center; justify-content: center;'>
                            <span style='color: white; font-weight: bold;'>{team['score']}점</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


class TeamCollaborationTools:
    """팀 협업 도구 - 실시간 소통과 역할 분담"""
    
    def __init__(self):
        if 'team_notes' not in st.session_state:
            st.session_state.team_notes = {'prosecutor': [], 'defender': []}
        if 'team_roles' not in st.session_state:
            st.session_state.team_roles = {'prosecutor': {}, 'defender': {}}
    
    def show_team_dashboard(self, team):
        """팀 대시보드 - 한눈에 보는 팀 상태"""
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, 
                    {'#ff6b6b' if team == 'prosecutor' else '#4ecdc4'} 0%, 
                    {'#ff8787' if team == 'prosecutor' else '#44a3aa'} 100%); 
                    border-radius: 20px; padding: 1.5rem; color: white;'>
            <h3>{'⚔️ 검사팀' if team == 'prosecutor' else '🛡️ 변호팀'} 대시보드</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.show_role_assignment(team)
        
        with col2:
            self.show_team_checklist(team)
        
        with col3:
            self.show_quick_notes(team)
    
    def show_role_assignment(self, team):
        """역할 분담 시스템"""
        st.markdown("### 👥 역할 분담")
        
        roles = {
            'main_speaker': {'title': '주 발언자', 'desc': '핵심 주장 전달', 'icon': '🎤'},
            'researcher': {'title': '자료 조사원', 'desc': '증거와 사례 찾기', 'icon': '🔍'},
            'rebuttal_expert': {'title': '반박 전문가', 'desc': '상대 주장 분석', 'icon': '🛡️'},
            'timekeeper': {'title': '시간 관리자', 'desc': '진행 시간 체크', 'icon': '⏰'}
        }
        
        team_members = st.session_state.student_names[team]
        
        for role_key, role_info in roles.items():
            selected = st.selectbox(
                f"{role_info['icon']} {role_info['title']}",
                ['미정'] + team_members,
                key=f"role_{team}_{role_key}",
                help=role_info['desc']
            )
            
            if selected != '미정':
                st.session_state.team_roles[team][role_key] = selected
                st.caption(f"✅ {selected}님이 담당")
    
    def show_team_checklist(self, team):
        """팀 체크리스트"""
        st.markdown("### 📋 준비 체크리스트")
        
        checklist = [
            {'task': '사건 내용 파악', 'key': f'check1_{team}'},
            {'task': '핵심 주장 3개 정리', 'key': f'check2_{team}'},
            {'task': '예상 반박 준비', 'key': f'check3_{team}'},
            {'task': '가치어 포함', 'key': f'check4_{team}'},
            {'task': '시간 배분 계획', 'key': f'check5_{team}'}
        ]
        
        completed = 0
        for item in checklist:
            if st.checkbox(item['task'], key=item['key']):
                completed += 1
        
        # 진행률 표시
        progress = completed / len(checklist)
        st.progress(progress)
        st.caption(f"완료율: {int(progress * 100)}%")
        
        if progress == 1:
            st.success("🎉 완벽 준비 완료!")
            return 10  # 보너스 포인트
        return 0
    
    def show_quick_notes(self, team):
        """빠른 메모 공유"""
        st.markdown("### 💬 팀 메모")
        
        # 메모 입력
        note = st.text_input(
            "빠른 메모", 
            key=f"quick_note_{team}",
            placeholder="핵심 포인트나 아이디어를 공유하세요"
        )
        
        if st.button("📝 추가", key=f"add_note_{team}"):
            if note:
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.team_notes[team].append({
                    'time': timestamp,
                    'note': note
                })
                st.success("메모 추가됨!")
        
        # 메모 표시 (최신 3개)
        recent_notes = st.session_state.team_notes[team][-3:]
        for note_item in reversed(recent_notes):
            st.info(f"**{note_item['time']}** - {note_item['note']}")


class SmartTimerSystem:
    """스마트 타이머 - 단계별 시간 관리 및 알림"""
    
    def __init__(self):
        self.time_limits = {
            'total': 50,  # 전체 수업 시간
            'preparation': 10,  # 준비 시간
            'debate': 25,  # 토론 시간
            'judgment': 10,  # 판결 시간
            'review': 5  # 정리 시간
        }
    
    def show_timer_display(self, phase, elapsed_seconds):
        """향상된 타이머 디스플레이"""
        time_limit = self.time_limits.get(phase, 50) * 60  # 분을 초로 변환
        remaining = time_limit - elapsed_seconds
        
        # 시간 포맷팅
        minutes = abs(remaining) // 60
        seconds = abs(remaining) % 60
        
        # 색상 결정
        if remaining > time_limit * 0.5:
            color = "#4CAF50"  # 녹색
            emoji = "🟢"
        elif remaining > time_limit * 0.2:
            color = "#FFC107"  # 노란색
            emoji = "🟡"
        else:
            color = "#F44336"  # 빨간색
            emoji = "🔴"
        
        # 타이머 표시
        st.markdown(f"""
        <div style='background: {color}; border-radius: 15px; padding: 1rem; 
                    text-align: center; color: white;'>
            <h1 style='margin: 0; font-family: "Courier New", monospace;'>
                {emoji} {minutes:02d}:{seconds:02d}
            </h1>
            <p style='margin: 0.5rem 0 0 0;'>{phase} 진행 중</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 시간 경고
        if remaining <= 60 and remaining > 0:
            st.warning("⏰ 1분 남았습니다! 마무리를 준비하세요.")
        elif remaining <= 0:
            st.error("⏱️ 시간 초과! 다음 단계로 넘어가세요.")
        
        return remaining > 0
    
    def get_phase_recommendation(self, elapsed_minutes):
        """현재 시간에 따른 단계 추천"""
        if elapsed_minutes < 10:
            return "preparation", "지금은 준비 시간입니다. 사건을 이해하고 전략을 세우세요."
        elif elapsed_minutes < 35:
            return "debate", "토론 시간입니다. 논리적으로 주장을 펼치세요."
        elif elapsed_minutes < 45:
            return "judgment", "AI 판결 시간입니다. 결과를 기다려주세요."
        else:
            return "review", "정리 시간입니다. 배운 점을 돌아보세요."


class VisualFeedbackSystem:
    """시각적 피드백 시스템 - 실시간 반응과 안내"""
    
    def show_speech_quality_indicator(self, text):
        """발언 품질 실시간 표시"""
        quality_scores = self.analyze_speech_quality(text)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.show_metric_card(
                "논리성", 
                quality_scores['logic'], 
                "주장과 근거의 연결"
            )
        
        with col2:
            self.show_metric_card(
                "구체성",
                quality_scores['specificity'],
                "구체적 사례 포함"
            )
        
        with col3:
            self.show_metric_card(
                "가치어",
                quality_scores['values'],
                "존중, 배려, 책임 등"
            )
        
        with col4:
            self.show_metric_card(
                "명확성",
                quality_scores['clarity'],
                "이해하기 쉬운 표현"
            )
    
    def analyze_speech_quality(self, text):
        """발언 품질 분석"""
        scores = {
            'logic': 0,
            'specificity': 0,
            'values': 0,
            'clarity': 0
        }
        
        if not text:
            return scores
        
        # 논리성 체크 (연결어 사용)
        logic_words = ['왜냐하면', '따라서', '그러므로', '결과적으로', '이유는']
        scores['logic'] = min(sum(1 for word in logic_words if word in text) * 20, 100)
        
        # 구체성 체크 (숫자, 시간, 장소)
        import re
        has_numbers = bool(re.search(r'\d+', text))
        has_time = any(word in text for word in ['시', '분', '날', '월', '년'])
        has_place = any(word in text for word in ['교실', '학교', '운동장', '복도'])
        scores['specificity'] = (has_numbers + has_time + has_place) * 33
        
        # 가치어 체크
        value_words = ['존중', '배려', '책임', '공정', '정의', '협력', '신뢰']
        scores['values'] = min(sum(text.count(word) for word in value_words) * 25, 100)
        
        # 명확성 (문장 길이 기반)
        sentences = text.split('.')
        avg_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        scores['clarity'] = max(0, min(100, 150 - avg_length))
        
        return scores
    
    def show_metric_card(self, title, score, description):
        """메트릭 카드 표시"""
        # 색상 결정
        if score >= 70:
            color = "#4CAF50"
            emoji = "😊"
        elif score >= 40:
            color = "#FFC107"
            emoji = "🤔"
        else:
            color = "#F44336"
            emoji = "😟"
        
        st.markdown(f"""
        <div style='background: white; border-left: 4px solid {color}; 
                    border-radius: 10px; padding: 1rem; margin: 0.5rem 0;'>
            <strong>{title} {emoji}</strong>
            <div style='background: #f0f0f0; border-radius: 5px; height: 10px; 
                        margin: 0.5rem 0; overflow: hidden;'>
                <div style='background: {color}; width: {score}%; height: 100%;'></div>
            </div>
            <small style='color: #666;'>{description}</small>
        </div>
        """, unsafe_allow_html=True)


# CSS 애니메이션 추가
def add_animations():
    """UI 애니메이션 스타일 추가"""
    st.markdown("""
    <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes slideIn {
            0% { 
                opacity: 0; 
                transform: translateY(-20px); 
            }
            100% { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        
        .hover-card {
            transition: all 0.3s ease;
        }
        
        .hover-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .progress-bar {
            animation: slideIn 0.5s ease;
        }
        
        .success-message {
            animation: pulse 0.5s ease;
        }
    </style>
    """, unsafe_allow_html=True)