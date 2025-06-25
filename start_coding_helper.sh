#!/bin/bash

echo "🤖 떠다니는 코딩 도우미"
echo "================================"

cd "$(dirname "$0")"

# 환경변수 로드
source load_env.sh

# 가상환경 활성화
source .venv/bin/activate

echo ""
echo "✨ 권한 문제 없는 간단한 버전입니다!"
echo ""
echo "🎮 사용법:"
echo "  • 작은 위젯이 화면에 나타납니다"
echo "  • 마우스로 드래그해서 위치 이동 가능"
echo "  • 📸 캡처 버튼을 눌러 화면 분석"
echo "  • 권한 설정이 필요 없습니다!"
echo ""
echo "🔧 AI 분석 방식:"
echo "  • 화면 분석: OpenAI GPT-4V"
echo "  • 코딩 조언: Claude 3.5 Sonnet"
echo ""
echo "⏹️  종료: 위젯의 ❌ 버튼 클릭"
echo ""

# 간단한 떠다니는 도우미 실행
python3 simple_floating_helper.py
