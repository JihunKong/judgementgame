# 🎓 AI 판사 모의재판 시스템

금천중학교 특별 수업용 AI 모의재판 시스템입니다.

## 🌟 주요 기능

### 교육적 기능
- 🎤 실시간 음성 인식 (한국어/영어)
- 🤖 AI 판사의 공정한 판결과 피드백
- 📊 팀별 점수 및 레벨 시스템
- 🏆 게이미피케이션 요소 (뱃지, 콤보, 레벨업)

### 수업 최적화
- ⏱️ 50분 수업에 최적화된 타임라인
- 📱 모바일/태블릿 반응형 디자인
- 💾 세션 저장 및 불러오기
- 📚 다양한 샘플 사건 제공

## 🚀 버전 선택 가이드

### ⭐ **app_simple.py** - 경량 버전 (추천!)
```bash
streamlit run app_simple.py
```
- ✅ **즉각적인 응답** (지연 없음)
- ✅ **텍스트 입력 중심** (100% 정확도)
- ✅ **GPT-3.5 사용** (빠른 판결, 저렴한 비용)
- ✅ **50분 수업에 최적화**
- ✅ **안정적 작동 보장**

### 🎮 **app.py** - 풀 버전
```bash
streamlit run app.py
```
- 게이미피케이션 시스템 (포인트, 레벨, 뱃지)
- 음성 인식 지원 (5-10초 처리 시간)
- 상세한 분석 및 피드백
- 고급 기능 포함

### ⚡ **browser_speech.py** - 브라우저 음성 인식
```bash
streamlit run browser_speech.py
```
- 실시간 음성 인식 (Web Speech API)
- 서버 부담 없음 (무료)
- Chrome/Edge에서 최적 작동

## 🚀 빠른 시작

### 1. Streamlit Cloud 배포 (권장)

1. GitHub에 Push
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. New app → Repository 연결
4. Secrets 설정:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

### 2. 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
echo "OPENAI_API_KEY=sk-your-key" > .env

# 실행 (버전 선택)
streamlit run app_simple.py  # 추천!
# 또는
streamlit run app.py  # 풀 버전
```

## 📖 사용법

### 교사용
1. **사전 준비** (5분)
   - 앱 접속 및 사건 선택
   - 팀 구성 확인

2. **토론 진행** (35분)
   - 라운드별 발언 입력
   - 실시간 피드백 확인
   - 포인트 및 뱃지 획득

3. **판결 및 평가** (10분)
   - AI 판결 생성
   - 결과 분석 및 저장

### 학생용
1. 팀 배정 확인
2. 사건 내용 숙지
3. 음성 또는 텍스트로 발언
4. 실시간 포인트 확인
5. AI 판결 및 피드백 확인

## 🎮 게이미피케이션

### 포인트 시스템
- 첫 발언: +10점
- 논리적 반박: +15점
- 증거 제시: +20점
- 창의적 주장: +25점
- 가치어 사용: +5점

### 레벨 시스템
1. 🌱 법정 신입생 (0-50점)
2. 📚 주니어 변호사 (51-150점)
3. ⚖️ 시니어 변호사 (151-300점)
4. 🌟 에이스 변호사 (301-500점)
5. 👑 전설의 변호사 (501점+)

### 뱃지
- 🔥 불꽃 변론가: 3회 연속 발언
- 🎯 저격수: 핵심 증거로 반박
- 🛡️ 철벽 수비: 3회 반박 방어
- ⚡ 번개 응답: 10초 내 반박
- 🏆 MVP: 라운드 최고 득점

## 📂 프로젝트 구조

```
judgementgame/
├── app.py                 # 풀 버전 (게이미피케이션)
├── app_simple.py         # 경량 버전 (추천!)
├── browser_speech.py     # 브라우저 음성 인식
├── speech_recognition.html # 독립형 음성 인식
├── utils.py              # 유틸리티 함수
├── requirements.txt      # 의존성
├── .streamlit/
│   └── config.toml      # Streamlit 설정
├── TEACHER_GUIDE.md     # 교사용 가이드
├── STUDENT_WORKSHEET.md # 학생 활동지
├── QUICK_START.md       # 빠른 시작 가이드
└── CLAUDE.md           # 개발 가이드
```

## 🔧 기술 스택

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-3.5/4, Whisper
- **Audio**: streamlit-audiorecorder, Web Speech API
- **Deployment**: Streamlit Cloud

## 📱 지원 환경

- ✅ Chrome, Edge (권장)
- ✅ Safari, Firefox
- ✅ 모바일/태블릿
- ⚠️ Internet Explorer (미지원)

## 🆘 문제 해결

### 음성 인식 안 됨
- 마이크 권한 확인
- 조용한 환경에서 재시도
- 텍스트 입력으로 대체

### AI 판결 지연
- 인터넷 연결 확인
- API 키 확인
- 30초 이상 시 새로고침

### 앱 접속 불가
- 브라우저 캐시 삭제
- 다른 브라우저 시도
- URL 재확인

## 🤝 기여

개선 제안이나 버그 리포트는 Issues에 등록해주세요.

## 📄 라이선스

교육 목적으로 자유롭게 사용 가능합니다.

## 👨‍🏫 문의

금천중학교 신세령 교사

---

**Made with ❤️ for Geumcheon Middle School Students**