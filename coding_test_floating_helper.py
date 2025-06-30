#!/usr/bin/env python3
"""
코딩 테스트 도우미 - 떠다니는 위젯

LangChain을 활용한 학습 중심 코딩 테스트 도우미
기존 floating_coding_helper.py를 확장하여 코딩 테스트 전용 기능 추가
"""

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from pathlib import Path
from datetime import datetime

# 환경변수 로드 (선택적)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv가 설치되지 않았습니다. .env 파일을 사용하려면 'pip install python-dotenv'를 실행하세요.")

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 기본 의존성 확인
try:
    from rich.console import Console
except ImportError:
    print("rich 패키지가 설치되지 않았습니다. 'pip install rich'를 실행하세요.")
    # 기본 콘솔 클래스로 대체
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    print("Pillow 패키지가 설치되지 않았습니다. 'pip install Pillow'를 실행하세요.")
    PIL_AVAILABLE = False

# 코딩 테스트 도우미 모듈 import
LANGCHAIN_AVAILABLE = False
try:
    from coding_test_helper.agents import get_coding_test_agent
    from coding_test_helper.chains import (
        analyze_new_problem,
        review_code_submission,
        provide_debugging_guidance
    )
    from coding_test_helper.ui_components import (
        ProgressiveHintDialog,
        ProblemInputDialog,
        LearningProgressTracker
    )
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain 모듈 로드 완료")
except ImportError as e:
    print(f"⚠️ LangChain 모듈을 불러올 수 없습니다: {e}")
    print("📦 다음 명령어로 의존성을 설치하세요:")
    print("   pip install -r requirements.txt")
    print("🔄 기본 모드로 실행됩니다 (화면 캡처만 가능)")

    # 기본 클래스들 정의 (LangChain 없이도 실행 가능하도록)
    class ProgressiveHintDialog:
        def __init__(self, *args, **kwargs):
            messagebox.showwarning("기능 제한", "LangChain이 설치되지 않아 힌트 기능을 사용할 수 없습니다.")

    class ProblemInputDialog:
        def __init__(self, *args, **kwargs):
            self.result = None
            messagebox.showwarning("기능 제한", "LangChain이 설치되지 않아 문제 분석 기능을 사용할 수 없습니다.")

    class LearningProgressTracker:
        def __init__(self, *args, **kwargs):
            pass
        def get_tracker_frame(self):
            return tk.Frame()
        def update_progress(self, *args, **kwargs):
            pass


