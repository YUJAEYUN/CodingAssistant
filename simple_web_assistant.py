#!/usr/bin/env python3
"""
간단한 웹 기반 코딩 어시스턴트 (권한 문제 해결 버전)

핫키 없이 수동 캡처만 지원하는 버전입니다.
"""

import os
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import json
import base64

# 환경변수 로드
def load_env():
    """환경변수 로드"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import pyautogui
import anthropic
from rich.console import Console


class SimpleWebAssistant:
    """간단한 웹 기반 코딩 어시스턴트"""
    
    def __init__(self):
        self.console = Console()
        self.chat_history = []
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Flask 앱 설정
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'simple_assistant_2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 라우트 설정
        self.setup_routes()
        self.setup_socketio_events()
        
        # 초기 메시지
        self.add_message("🤖 안녕하세요! 간단한 코딩 어시스턴트입니다.", "assistant")
        self.add_message("📸 '캡처' 버튼을 눌러 화면을 분석해보세요!", "assistant")
    
    def add_message(self, message, sender="user"):
        """메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg_data = {
            "timestamp": timestamp,
            "sender": sender,
            "message": message
        }
        self.chat_history.append(msg_data)
        
        # 최대 50개 메시지만 유지
        if len(self.chat_history) > 50:
            self.chat_history.pop(0)
        
        # 웹 클라이언트에 실시간 전송
        self.socketio.emit('new_message', msg_data)
    
    def setup_routes(self):
        """Flask 라우트 설정"""
        
        @self.app.route('/')
        def index():
            return render_template('simple_index.html')
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'anthropic_api': bool(os.getenv("ANTHROPIC_API_KEY"))
            })
        
        @self.app.route('/api/chat_history')
        def get_chat_history():
            return jsonify(self.chat_history)
        
        @self.app.route('/api/capture', methods=['POST'])
        def capture_screen():
            try:
                prompt = request.json.get('prompt', '이 화면을 분석하고 코딩 관련 조언을 제공해주세요.')
                threading.Thread(
                    target=self.process_screen_capture,
                    args=(prompt,),
                    daemon=True
                ).start()
                return jsonify({'success': True, 'message': '화면 캡처를 시작했습니다.'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
    
    def setup_socketio_events(self):
        """SocketIO 이벤트 설정"""
        
        @self.socketio.on('connect')
        def handle_connect():
            emit('status_update', {
                'anthropic_api': bool(os.getenv("ANTHROPIC_API_KEY"))
            })
        
        @self.socketio.on('send_message')
        def handle_message(data):
            user_message = data.get('message', '').strip()
            if user_message:
                self.add_message(user_message, "user")
                
                # 화면 캡처 + 사용자 프롬프트로 분석
                self.add_message("화면을 캡처하고 분석 중...", "assistant")
                threading.Thread(
                    target=self.process_screen_capture,
                    args=(user_message,),
                    daemon=True
                ).start()
    
    def capture_screen(self):
        """화면 캡처"""
        try:
            # 화면 캡처
            screenshot = pyautogui.screenshot()
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            # 이미지 저장
            screenshot.save(filepath)
            
            self.console.print(f"[green]📸 화면 캡처 완료: {filepath}[/green]")
            return str(filepath)
            
        except Exception as e:
            self.console.print(f"[red]❌ 화면 캡처 실패: {e}[/red]")
            return None
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """이미지를 base64로 인코딩"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.console.print(f"[red]❌ 이미지 인코딩 실패: {e}[/red]")
            return ""
    
    def analyze_screen_with_ai(self, image_path: str, user_prompt: str) -> str:
        """AI로 화면 분석"""
        try:
            # 이미지를 base64로 인코딩
            image_base64 = self.encode_image_to_base64(image_path)
            if not image_base64:
                return "이미지 처리에 실패했습니다."
            
            # AI 분석 프롬프트 구성
            system_prompt = """
당신은 화면을 보고 코딩 문제를 해결하는 전문 AI 어시스턴트입니다.

사용자가 제공한 화면 스크린샷과 프롬프트를 분석하여:
1. 화면에 표시된 내용을 정확히 파악
2. 코드 에러, UI 문제, 또는 개발 이슈 식별
3. 사용자 프롬프트와 화면 내용을 결합하여 문제 해결
4. 실행 가능한 코드나 해결책 제공

응답 형식:
## 📋 화면 분석
[화면에서 발견한 내용 설명]

## 🎯 문제 식별
[발견된 문제나 이슈]

## 💡 해결 방안
[구체적인 해결 방법]

## 💻 코드 솔루션
```python
# 실행 가능한 코드 제공
```

## 📝 추가 설명
[필요한 경우 추가 설명]
"""
            
            user_message = f"""
사용자 프롬프트: {user_prompt}

첨부된 화면 스크린샷을 분석하고, 사용자의 요청과 결합하여 문제를 해결해주세요.
"""

            # Anthropic 클라이언트 사용
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_message
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.console.print(f"[red]❌ AI 분석 실패: {e}[/red]")
            return f"AI 분석 중 오류가 발생했습니다: {e}"
    
    def process_screen_capture(self, prompt):
        """화면 캡처 및 분석"""
        try:
            # 화면 캡처
            image_path = self.capture_screen()
            if not image_path:
                self.add_message("화면 캡처에 실패했습니다.", "assistant")
                return
            
            # AI 분석
            result = self.analyze_screen_with_ai(image_path, prompt)
            
            self.add_message("📸 화면 분석 완료!", "assistant")
            self.add_message(result, "assistant")
            
            # 결과를 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = self.screenshots_dir / f"analysis_{timestamp}.md"
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"# 화면 분석 결과\n\n")
                f.write(f"**시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**프롬프트**: {prompt}\n")
                f.write(f"**이미지**: {image_path}\n\n")
                f.write(result)
            
            self.console.print(f"[green]💾 결과 저장됨: {result_file}[/green]")
            
        except Exception as e:
            self.add_message(f"분석 중 오류 발생: {e}", "assistant")
    
    def run(self, host='127.0.0.1', port=8080, debug=False):
        """웹 서버 실행"""
        self.console.print(f"[bold cyan]🌐 간단한 웹 기반 코딩 어시스턴트 시작![/bold cyan]")
        self.console.print(f"[green]URL: http://{host}:{port}[/green]")
        self.console.print(f"[yellow]핫키 없이 수동 캡처만 지원합니다.[/yellow]")
        
        # 브라우저 자동 열기
        if not debug:
            threading.Timer(1.5, lambda: webbrowser.open(f'http://{host}:{port}')).start()
        
        # 웹 서버 실행
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """메인 실행 함수"""
    try:
        assistant = SimpleWebAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
