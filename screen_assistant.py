#!/usr/bin/env python3
"""
스마트 코딩 어시스턴트 - 화면 캡처 및 AI 분석 도구

사용자의 화면을 캡처하고 AI로 분석하여 코드 문제를 해결하는 도구입니다.
"""

import os
import sys
import time
import base64
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import pyautogui
import keyboard
from PIL import Image, ImageGrab
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.llm_client import get_client


class ScreenAssistant:
    """화면 캡처 및 AI 분석을 담당하는 메인 클래스"""
    
    def __init__(self):
        self.console = Console()
        self.client = None
        self.is_running = False
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # API 키 확인
        if "ANTHROPIC_API_KEY" not in os.environ:
            self.console.print("[red]❌ ANTHROPIC_API_KEY가 설정되지 않았습니다![/red]")
            sys.exit(1)
            
        # LLM 클라이언트 초기화
        try:
            self.client = get_client(
                "anthropic-direct",
                model_name="claude-sonnet-4-20250514",
                use_caching=True,
            )
            self.console.print("[green]✅ AI 클라이언트 초기화 완료[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ AI 클라이언트 초기화 실패: {e}[/red]")
            sys.exit(1)
    
    def capture_screen(self, region: Optional[tuple] = None) -> str:
        """
        화면을 캡처하고 파일로 저장
        
        Args:
            region: 캡처할 영역 (x, y, width, height). None이면 전체 화면
            
        Returns:
            저장된 이미지 파일 경로
        """
        try:
            # 화면 캡처
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            # 이미지 저장
            screenshot.save(filepath)
            self.console.print(f"[green]📸 화면 캡처 완료: {filepath}[/green]")
            
            return str(filepath)
            
        except Exception as e:
            self.console.print(f"[red]❌ 화면 캡처 실패: {e}[/red]")
            return ""
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """이미지를 base64로 인코딩"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.console.print(f"[red]❌ 이미지 인코딩 실패: {e}[/red]")
            return ""
    
    def analyze_screen_with_prompt(self, image_path: str, user_prompt: str) -> str:
        """
        캡처된 화면과 사용자 프롬프트를 결합하여 AI 분석
        
        Args:
            image_path: 캡처된 이미지 파일 경로
            user_prompt: 사용자가 입력한 프롬프트
            
        Returns:
            AI 분석 결과 및 해결 코드
        """
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

            # AI 클라이언트 호출 (Anthropic 직접 사용)
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("🤖 AI 분석 중...", total=None)

                # Anthropic 클라이언트 직접 사용
                import anthropic
                anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

                response = anthropic_client.messages.create(
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

                progress.remove_task(task)

            return response.content[0].text
            
        except Exception as e:
            self.console.print(f"[red]❌ AI 분석 실패: {e}[/red]")
            return f"AI 분석 중 오류가 발생했습니다: {e}"
    
    def process_request(self, user_prompt: str):
        """사용자 요청 처리 (화면 캡처 + AI 분석)"""
        self.console.print(Panel(
            f"[bold blue]🚀 요청 처리 시작[/bold blue]\n"
            f"프롬프트: {user_prompt}",
            title="Screen Assistant",
            border_style="blue"
        ))
        
        # 1. 화면 캡처
        image_path = self.capture_screen()
        if not image_path:
            return
        
        # 2. AI 분석
        result = self.analyze_screen_with_prompt(image_path, user_prompt)
        
        # 3. 결과 출력
        self.console.print(Panel(
            result,
            title="[bold green]🎯 AI 분석 결과[/bold green]",
            border_style="green"
        ))
        
        # 4. 결과를 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.screenshots_dir / f"analysis_{timestamp}.md"
        
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"# 화면 분석 결과\n\n")
            f.write(f"**시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**프롬프트**: {user_prompt}\n")
            f.write(f"**이미지**: {image_path}\n\n")
            f.write(result)
        
        self.console.print(f"[green]💾 결과 저장됨: {result_file}[/green]")


def main():
    """메인 실행 함수"""
    assistant = ScreenAssistant()
    
    assistant.console.print(Panel(
        "[bold]🎯 스마트 코딩 어시스턴트[/bold]\n\n"
        "화면을 캡처하고 AI로 분석하여 코딩 문제를 해결합니다.\n\n"
        "[yellow]사용법:[/yellow]\n"
        "1. 문제가 있는 화면을 띄워놓으세요\n"
        "2. 아래에 해결하고 싶은 내용을 입력하세요\n"
        "3. Enter를 누르면 화면을 캡처하고 분석합니다\n\n"
        "[red]종료: 'quit' 또는 'exit' 입력[/red]",
        title="Screen Assistant",
        border_style="cyan"
    ))
    
    try:
        while True:
            # 사용자 입력 받기
            user_prompt = input("\n💬 프롬프트를 입력하세요: ").strip()
            
            # 종료 명령 확인
            if user_prompt.lower() in ['quit', 'exit', '종료']:
                assistant.console.print("[bold]👋 프로그램을 종료합니다.[/bold]")
                break
            
            if not user_prompt:
                assistant.console.print("[yellow]⚠️ 프롬프트를 입력해주세요.[/yellow]")
                continue
            
            # 요청 처리
            assistant.process_request(user_prompt)
            
    except KeyboardInterrupt:
        assistant.console.print("\n[bold]👋 프로그램이 중단되었습니다.[/bold]")


if __name__ == "__main__":
    main()
