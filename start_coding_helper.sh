#!/bin/bash

echo "🤖 떠다니는 코딩 도우미 시작!"
echo "================================"

cd "$(dirname "$0")"

# 환경변수 로드
source load_env.sh

# 가상환경 활성화
source .venv/bin/activate

# tkinter 설치 확인
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter가 설치되지 않았습니다."
    echo "macOS에서는 다음 명령어로 설치하세요:"
    echo "brew install python-tk"
    echo ""
    echo "또는 웹 버전을 사용하세요: ./start_gui.sh"
    exit 1
fi

echo ""
echo "🎮 사용법:"
echo "  • 작은 위젯이 화면에 나타납니다"
echo "  • 마우스로 드래그해서 위치 이동 가능"
echo "  • Ctrl+R을 눌러 화면 캡처 및 AI 분석"
echo "  • ⚙️ 버튼으로 핫키 변경 가능"
echo ""
echo "🔧 AI 분석 방식:"
echo "  • 화면 분석: OpenAI GPT-4V"
echo "  • 코딩 조언: Claude 3.5 Sonnet"
echo ""
echo "⏹️  종료: 위젯의 ❌ 버튼 클릭"
echo ""

# 떠다니는 코딩 도우미 실행
python3 floating_coding_helper.py
