#!/bin/bash

# 가상환경 설정 스크립트
# 코딩 테스트 도우미를 위한 가상환경 자동 설정

echo "🔧 가상환경 설정 시작..."

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# Python 버전 확인
echo "🐍 Python 버전 확인 중..."
python_cmd=""
if command -v python3 &> /dev/null; then
    python_cmd="python3"
    python_version=$(python3 --version)
elif command -v python &> /dev/null; then
    python_cmd="python"
    python_version=$(python --version)
else
    echo "❌ Python이 설치되지 않았습니다."
    echo "💡 Python 설치 방법:"
    echo "   macOS: brew install python"
    echo "   Ubuntu: sudo apt update && sudo apt install python3"
    echo "   Windows: https://python.org에서 다운로드"
    exit 1
fi

echo "✅ $python_version 발견"

# 가상환경 생성
if [ -d ".venv" ]; then
    echo "📦 기존 가상환경 발견"
    echo "🤔 기존 가상환경을 삭제하고 새로 만드시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🗑️ 기존 가상환경 삭제 중..."
        rm -rf .venv
    else
        echo "✅ 기존 가상환경 사용"
        source .venv/bin/activate
        echo "📦 가상환경 활성화 완료"
        echo "🔍 현재 Python 경로: $(which python)"
        echo "📋 설치된 패키지 확인 중..."
        pip list
        exit 0
    fi
fi

echo "📦 새 가상환경 생성 중..."
$python_cmd -m venv .venv

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성 실패"
    echo "💡 venv 모듈이 설치되지 않았을 수 있습니다."
    echo "   Ubuntu: sudo apt install python3-venv"
    exit 1
fi

echo "✅ 가상환경 생성 완료"

# 가상환경 활성화
echo "🔄 가상환경 활성화 중..."
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화 실패"
    exit 1
fi

echo "✅ 가상환경 활성화 완료"
echo "🔍 현재 Python 경로: $(which python)"

# pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip

# 설치 옵션 선택
echo ""
echo "📋 설치할 패키지를 선택하세요:"
echo "1) 최소 설치 (기본 화면 캡처만)"
echo "2) 전체 설치 (AI 기능 포함)"
echo "3) 사용자 정의"
echo ""
read -p "선택 (1-3): " choice

case $choice in
    1)
        echo "📦 최소 패키지 설치 중..."
        pip install -r requirements-minimal.txt
        ;;
    2)
        echo "📦 전체 패키지 설치 중..."
        pip install -r requirements.txt
        ;;
    3)
        echo "📦 기본 패키지 설치 중..."
        pip install -r requirements-minimal.txt
        echo ""
        echo "🤔 추가 기능을 설치하시겠습니까?"
        echo "y) AI 기능 (LangChain, Anthropic, OpenAI)"
        echo "n) 건너뛰기"
        read -p "선택 (y/n): " ai_choice
        
        if [[ "$ai_choice" =~ ^[Yy]$ ]]; then
            echo "📦 AI 패키지 설치 중..."
            pip install langchain langchain-core langchain-community langchain-anthropic langchain-openai anthropic openai
        fi
        ;;
    *)
        echo "❌ 잘못된 선택입니다. 최소 설치를 진행합니다."
        pip install -r requirements-minimal.txt
        ;;
esac

# 설치 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ 패키지 설치 완료"
else
    echo "⚠️ 일부 패키지 설치에 실패했습니다."
    echo "💡 개별적으로 설치를 시도해보세요."
fi

# 환경변수 설정 안내
echo ""
echo "🔑 환경변수 설정 (선택적):"
if [ ! -f ".env" ]; then
    echo "💡 AI 기능을 사용하려면 API 키를 설정하세요:"
    echo "   echo 'ANTHROPIC_API_KEY=your_anthropic_key' > .env"
    echo "   echo 'OPENAI_API_KEY=your_openai_key' >> .env"
    echo ""
    echo "🤔 지금 API 키를 설정하시겠습니까? (y/n)"
    read -p "선택: " api_choice
    
    if [[ "$api_choice" =~ ^[Yy]$ ]]; then
        echo "🔑 Anthropic API 키를 입력하세요 (없으면 Enter):"
        read -r anthropic_key
        echo "🔑 OpenAI API 키를 입력하세요 (없으면 Enter):"
        read -r openai_key
        
        if [ -n "$anthropic_key" ]; then
            echo "ANTHROPIC_API_KEY=$anthropic_key" > .env
            echo "✅ Anthropic API 키 저장됨"
        fi
        
        if [ -n "$openai_key" ]; then
            echo "OPENAI_API_KEY=$openai_key" >> .env
            echo "✅ OpenAI API 키 저장됨"
        fi
    fi
else
    echo "✅ .env 파일이 이미 존재합니다."
fi

# 설치된 패키지 목록
echo ""
echo "📋 설치된 패키지 목록:"
pip list

# 완료 메시지
echo ""
echo "🎉 가상환경 설정 완료!"
echo ""
echo "📖 사용 방법:"
echo "1. 가상환경 활성화: source .venv/bin/activate"
echo "2. 코딩 테스트 도우미 실행: ./start_coding_test_helper.sh"
echo "3. 또는 직접 실행: python coding_test_floating_helper.py"
echo ""
echo "💡 다음에 실행할 때는 ./start_coding_test_helper.sh만 실행하면 됩니다."
