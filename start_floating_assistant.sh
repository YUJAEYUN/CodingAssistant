#!/bin/bash
echo "🌐 웹 기반 코딩 어시스턴트 시작 중..."
cd "$(dirname "$0")"

# 환경변수 로드
source load_env.sh

# 가상환경 활성화
source .venv/bin/activate

# 웹 어시스턴트 실행
echo "🚀 웹 서버를 시작합니다..."
echo "브라우저가 자동으로 열립니다."
echo "수동으로 열려면: http://127.0.0.1:8080"
echo ""
echo "📸 화면 캡처 버튼을 눌러 AI 분석을 받아보세요!"
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

python3 manual_web_assistant.py
