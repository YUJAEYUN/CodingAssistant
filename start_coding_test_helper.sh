#!/bin/bash

# 코딩 테스트 도우미 시작 스크립트
# LangChain 기반 학습 중심 코딩 테스트 도우미

echo "🧠 코딩 테스트 도우미 시작 중..."

# 현재 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# Python 버전 확인
python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Python이 설치되지 않았습니다."
    exit 1
fi
echo "🐍 Python 버전: $python_version"

# 가상환경 확인 및 활성화
if [ -d ".venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source .venv/bin/activate
    echo "✅ 가상환경 활성화 완료"
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "📦 기존 가상환경 사용 중: $VIRTUAL_ENV"
else
    echo "⚠️ 가상환경이 없습니다."
    echo "🔧 가상환경을 생성하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "📦 가상환경 생성 중..."
        python3 -m venv .venv || python -m venv .venv
        source .venv/bin/activate
        echo "✅ 가상환경 생성 및 활성화 완료"
    else
        echo "⚠️ 시스템 Python으로 실행합니다."
    fi
fi

# 환경변수 로드 (선택적)
if [ -f ".env" ]; then
    echo "🔑 환경변수 로드 중..."
    source .env
    echo "✅ 환경변수 로드 완료"
else
    echo "⚠️ .env 파일이 없습니다."
    echo "💡 AI 기능을 사용하려면 API 키를 설정하세요:"
    echo "   echo 'ANTHROPIC_API_KEY=your_key_here' > .env"
    echo "   echo 'OPENAI_API_KEY=your_key_here' >> .env"
    echo "🔄 기본 모드로 실행합니다."
fi

# 기본 패키지 확인
echo "📋 기본 의존성 확인 중..."
python -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter가 설치되지 않았습니다."
    echo "💡 설치 방법:"
    echo "   macOS: brew install python-tk"
    echo "   Ubuntu: sudo apt-get install python3-tk"
    exit 1
fi

# LangChain 패키지 확인 (선택적)
echo "🔍 LangChain 패키지 확인 중..."
python -c "import langchain, langchain_anthropic, langchain_openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ LangChain 패키지가 설치되지 않았습니다."
    echo "🤔 LangChain 패키지를 설치하시겠습니까? (y/n)"
    echo "   (설치하지 않으면 기본 화면 캡처 기능만 사용 가능)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "📦 패키지 설치 중..."
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "❌ 패키지 설치 실패. 기본 모드로 실행합니다."
        else
            echo "✅ 패키지 설치 완료"
        fi
    else
        echo "🔄 기본 모드로 실행합니다."
    fi
else
    echo "✅ LangChain 패키지 확인 완료"
fi

# 코딩 테스트 도우미 실행
echo "🚀 코딩 테스트 도우미 실행..."
echo "💡 창이 나타나지 않으면 Dock에서 Python 아이콘을 확인하세요."

python coding_test_floating_helper.py

echo "👋 코딩 테스트 도우미 종료"
