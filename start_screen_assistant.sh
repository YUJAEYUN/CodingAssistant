#!/bin/bash
echo "🎯 스마트 코딩 어시스턴트 시작 중..."
cd "$(dirname "$0")"

# 환경변수 로드
source load_env.sh

# 가상환경 활성화
source .venv/bin/activate

# 프로그램 실행
python3 screen_assistant.py
