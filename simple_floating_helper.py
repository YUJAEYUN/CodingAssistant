#!/usr/bin/env python3
"""
간단한 떠다니는 코딩 도우미 (권한 문제 없음)

수동 캡처만 지원하는 간단한 버전입니다.
"""

import os
import sys
import threading
import time
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

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
except ImportError:
    print("❌ tkinter가 설치되지 않았습니다.")
    print("macOS에서는 다음 명령어로 설치하세요:")
    print("brew install python-tk")
    sys.exit(1)

import pyautogui
import openai
import anthropic
from rich.console import Console
from PIL import Image, ImageTk


class SimpleFloatingHelper:
    """간단한 떠다니는 코딩 도우미"""
    
    def __init__(self):
        self.console = Console()
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # AI 클라이언트 설정
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # GUI 설정
        self.setup_gui()
        
        # 설정 로드
        self.load_settings()
    
    def setup_gui(self):
        """GUI 설정"""
        self.root = tk.Tk()
        self.root.title("🤖 코딩 도우미")
        
        # 작은 크기로 설정
        self.root.geometry("220x140")
        
        # 항상 위에 표시
        self.root.attributes('-topmost', True)
        
        # 창 스타일 설정 (macOS)
        try:
            self.root.attributes('-alpha', 0.9)  # 약간 투명
        except:
            pass
        
        # 배경색 설정
        self.root.configure(bg='#2c3e50')
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 아이콘 및 제목
        title_label = tk.Label(
            main_frame,
            text="🤖 코딩 도우미",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=(0, 5))
        
        # 상태 표시
        self.status_label = tk.Label(
            main_frame,
            text="✅ 준비됨",
            font=("Arial", 9),
            fg="#2ecc71",
            bg="#2c3e50"
        )
        self.status_label.pack(pady=(0, 5))
        
        # 안내 메시지
        info_label = tk.Label(
            main_frame,
            text="📸 버튼으로 캡처",
            font=("Arial", 8),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        info_label.pack(pady=(0, 8))
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.pack(fill=tk.X)
        
        # 캡처 버튼 (큰 버튼)
        capture_btn = tk.Button(
            button_frame,
            text="📸 캡처",
            font=("Arial", 11, "bold"),
            command=self.manual_capture,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            height=2
        )
        capture_btn.pack(fill=tk.X, pady=(0, 5))
        
        # 작은 버튼들
        small_button_frame = tk.Frame(button_frame, bg="#2c3e50")
        small_button_frame.pack(fill=tk.X)
        
        # 설정 버튼
        settings_btn = tk.Button(
            small_button_frame,
            text="⚙️",
            font=("Arial", 9),
            command=self.show_info,
            bg="#34495e",
            fg="white",
            relief=tk.FLAT,
            width=4
        )
        settings_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 종료 버튼
        quit_btn = tk.Button(
            small_button_frame,
            text="❌",
            font=("Arial", 9),
            command=self.quit_app,
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            width=4
        )
        quit_btn.pack(side=tk.RIGHT)
        
        # 드래그 가능하게 만들기
        self.make_draggable()
        
        # 창 닫기 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def make_draggable(self):
        """창을 드래그 가능하게 만들기"""
        def start_drag(event):
            self.root.x = event.x
            self.root.y = event.y
        
        def drag(event):
            x = self.root.winfo_pointerx() - self.root.x
            y = self.root.winfo_pointery() - self.root.y
            self.root.geometry(f"+{x}+{y}")
        
        # 모든 위젯에 드래그 이벤트 바인딩
        def bind_drag(widget):
            widget.bind("<Button-1>", start_drag)
            widget.bind("<B1-Motion>", drag)
            for child in widget.winfo_children():
                if isinstance(child, (tk.Label, tk.Frame)):
                    bind_drag(child)
        
        bind_drag(self.root)
    
    def load_settings(self):
        """설정 로드"""
        try:
            config_file = Path("simple_helper_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # 창 위치 복원
                    if 'window_position' in config:
                        x, y = config['window_position']
                        self.root.geometry(f"220x140+{x}+{y}")
        except Exception as e:
            self.console.print(f"[yellow]⚠️ 설정 로드 실패: {e}[/yellow]")
    
    def save_settings(self):
        """설정 저장"""
        try:
            # 현재 창 위치 가져오기
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            
            config = {
                'window_position': [x, y],
                'last_updated': datetime.now().isoformat()
            }
            
            with open("simple_helper_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]❌ 설정 저장 실패: {e}[/red]")
    
    def manual_capture(self):
        """수동 캡처"""
        self.console.print("[yellow]📸 수동 캡처 시작...[/yellow]")
        
        # 상태 업데이트
        self.status_label.config(text="📸 캡처 중...", fg="#f39c12")
        self.root.update()
        
        # 별도 스레드에서 처리
        threading.Thread(target=self.process_capture, daemon=True).start()
    
    def process_capture(self):
        """캡처 처리"""
        try:
            # 화면 캡처
            image_path = self.capture_screen()
            if not image_path:
                self.root.after(0, lambda: self.status_label.config(text="❌ 캡처 실패", fg="#e74c3c"))
                return
            
            # 사용자 입력 받기
            self.root.after(0, self.ask_user_input, image_path)
            
        except Exception as e:
            self.console.print(f"[red]❌ 캡처 처리 실패: {e}[/red]")
            self.root.after(0, lambda: self.status_label.config(text="❌ 오류", fg="#e74c3c"))
    
    def ask_user_input(self, image_path):
        """사용자 입력 받기"""
        self.status_label.config(text="💭 입력 대기", fg="#9b59b6")
        
        user_input = simpledialog.askstring(
            "🤖 코딩 도우미",
            "어떤 도움이 필요하신가요?\n\n예시:\n• 이 에러를 해결해주세요\n• 이 코드를 리뷰해주세요\n• UI를 개선해주세요",
            parent=self.root
        )
        
        if user_input:
            self.status_label.config(text="🤖 분석 중...", fg="#3498db")
            threading.Thread(
                target=self.analyze_and_respond,
                args=(image_path, user_input),
                daemon=True
            ).start()
        else:
            self.status_label.config(text="✅ 준비됨", fg="#2ecc71")
    
    def capture_screen(self):
        """화면 캡처"""
        try:
            # 화면 캡처
            screenshot = pyautogui.screenshot()
            
            # 이미지 크기 조정
            width, height = screenshot.size
            max_dimension = 1920
            
            if width > max_dimension or height > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))
                
                screenshot = screenshot.resize((new_width, new_height), Image.LANCZOS)
            
            # 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            screenshot.save(filepath, optimize=True, quality=85)
            
            self.console.print(f"[green]📸 화면 캡처 완료: {filepath}[/green]")
            return str(filepath)
            
        except Exception as e:
            self.console.print(f"[red]❌ 화면 캡처 실패: {e}[/red]")
            return None
    
    def analyze_and_respond(self, image_path, user_input):
        """화면 분석 및 응답"""
        try:
            # 1단계: OpenAI로 화면 분석
            screen_analysis = self.analyze_screen_with_openai(image_path)
            
            # 2단계: Claude로 코딩 조언
            coding_advice = self.get_coding_advice_with_claude(screen_analysis, user_input)
            
            # 결과 표시
            self.root.after(0, self.show_result, coding_advice)
            
            # 결과 저장
            self.save_result(image_path, user_input, screen_analysis, coding_advice)
            
        except Exception as e:
            error_msg = f"분석 중 오류 발생: {e}"
            self.console.print(f"[red]❌ {error_msg}[/red]")
            self.root.after(0, lambda: messagebox.showerror("오류", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="❌ 오류", fg="#e74c3c"))
    
    def analyze_screen_with_openai(self, image_path):
        """OpenAI로 화면 분석"""
        try:
            # 이미지를 base64로 인코딩
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "이 화면 스크린샷을 분석하고 다음 정보를 제공해주세요:\n1. 화면에 표시된 주요 내용\n2. 코드 에러나 문제점 (있다면)\n3. 개발 환경이나 도구\n4. 현재 상황 요약\n\n간결하고 정확하게 분석해주세요."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.console.print(f"[red]❌ OpenAI 분석 실패: {e}[/red]")
            return f"화면 분석 실패: {e}"
    
    def get_coding_advice_with_claude(self, screen_analysis, user_input):
        """Claude로 코딩 조언"""
        try:
            system_prompt = """
당신은 전문 코딩 멘토입니다. 화면 분석 결과와 사용자 요청을 바탕으로 실용적인 코딩 조언을 제공해주세요.

응답 형식:
## 🎯 문제 파악
[문제 요약]

## 💡 해결 방안
[구체적인 해결 방법]

## 💻 코드 예시
```언어
// 실행 가능한 코드
```

## 📝 추가 팁
[유용한 추가 정보]

간결하고 실용적으로 답변해주세요.
"""
            
            user_message = f"""
화면 분석 결과:
{screen_analysis}

사용자 요청:
{user_input}

위 정보를 바탕으로 코딩 문제 해결 및 조언을 제공해주세요.
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.console.print(f"[red]❌ Claude 분석 실패: {e}[/red]")
            return f"코딩 조언 생성 실패: {e}"
    
    def show_result(self, result):
        """결과 표시"""
        self.status_label.config(text="✅ 완료", fg="#2ecc71")
        
        # 결과 창 표시
        result_window = tk.Toplevel(self.root)
        result_window.title("🤖 코딩 도우미 - 분석 결과")
        result_window.geometry("600x500")
        result_window.attributes('-topmost', True)
        
        # 텍스트 위젯
        text_widget = tk.Text(
            result_window,
            wrap=tk.WORD,
            font=("Consolas", 11),
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스크롤바
        scrollbar = tk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)
        
        # 결과 텍스트 삽입
        text_widget.insert(tk.END, result)
        text_widget.config(state=tk.DISABLED)
        
        # 닫기 버튼
        close_btn = tk.Button(
            result_window,
            text="닫기",
            command=result_window.destroy,
            bg="#3498db",
            fg="white",
            font=("Arial", 10)
        )
        close_btn.pack(pady=10)
    
    def save_result(self, image_path, user_input, screen_analysis, coding_advice):
        """결과 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = self.screenshots_dir / f"analysis_{timestamp}.md"
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"# 코딩 도우미 분석 결과\n\n")
                f.write(f"**시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**사용자 요청**: {user_input}\n")
                f.write(f"**이미지**: {image_path}\n\n")
                f.write(f"## 화면 분석 (OpenAI)\n\n{screen_analysis}\n\n")
                f.write(f"## 코딩 조언 (Claude)\n\n{coding_advice}\n")
            
            self.console.print(f"[green]💾 결과 저장됨: {result_file}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ 결과 저장 실패: {e}[/red]")
    
    def show_info(self):
        """정보 표시"""
        info_text = """
🤖 간단한 코딩 도우미

📸 캡처 버튼을 눌러 화면을 분석하세요!

🔧 AI 분석 방식:
• 화면 분석: OpenAI GPT-4V
• 코딩 조언: Claude 3.5 Sonnet

📁 결과는 screenshots/ 폴더에 저장됩니다.

💡 위젯을 드래그해서 이동할 수 있습니다.
        """
        messagebox.showinfo("정보", info_text)
    
    def quit_app(self):
        """앱 종료"""
        self.save_settings()
        self.root.destroy()
    
    def run(self):
        """GUI 실행"""
        self.console.print("[bold cyan]🤖 간단한 떠다니는 코딩 도우미 시작![/bold cyan]")
        self.console.print("[yellow]📸 캡처 버튼을 눌러 화면을 분석하세요![/yellow]")
        
        # GUI 실행
        self.root.mainloop()


def main():
    """메인 실행 함수"""
    try:
        helper = SimpleFloatingHelper()
        helper.run()
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
