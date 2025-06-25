#!/usr/bin/env python3
"""
웹 기반 떠다니는 코딩 어시스턴트

Flask 웹 인터페이스로 구현된 GUI 챗봇입니다.
Ctrl+R 핫키로 화면 캡처 및 AI 분석을 제공합니다.
"""

import os
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import json

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
import keyboard
from rich.console import Console

from screen_assistant import ScreenAssistant


class WebAssistant:
    """웹 기반 코딩 어시스턴트"""
    
    def __init__(self):
        self.console = Console()
        self.assistant = ScreenAssistant()
        self.is_service_running = False
        self.hotkey = "ctrl+r"
        self.chat_history = []
        
        # Flask 앱 설정
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'smart_coding_assistant_2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 라우트 설정
        self.setup_routes()
        self.setup_socketio_events()
        
        # 설정 로드
        self.load_settings()
        
        # 초기 메시지
        self.add_message("🤖 안녕하세요! 스마트 코딩 어시스턴트입니다.", "assistant")
        self.add_message(f"🔥 {self.hotkey.upper()}를 눌러 화면을 분석해보세요!", "assistant")
    
    def load_settings(self):
        """설정 로드"""
        try:
            config_file = Path("web_assistant_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.hotkey = config.get('hotkey', 'ctrl+r')
        except Exception as e:
            self.console.print(f"[yellow]⚠️ 설정 로드 실패: {e}[/yellow]")
    
    def save_settings(self):
        """설정 저장"""
        try:
            config = {
                'hotkey': self.hotkey,
                'last_updated': datetime.now().isoformat()
            }
            
            with open("web_assistant_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]❌ 설정 저장 실패: {e}[/red]")
    
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
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'service_running': self.is_service_running,
                'hotkey': self.hotkey,
                'openai_api': bool(os.getenv("OPENAI_API_KEY")),
                'anthropic_api': bool(os.getenv("ANTHROPIC_API_KEY"))
            })
        
        @self.app.route('/api/chat_history')
        def get_chat_history():
            return jsonify(self.chat_history)
        
        @self.app.route('/api/start_service', methods=['POST'])
        def start_service():
            try:
                self.start_hotkey_service()
                return jsonify({'success': True, 'message': '서비스가 시작되었습니다.'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/stop_service', methods=['POST'])
        def stop_service():
            try:
                self.stop_hotkey_service()
                return jsonify({'success': True, 'message': '서비스가 중지되었습니다.'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/change_hotkey', methods=['POST'])
        def change_hotkey():
            try:
                new_hotkey = request.json.get('hotkey', '').strip()
                if new_hotkey:
                    self.change_hotkey_setting(new_hotkey)
                    return jsonify({'success': True, 'message': f'핫키가 {new_hotkey.upper()}로 변경되었습니다.'})
                else:
                    return jsonify({'success': False, 'message': '유효한 핫키를 입력해주세요.'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/manual_capture', methods=['POST'])
        def manual_capture():
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
                'service_running': self.is_service_running,
                'hotkey': self.hotkey
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
    
    def start_hotkey_service(self):
        """핫키 서비스 시작"""
        if self.is_service_running:
            return
        
        try:
            keyboard.add_hotkey(self.hotkey, self.on_hotkey_pressed)
            self.is_service_running = True
            self.add_message(f"서비스가 시작되었습니다! {self.hotkey.upper()}를 눌러보세요.", "assistant")
            
            # 상태 업데이트 전송
            self.socketio.emit('status_update', {
                'service_running': self.is_service_running,
                'hotkey': self.hotkey
            })
            
        except Exception as e:
            self.add_message(f"서비스 시작 실패: {e}", "assistant")
            raise e
    
    def stop_hotkey_service(self):
        """핫키 서비스 중지"""
        if not self.is_service_running:
            return
        
        try:
            keyboard.remove_hotkey(self.hotkey)
            self.is_service_running = False
            self.add_message("서비스가 중지되었습니다.", "assistant")
            
            # 상태 업데이트 전송
            self.socketio.emit('status_update', {
                'service_running': self.is_service_running,
                'hotkey': self.hotkey
            })
            
        except Exception as e:
            self.add_message(f"서비스 중지 실패: {e}", "assistant")
            raise e
    
    def change_hotkey_setting(self, new_hotkey):
        """핫키 변경"""
        was_running = self.is_service_running
        if was_running:
            self.stop_hotkey_service()
        
        self.hotkey = new_hotkey
        self.save_settings()
        
        if was_running:
            self.start_hotkey_service()
        
        self.add_message(f"핫키가 {new_hotkey.upper()}로 변경되었습니다.", "assistant")
    
    def on_hotkey_pressed(self):
        """핫키가 눌렸을 때"""
        self.add_message("🔥 핫키 감지! 화면을 캡처하고 분석 중...", "assistant")
        
        threading.Thread(
            target=self.process_screen_capture,
            args=("이 화면을 분석하고 코딩 관련 조언이나 문제 해결 방법을 제공해주세요.",),
            daemon=True
        ).start()
    
    def process_screen_capture(self, prompt):
        """화면 캡처 및 분석"""
        try:
            # 화면 캡처
            image_path = self.assistant.capture_screen()
            if not image_path:
                self.add_message("화면 캡처에 실패했습니다.", "assistant")
                return
            
            # AI 분석
            result = self.assistant.analyze_screen_with_prompt(image_path, prompt)
            
            self.add_message("📸 화면 분석 완료!", "assistant")
            self.add_message(result, "assistant")
            
        except Exception as e:
            self.add_message(f"분석 중 오류 발생: {e}", "assistant")
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """웹 서버 실행"""
        self.console.print(f"[bold cyan]🌐 웹 기반 코딩 어시스턴트 시작![/bold cyan]")
        self.console.print(f"[green]URL: http://{host}:{port}[/green]")
        self.console.print(f"[green]핫키: {self.hotkey.upper()}[/green]")
        
        # 브라우저 자동 열기
        if not debug:
            threading.Timer(1.5, lambda: webbrowser.open(f'http://{host}:{port}')).start()
        
        # 웹 서버 실행
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """메인 실행 함수"""
    try:
        assistant = WebAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
