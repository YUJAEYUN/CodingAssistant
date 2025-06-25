#!/bin/bash
echo "🎯 스마트 코딩 어시스턴트 백그라운드 서비스 시작 중..."
cd "$(dirname "$0")"

# 환경변수 로드
source load_env.sh

# 가상환경 활성화
source .venv/bin/activate

# 백그라운드 서비스 실행
python3 simple_background_service.py