class CodingTestFloatingHelper:
    """코딩 테스트 전용 떠다니는 도우미"""
    
    def __init__(self):
        self.console = Console()
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # LangChain Agent 초기화
        if LANGCHAIN_AVAILABLE:
            try:
                self.agent = get_coding_test_agent()
                self.console.print("[green]✅ 코딩 테스트 Agent 초기화 완료[/green]")
            except Exception as e:
                self.console.print(f"[red]❌ Agent 초기화 실패: {e}[/red]")
                self.agent = None
        else:
            self.agent = None
        
        # 현재 모드 (일반/코딩테스트)
        self.current_mode = "coding_test"

        # 학습 진행 상황 추적기 초기화
        if LANGCHAIN_AVAILABLE:
            self.progress_tracker = None  # GUI 설정 후 초기화
        else:
            self.progress_tracker = None

        # GUI 설정
        self.setup_gui()

        # 설정 로드
        self.load_settings()
    
    def setup_gui(self):
        """GUI 설정"""
        self.root = tk.Tk()
        self.root.title("🧠 코딩 테스트 도우미")
        self.root.geometry("300x400")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        
        # 드래그 가능하게 설정
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.on_drag)
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = tk.Label(
            main_frame,
            text="🧠 코딩 테스트 도우미",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))
        
        # 모드 선택
        mode_frame = tk.Frame(main_frame, bg="#2c3e50")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(mode_frame, text="모드:", fg="#ecf0f1", bg="#2c3e50").pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value="coding_test")
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.mode_var,
            values=["coding_test", "general"],
            state="readonly",
            width=12
        )
        mode_combo.pack(side=tk.RIGHT)
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # 코딩 테스트 전용 버튼들
        self.coding_test_frame = tk.Frame(main_frame, bg="#2c3e50")
        self.coding_test_frame.pack(fill=tk.X, pady=5)
        
        # 문제 분석 버튼
        analyze_btn = tk.Button(
            self.coding_test_frame,
            text="📋 문제 분석",
            command=self.analyze_problem,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        analyze_btn.pack(fill=tk.X, pady=2)
        
        # 코드 리뷰 버튼
        review_btn = tk.Button(
            self.coding_test_frame,
            text="🔍 코드 리뷰",
            command=self.review_code,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        review_btn.pack(fill=tk.X, pady=2)
        
        # 힌트 요청 버튼
        hint_btn = tk.Button(
            self.coding_test_frame,
            text="💡 힌트 요청",
            command=self.request_hint,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        hint_btn.pack(fill=tk.X, pady=2)
        
        # 디버깅 도움 버튼
        debug_btn = tk.Button(
            self.coding_test_frame,
            text="🐛 디버깅 도움",
            command=self.debug_help,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        debug_btn.pack(fill=tk.X, pady=2)
        
        # 화면 캡처 버튼 (공통)
        capture_btn = tk.Button(
            main_frame,
            text="📸 화면 캡처",
            command=self.capture_and_analyze,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        capture_btn.pack(fill=tk.X, pady=10)
        
        # 상태 표시
        self.status_label = tk.Label(
            main_frame,
            text="🟢 준비됨",
            fg="#2ecc71",
            bg="#2c3e50",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=(10, 0))
        
        # 입력 프롬프트 영역
        prompt_frame = tk.Frame(main_frame, bg="#2c3e50")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(
            prompt_frame,
            text="💬 요청사항:",
            fg="#ecf0f1",
            bg="#2c3e50",
            font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        self.prompt_text = tk.Text(
            prompt_frame,
            height=4,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 기본 프롬프트 설정
        self.prompt_text.insert("1.0", "이 문제를 어떻게 접근해야 할까요?")

        # 학습 진행 상황 추적기 추가
        if LANGCHAIN_AVAILABLE and self.progress_tracker is None:
            try:
                self.progress_tracker = LearningProgressTracker(main_frame)
                tracker_frame = self.progress_tracker.get_tracker_frame()
                tracker_frame.pack(fill=tk.X, pady=5)
            except:
                self.progress_tracker = None
    
    def on_mode_change(self, event=None):
        """모드 변경 처리"""
        self.current_mode = self.mode_var.get()
        if self.current_mode == "coding_test":
            self.coding_test_frame.pack(fill=tk.X, pady=5)
            self.root.title("🧠 코딩 테스트 도우미")
        else:
            self.coding_test_frame.pack_forget()
            self.root.title("🤖 일반 코딩 도우미")
    
    def start_drag(self, event):
        """드래그 시작"""
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        """드래그 중"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def load_settings(self):
        """설정 로드"""
        config_file = Path("coding_test_helper_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 위치 복원
                if 'position' in config:
                    x, y = config['position']
                    self.root.geometry(f"+{x}+{y}")
                    
            except Exception as e:
                self.console.print(f"[yellow]⚠️ 설정 로드 실패: {e}[/yellow]")
    
    def save_settings(self):
        """설정 저장"""
        try:
            config = {
                'position': [self.root.winfo_x(), self.root.winfo_y()],
                'mode': self.current_mode
            }
            
            with open("coding_test_helper_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.console.print(f"[yellow]⚠️ 설정 저장 실패: {e}[/yellow]")

    def analyze_problem(self):
        """문제 분석 실행"""
        if not LANGCHAIN_AVAILABLE or not self.agent:
            messagebox.showerror("오류", "LangChain이 설치되지 않았습니다.")
            return

        # 문제 입력 다이얼로그 사용
        problem_dialog = ProblemInputDialog(self.root)
        if not problem_dialog.result:
            return

        problem_description = problem_dialog.result

        self.status_label.config(text="🔄 문제 분석 중...", fg="#f39c12")
        self.root.update()

        def analyze_thread():
            try:
                result = analyze_new_problem(problem_description)
                self.root.after(0, lambda: self.show_result("문제 분석 결과", result))
                self.root.after(0, lambda: self.status_label.config(text="✅ 분석 완료", fg="#2ecc71"))

                # 진행 상황 업데이트
                if self.progress_tracker:
                    self.progress_tracker.update_progress("problems_analyzed")

            except Exception as e:
                error_msg = f"문제 분석 중 오류 발생: {e}"
                self.root.after(0, lambda: messagebox.showerror("오류", error_msg))
                self.root.after(0, lambda: self.status_label.config(text="❌ 오류", fg="#e74c3c"))

        threading.Thread(target=analyze_thread, daemon=True).start()

    def review_code(self):
        """코드 리뷰 실행"""
        if not LANGCHAIN_AVAILABLE or not self.agent:
            messagebox.showerror("오류", "LangChain이 설치되지 않았습니다.")
            return

        # 코드 입력 다이얼로그
        code_dialog = CodeInputDialog(self.root)
        if code_dialog.result:
            code = code_dialog.result['code']
            problem = code_dialog.result['problem']

            self.status_label.config(text="🔄 코드 리뷰 중...", fg="#f39c12")
            self.root.update()

            def review_thread():
                try:
                    result = review_code_submission(code, problem)
                    self.root.after(0, lambda: self.show_result("코드 리뷰 결과", result))
                    self.root.after(0, lambda: self.status_label.config(text="✅ 리뷰 완료", fg="#2ecc71"))

                    # 진행 상황 업데이트
                    if self.progress_tracker:
                        self.progress_tracker.update_progress("codes_reviewed")

                except Exception as e:
                    error_msg = f"코드 리뷰 중 오류 발생: {e}"
                    self.root.after(0, lambda: messagebox.showerror("오류", error_msg))
                    self.root.after(0, lambda: self.status_label.config(text="❌ 오류", fg="#e74c3c"))

            threading.Thread(target=review_thread, daemon=True).start()

    def request_hint(self):
        """힌트 요청 실행"""
        if not LANGCHAIN_AVAILABLE or not self.agent:
            messagebox.showerror("오류", "LangChain이 설치되지 않았습니다.")
            return

        # 문제 설명 가져오기
        problem_description = self.prompt_text.get("1.0", tk.END).strip()
        if not problem_description or problem_description == "이 문제를 어떻게 접근해야 할까요?":
            # 문제 입력 다이얼로그 사용
            problem_dialog = ProblemInputDialog(self.root)
            if not problem_dialog.result:
                return
            problem_description = problem_dialog.result

        # 단계별 힌트 다이얼로그 열기
        def hint_provider_func(problem_desc, current_progress, hint_type):
            """힌트 제공 함수"""
            from coding_test_helper.tools import HintProviderTool
            hint_tool = HintProviderTool()
            return hint_tool._run(problem_desc, current_progress, hint_type)

        # 단계별 힌트 다이얼로그 실행
        ProgressiveHintDialog(self.root, problem_description, hint_provider_func)

        # 진행 상황 업데이트
        if self.progress_tracker:
            self.progress_tracker.update_progress("hints_requested")

    def debug_help(self):
        """디버깅 도움 실행"""
        if not LANGCHAIN_AVAILABLE or not self.agent:
            messagebox.showerror("오류", "LangChain이 설치되지 않았습니다.")
            return

        user_input = self.prompt_text.get("1.0", tk.END).strip()
        if not user_input:
            user_input = "화면의 에러를 분석하고 디버깅 도움을 주세요."

        self.status_label.config(text="🔄 디버깅 분석 중...", fg="#f39c12")
        self.root.update()

        def debug_thread():
            try:
                result = provide_debugging_guidance(user_input)
                self.root.after(0, lambda: self.show_result("디버깅 가이드", result))
                self.root.after(0, lambda: self.status_label.config(text="✅ 분석 완료", fg="#2ecc71"))

                # 진행 상황 업데이트
                if self.progress_tracker:
                    self.progress_tracker.update_progress("debugging_sessions")

            except Exception as e:
                error_msg = f"디버깅 분석 중 오류 발생: {e}"
                self.root.after(0, lambda: messagebox.showerror("오류", error_msg))
                self.root.after(0, lambda: self.status_label.config(text="❌ 오류", fg="#e74c3c"))

        threading.Thread(target=debug_thread, daemon=True).start()

    def capture_and_analyze(self):
        """화면 캡처 및 분석"""
        user_input = self.prompt_text.get("1.0", tk.END).strip()
        if not user_input:
            user_input = "이 화면을 분석해주세요."

        self.status_label.config(text="🔄 캡처 및 분석 중...", fg="#f39c12")
        self.root.update()

        def capture_thread():
            try:
                if LANGCHAIN_AVAILABLE and self.agent:
                    # LangChain Agent 사용
                    request = f"화면을 캡처하고 분석해주세요. 요청사항: {user_input}"
                    result = self.agent.process_request(request)
                else:
                    # 기본 화면 캡처 (fallback)
                    result = self.basic_screen_capture(user_input)

                self.root.after(0, lambda: self.show_result("화면 분석 결과", result))
                self.root.after(0, lambda: self.status_label.config(text="✅ 분석 완료", fg="#2ecc71"))
            except Exception as e:
                error_msg = f"화면 분석 중 오류 발생: {e}"
                self.root.after(0, lambda: messagebox.showerror("오류", error_msg))
                self.root.after(0, lambda: self.status_label.config(text="❌ 오류", fg="#e74c3c"))

        threading.Thread(target=capture_thread, daemon=True).start()

    def basic_screen_capture(self, user_input: str) -> str:
        """기본 화면 캡처 (LangChain 없을 때 fallback)"""
        try:
            # pyautogui 동적 import
            try:
                import pyautogui
            except ImportError:
                return "❌ pyautogui 패키지가 설치되지 않았습니다.\n'pip install pyautogui'를 실행하세요."

            # 화면 캡처
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = self.screenshots_dir / f"screen_{timestamp}.png"

            screenshot = pyautogui.screenshot()
            screenshot.save(image_path)

            return f"📸 화면이 캡처되었습니다: {image_path}\n\n💡 LangChain을 설치하면 AI 분석 기능을 사용할 수 있습니다.\n\n📦 설치 명령어:\npip install -r requirements.txt"

        except Exception as e:
            return f"화면 캡처 실패: {e}\n\n💡 macOS에서는 시스템 환경설정 > 보안 및 개인정보보호 > 개인정보보호 > 화면 기록에서 Python 또는 터미널 권한을 허용해야 합니다."

    def show_result(self, title: str, content: str):
        """결과 표시"""
        result_window = tk.Toplevel(self.root)
        result_window.title(f"🤖 {title}")
        result_window.geometry("700x600")
        result_window.attributes('-topmost', True)

        # 텍스트 위젯
        text_frame = tk.Frame(result_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            padx=10,
            pady=10
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 스크롤바
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # 내용 삽입
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

        # 버튼 프레임
        button_frame = tk.Frame(result_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 복사 버튼
        copy_btn = tk.Button(
            button_frame,
            text="📋 복사",
            command=lambda: self.copy_to_clipboard(content),
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 닫기 버튼
        close_btn = tk.Button(
            button_frame,
            text="❌ 닫기",
            command=result_window.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT)

    def copy_to_clipboard(self, text: str):
        """클립보드에 복사"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("복사 완료", "결과가 클립보드에 복사되었습니다.")

    def run(self):
        """메인 루프 실행"""
        try:
            self.console.print("[green]🚀 코딩 테스트 도우미 시작[/green]")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.console.print("[yellow]⚠️ 사용자에 의해 중단됨[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ 실행 중 오류: {e}[/red]")

    def on_closing(self):
        """종료 처리"""
        self.save_settings()
        self.root.destroy()


class CodeInputDialog:
    """코드 입력 다이얼로그"""

    def __init__(self, parent):
        self.result = None

        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📝 코드 입력")
        self.dialog.geometry("600x500")
        self.dialog.attributes('-topmost', True)
        self.dialog.grab_set()  # 모달 다이얼로그

        # 메인 프레임
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 문제 설명 입력
        tk.Label(main_frame, text="문제 설명:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.problem_text = tk.Text(main_frame, height=4, font=("Consolas", 9))
        self.problem_text.pack(fill=tk.X, pady=(5, 10))

        # 코드 입력
        tk.Label(main_frame, text="코드:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.code_text = tk.Text(main_frame, height=15, font=("Consolas", 9))
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # 버튼 프레임
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 확인 버튼
        ok_btn = tk.Button(
            button_frame,
            text="✅ 확인",
            command=self.on_ok,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        ok_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 취소 버튼
        cancel_btn = tk.Button(
            button_frame,
            text="❌ 취소",
            command=self.on_cancel,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        cancel_btn.pack(side=tk.RIGHT)

        # 포커스 설정
        self.problem_text.focus_set()

        # 대화상자가 닫힐 때까지 대기
        self.dialog.wait_window()

    def on_ok(self):
        """확인 버튼 클릭"""
        problem = self.problem_text.get("1.0", tk.END).strip()
        code = self.code_text.get("1.0", tk.END).strip()

        if not problem or not code:
            messagebox.showwarning("경고", "문제 설명과 코드를 모두 입력해주세요.")
            return

        self.result = {
            'problem': problem,
            'code': code
        }
        self.dialog.destroy()

    def on_cancel(self):
        """취소 버튼 클릭"""
        self.dialog.destroy()


def main():
    """메인 실행 함수"""
    try:
        helper = CodingTestFloatingHelper()
        helper.run()
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
