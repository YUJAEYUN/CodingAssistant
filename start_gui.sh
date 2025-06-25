#!/bin/bash

echo "🎯 스마트 코딩 어시스턴트 GUI 시작!"
echo "=================================="

cd "$(dirname "$0")"

# 환경변수 로드
source load_env.sh

# 가상환경 활성화
source .venv/bin/activate

# 브라우저 기반 GUI 실행
echo ""
echo "✨ 브라우저에서 GUI가 자동으로 열립니다!"
echo "📱 URL: http://127.0.0.1:8080"
echo ""
echo "🎮 사용법:"
echo "  • 📸 '화면 캡처' 버튼 클릭"
echo "  • 💬 메시지 입력 후 Enter"
echo "  • 🐛 빠른 버튼들 활용"
echo ""
echo "⏹️  종료: Ctrl+C"
echo ""

python3 manual_web_assistant.py
