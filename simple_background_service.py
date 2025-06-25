#!/usr/bin/env python3
"""
간단한 백그라운드 서비스 - 핫키 기반 화면 캡처 및 AI 분석

tkinter 없이 터미널 기반으로 작동하는 백그라운드 서비스입니다.
"""

import os
import sys
import time
import threading
import json
from datetime import datetime
from pathlib import Path

import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

from screen_assistant import ScreenAssistant


class SimpleBackgroundService:
    """터미널 기반 백그라운드 서비스"""
    
    def __init__(self):
        self.console = Console()
        self.assistant = ScreenAssistant()
        self.is_running = False
        self.hotkey_combination = "ctrl+shift+a"  # 기본 핫키
        self.config_file = Path("config.json")
        self.activity_log = []
        
        # 설정 로드
        self.load_config()
        
    def load_config(self):
        """설정 파일 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.hotkey_combination = config.get('hotkey', 'ctrl+shift+a')
                    self.console.print(f"[green]✅ 설정 로드됨: 핫키 = {self.hotkey_combination}[/green]")
            else:
                self.save_config()
        except Exception as e:
            self.console.print(f"[yellow]⚠️ 설정 로드 실패, 기본값 사용: {e}[/yellow]")
    
    def save_config(self):
        """설정 파일 저장"""
        try:
            config = {
                'hotkey': self.hotkey_combination,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]❌ 설정 저장 실패: {e}[/red]")
    
    def add_log(self, message):
        """활동 로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)
        
        # 로그가 너무 많으면 오래된 것 삭제
        if len(self.activity_log) > 20:
            self.activity_log.pop(0)
    
    def create_status_table(self):
        """상태 테이블 생성"""
        table = Table(title="🎯 스마트 코딩 어시스턴트 상태")
        
        table.add_column("항목", style="cyan", no_wrap=True)
        table.add_column("상태", style="magenta")
        
        # 서비스 상태
        status = "🟢 실행 중" if self.is_running else "⏸️ 중지됨"
        table.add_row("서비스", status)
        
        # 핫키
        table.add_row("핫키", f"🔥 {self.hotkey_combination}")
        
        # API 키 상태
        openai_status = "✅" if os.getenv("OPENAI_API_KEY") else "❌"
        anthropic_status = "✅" if os.getenv("ANTHROPIC_API_KEY") else "❌"
        table.add_row("OpenAI API", openai_status)
        table.add_row("Anthropic API", anthropic_status)
        
        return table
    
    def create_log_panel(self):
        """로그 패널 생성"""
        log_text = "\n".join(self.activity_log[-10:]) if self.activity_log else "로그가 없습니다."
        return Panel(log_text, title="📋 최근 활동", border_style="blue")
    
    def create_help_panel(self):
        """도움말 패널 생성"""
        help_text = """
[bold]사용 가능한 명령어:[/bold]

• [cyan]start[/cyan] - 서비스 시작
• [cyan]stop[/cyan] - 서비스 중지  
• [cyan]hotkey <키조합>[/cyan] - 핫키 변경 (예: hotkey alt+space)
• [cyan]capture[/cyan] - 수동 화면 캡처
• [cyan]status[/cyan] - 상태 새로고침
• [cyan]help[/cyan] - 도움말 표시
• [cyan]quit[/cyan] - 프로그램 종료

[yellow]핫키를 누르면 화면을 캡처하고 AI 분석을 시작합니다![/yellow]
"""
        return Panel(help_text, title="💡 도움말", border_style="green")
    
    def start_service(self):
        """서비스 시작"""
        if self.is_running:
            self.add_log("서비스가 이미 실행 중입니다.")
            return
        
        try:
            # 핫키 등록
            keyboard.add_hotkey(self.hotkey_combination, self.on_hotkey_pressed)
            
            self.is_running = True
            self.add_log(f"서비스 시작됨 (핫키: {self.hotkey_combination})")
            
        except Exception as e:
            self.add_log(f"서비스 시작 실패: {e}")
    
    def stop_service(self):
        """서비스 중지"""
        if not self.is_running:
            self.add_log("서비스가 이미 중지되어 있습니다.")
            return
        
        try:
            # 핫키 해제
            keyboard.remove_hotkey(self.hotkey_combination)
            
            self.is_running = False
            self.add_log("서비스 중지됨")
            
        except Exception as e:
            self.add_log(f"서비스 중지 실패: {e}")
    
    def change_hotkey(self, new_hotkey):
        """핫키 변경"""
        old_hotkey = self.hotkey_combination
        
        # 서비스가 실행 중이면 중지
        was_running = self.is_running
        if was_running:
            self.stop_service()
        
        self.hotkey_combination = new_hotkey
        self.save_config()
        
        # 서비스가 실행 중이었으면 다시 시작
        if was_running:
            self.start_service()
        
        self.add_log(f"핫키 변경: {old_hotkey} → {new_hotkey}")
    
    def on_hotkey_pressed(self):
        """핫키가 눌렸을 때 호출되는 함수"""
        self.add_log("핫키 감지됨! 프롬프트 입력 요청...")
        
        # 별도 스레드에서 처리
        threading.Thread(
            target=self.handle_hotkey_capture, 
            daemon=True
        ).start()
    
    def handle_hotkey_capture(self):
        """핫키 캡처 처리"""
        try:
            # 간단한 프롬프트 (실제로는 더 정교한 입력 방식 필요)
            prompt = "이 화면의 문제를 해결하는 코드를 작성해주세요"
            
            self.add_log(f"분석 시작: {prompt[:30]}...")
            self.assistant.process_request(prompt)
            self.add_log("분석 완료!")
            
        except Exception as e:
            self.add_log(f"분석 실패: {e}")
    
    def manual_capture(self):
        """수동 캡처"""
        try:
            self.console.print("\n[cyan]프롬프트를 입력하세요:[/cyan]")
            prompt = input("💬 ").strip()
            
            if prompt:
                self.add_log(f"수동 분석 시작: {prompt[:30]}...")
                threading.Thread(
                    target=self.assistant.process_request,
                    args=(prompt,),
                    daemon=True
                ).start()
            else:
                self.add_log("프롬프트가 입력되지 않았습니다.")
                
        except Exception as e:
            self.add_log(f"수동 캡처 실패: {e}")
    
    def run_interactive(self):
        """대화형 모드 실행"""
        self.console.print(Panel(
            "[bold]🎯 스마트 코딩 어시스턴트 백그라운드 서비스[/bold]\n\n"
            "터미널 기반 백그라운드 서비스가 시작되었습니다.\n"
            "'help' 명령어로 사용법을 확인하세요.",
            title="Background Service",
            border_style="cyan"
        ))
        
        self.add_log("프로그램 시작됨")
        
        try:
            while True:
                # 상태 표시
                self.console.print("\n" + "="*60)
                self.console.print(self.create_status_table())
                self.console.print(self.create_log_panel())
                
                # 명령어 입력
                self.console.print("\n[cyan]명령어를 입력하세요 (help: 도움말):[/cyan]")
                command = input("🎯 ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "start":
                    self.start_service()
                elif command == "stop":
                    self.stop_service()
                elif command.startswith("hotkey "):
                    new_hotkey = command[7:].strip()
                    if new_hotkey:
                        self.change_hotkey(new_hotkey)
                    else:
                        self.add_log("핫키를 입력해주세요. 예: hotkey alt+space")
                elif command == "capture":
                    self.manual_capture()
                elif command == "status":
                    self.add_log("상태 새로고침됨")
                elif command == "help":
                    self.console.print(self.create_help_panel())
                else:
                    self.add_log(f"알 수 없는 명령어: {command}")
                
        except KeyboardInterrupt:
            pass
        finally:
            if self.is_running:
                self.stop_service()
            self.console.print("\n[bold]👋 프로그램을 종료합니다.[/bold]")


def main():
    """메인 실행 함수"""
    try:
        service = SimpleBackgroundService()
        service.run_interactive()
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
