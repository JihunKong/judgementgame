"""
브라우저 기반 음성 인식 컴포넌트
Web Speech API를 활용한 실시간 음성 인식
"""

import streamlit as st
import streamlit.components.v1 as components

def browser_speech_input(key="speech"):
    """브라우저 음성 인식 컴포넌트"""
    
    # HTML/JS 코드
    speech_html = f"""
    <div id="speech-{key}" style="padding: 20px; background: #f0f0f0; border-radius: 10px;">
        <button id="btn-{key}" onclick="toggleSpeech_{key}()" 
                style="background: #ff6b6b; color: white; border: none; 
                       padding: 12px 24px; border-radius: 20px; 
                       font-size: 16px; cursor: pointer;">
            🎤 음성 입력 시작
        </button>
        <div id="status-{key}" style="margin-top: 10px; color: #666;">준비됨</div>
        <div id="result-{key}" style="margin-top: 15px; padding: 10px; 
                                      background: white; border-radius: 5px; 
                                      min-height: 50px; display: none;"></div>
    </div>
    
    <script>
        const recognition_{key} = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition_{key}.lang = 'ko-KR';
        recognition_{key}.continuous = true;
        recognition_{key}.interimResults = true;
        
        let isRecording_{key} = false;
        let finalText_{key} = '';
        
        function toggleSpeech_{key}() {{
            if (isRecording_{key}) {{
                recognition_{key}.stop();
                document.getElementById('btn-{key}').textContent = '🎤 음성 입력 시작';
                document.getElementById('btn-{key}').style.background = '#ff6b6b';
                document.getElementById('status-{key}').textContent = '준비됨';
                isRecording_{key} = false;
                
                // Streamlit으로 결과 전송
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: finalText_{key}
                }}, '*');
            }} else {{
                finalText_{key} = '';
                recognition_{key}.start();
                document.getElementById('btn-{key}').textContent = '⏹️ 중지';
                document.getElementById('btn-{key}').style.background = '#4ecdc4';
                document.getElementById('status-{key}').textContent = '🎤 듣는 중...';
                document.getElementById('result-{key}').style.display = 'block';
                isRecording_{key} = true;
            }}
        }}
        
        recognition_{key}.onresult = (event) => {{
            let interim = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {{
                    finalText_{key} += transcript + ' ';
                }} else {{
                    interim = transcript;
                }}
            }}
            
            document.getElementById('result-{key}').innerHTML = 
                finalText_{key} + '<span style="color: #999;">' + interim + '</span>';
        }};
        
        recognition_{key}.onerror = (event) => {{
            document.getElementById('status-{key}').textContent = '오류: ' + event.error;
        }};
    </script>
    """
    
    # 컴포넌트 렌더링
    result = components.html(speech_html, height=200)
    return result

# 사용 예제
if __name__ == "__main__":
    st.title("🎙️ 브라우저 음성 인식 테스트")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("검사팀")
        pros_speech = browser_speech_input("prosecutor")
        if pros_speech:
            st.write("인식된 텍스트:", pros_speech)
    
    with col2:
        st.subheader("변호팀")
        def_speech = browser_speech_input("defender")
        if def_speech:
            st.write("인식된 텍스트:", def_speech)