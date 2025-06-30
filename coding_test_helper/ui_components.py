"""
코딩 테스트 도우미 UI 컴포넌트

사용자 친화적인 인터페이스와 단계별 힌트 제공을 위한 UI 컴포넌트들
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, Any, Callable, Optional
import threading


class ProgressiveHintDialog:
    """단계별 힌트 제공 다이얼로그"""
    
    def __init__(self, parent, problem_description: str, hint_provider_func: Callable):
        self.parent = parent
        self.problem_description = problem_description
        self.hint_provider_func = hint_provider_func
        self.current_hint_level = 0
        self.hints = []
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """다이얼로그 설정"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("💡 단계별 힌트")
        self.dialog.geometry("600x500")
        self.dialog.attributes('-topmost', True)
        self.dialog.grab_set()
        
        # 메인 프레임
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = tk.Label(
            main_frame,
            text="🧠 단계별 힌트 제공",
            font=("Arial", 14, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))
        
        # 진행 상황 표시
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(progress_frame, text="힌트 단계:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.progress_label = tk.Label(
            progress_frame,
            text="0/3",
            font=("Arial", 10, "bold"),
            fg="#3498db"
        )
        self.progress_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 힌트 표시 영역
        self.hint_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.hint_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 다음 힌트 버튼
        self.next_hint_btn = tk.Button(
            button_frame,
            text="💡 다음 힌트",
            command=self.get_next_hint,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        self.next_hint_btn.pack(side=tk.LEFT)
        
        # 로딩 표시
        self.loading_label = tk.Label(
            button_frame,
            text="",
            font=("Arial", 9),
            fg="#7f8c8d"
        )
        self.loading_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 닫기 버튼
        close_btn = tk.Button(
            button_frame,
            text="❌ 닫기",
            command=self.dialog.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT)
        
        # 초기 안내 메시지
        self.add_hint_text("🎯 문제 해결을 위한 단계별 힌트를 제공합니다.\n'다음 힌트' 버튼을 클릭하여 시작하세요!\n\n")
    
    def add_hint_text(self, text: str):
        """힌트 텍스트 추가"""
        self.hint_text.config(state=tk.NORMAL)
        self.hint_text.insert(tk.END, text)
        self.hint_text.see(tk.END)
        self.hint_text.config(state=tk.DISABLED)
    
    def get_next_hint(self):
        """다음 힌트 가져오기"""
        if self.current_hint_level >= 3:
            messagebox.showinfo("완료", "모든 힌트를 제공했습니다. 이제 스스로 도전해보세요!")
            return
        
        self.next_hint_btn.config(state=tk.DISABLED)
        self.loading_label.config(text="🔄 힌트 생성 중...")
        
        def hint_thread():
            try:
                hint_types = ["next_step", "algorithm", "debugging"]
                hint_type = hint_types[self.current_hint_level]
                
                current_progress = f"힌트 {self.current_hint_level + 1}단계"
                hint = self.hint_provider_func(
                    self.problem_description,
                    current_progress,
                    hint_type
                )
                
                self.dialog.after(0, lambda: self.display_hint(hint))
                
            except Exception as e:
                error_msg = f"힌트 생성 실패: {e}"
                self.dialog.after(0, lambda: self.show_error(error_msg))
        
        threading.Thread(target=hint_thread, daemon=True).start()
    
    def display_hint(self, hint: str):
        """힌트 표시"""
        self.current_hint_level += 1
        self.progress_label.config(text=f"{self.current_hint_level}/3")
        
        hint_header = f"\n{'='*50}\n💡 힌트 {self.current_hint_level}\n{'='*50}\n\n"
        self.add_hint_text(hint_header + hint + "\n\n")
        
        self.next_hint_btn.config(state=tk.NORMAL)
        self.loading_label.config(text="")
        
        if self.current_hint_level >= 3:
            self.next_hint_btn.config(text="✅ 완료", state=tk.DISABLED)
    
    def show_error(self, error_msg: str):
        """에러 표시"""
        self.add_hint_text(f"❌ {error_msg}\n\n")
        self.next_hint_btn.config(state=tk.NORMAL)
        self.loading_label.config(text="")


class ProblemInputDialog:
    """문제 입력 다이얼로그"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📋 문제 입력")
        self.dialog.geometry("600x400")
        self.dialog.attributes('-topmost', True)
        self.dialog.grab_set()
        
        # 메인 프레임
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = tk.Label(
            main_frame,
            text="📝 코딩 테스트 문제를 입력하세요",
            font=("Arial", 12, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))
        
        # 안내 메시지
        info_label = tk.Label(
            main_frame,
            text="문제 전문을 복사해서 붙여넣으세요. 문제 분석과 학습 가이드를 제공합니다.",
            font=("Arial", 9),
            fg="#7f8c8d",
            wraplength=550
        )
        info_label.pack(pady=(0, 10))
        
        # 문제 입력 영역
        self.problem_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.problem_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 예시 텍스트
        example_text = """예시: 두 개의 정수 배열 nums1과 nums2가 주어졌을 때, 두 배열의 교집합을 반환하라. 각 요소는 결과에 한 번만 나타나야 하며, 결과는 어떤 순서로든 반환될 수 있다.

입력: nums1 = [1,2,2,1], nums2 = [2,2]
출력: [2]"""
        
        self.problem_text.insert("1.0", example_text)
        self.problem_text.tag_add("example", "1.0", "end")
        self.problem_text.tag_config("example", foreground="#95a5a6")
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 분석 시작 버튼
        ok_btn = tk.Button(
            button_frame,
            text="🎯 분석 시작",
            command=self.on_ok,
            bg="#3498db",
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
        self.problem_text.tag_add("sel", "1.0", "end")
        
        # 대화상자가 닫힐 때까지 대기
        self.dialog.wait_window()
    
    def on_ok(self):
        """확인 버튼 클릭"""
        problem = self.problem_text.get("1.0", tk.END).strip()
        
        if not problem or problem.startswith("예시:"):
            messagebox.showwarning("경고", "실제 문제를 입력해주세요.")
            return
        
        self.result = problem
        self.dialog.destroy()
    
    def on_cancel(self):
        """취소 버튼 클릭"""
        self.dialog.destroy()


class LearningProgressTracker:
    """학습 진행 상황 추적기"""
    
    def __init__(self, parent):
        self.parent = parent
        self.progress_data = {
            "problems_analyzed": 0,
            "codes_reviewed": 0,
            "hints_requested": 0,
            "debugging_sessions": 0
        }
        
        self.setup_tracker()
    
    def setup_tracker(self):
        """추적기 UI 설정"""
        self.tracker_frame = tk.Frame(self.parent, bg="#ecf0f1", relief=tk.RAISED, bd=1)
        
        # 제목
        title_label = tk.Label(
            self.tracker_frame,
            text="📊 학습 진행 상황",
            font=("Arial", 9, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title_label.pack(pady=2)
        
        # 진행 상황 표시
        self.progress_labels = {}
        progress_items = [
            ("problems_analyzed", "📋 문제 분석", "#3498db"),
            ("codes_reviewed", "🔍 코드 리뷰", "#e74c3c"),
            ("hints_requested", "💡 힌트 요청", "#f39c12"),
            ("debugging_sessions", "🐛 디버깅", "#9b59b6")
        ]
        
        for key, label, color in progress_items:
            frame = tk.Frame(self.tracker_frame, bg="#ecf0f1")
            frame.pack(fill=tk.X, padx=5, pady=1)
            
            tk.Label(
                frame,
                text=label,
                font=("Arial", 8),
                bg="#ecf0f1",
                fg=color
            ).pack(side=tk.LEFT)
            
            count_label = tk.Label(
                frame,
                text="0",
                font=("Arial", 8, "bold"),
                bg="#ecf0f1",
                fg=color
            )
            count_label.pack(side=tk.RIGHT)
            
            self.progress_labels[key] = count_label
    
    def update_progress(self, action: str):
        """진행 상황 업데이트"""
        if action in self.progress_data:
            self.progress_data[action] += 1
            self.progress_labels[action].config(text=str(self.progress_data[action]))
    
    def get_tracker_frame(self):
        """추적기 프레임 반환"""
        return self.tracker_frame
