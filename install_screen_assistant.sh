#!/bin/bash

# 스마트 코딩 어시스턴트 설치 스크립트
# macOS/Linux용 자동 설치 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "🎯 스마트 코딩 어시스턴트 설치 시작"
echo "=================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# 1. Python 버전 확인
echo ""
print_info "Python 버전 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION 발견"
else
    print_error "Python 3이 설치되지 않았습니다."
    echo "Python 3.8 이상을 설치해주세요: https://python.org"
    exit 1
fi

# 2. 가상환경 확인 및 생성
echo ""
print_info "가상환경 확인 중..."
if [ ! -d ".venv" ]; then
    print_info "가상환경 생성 중..."
    python3 -m venv .venv
    print_success "가상환경 생성 완료"
else
    print_success "기존 가상환경 발견"
fi

# 3. 가상환경 활성화
print_info "가상환경 활성화 중..."
source .venv/bin/activate
print_success "가상환경 활성화 완료"

# 4. 의존성 설치
echo ""
print_info "의존성 패키지 설치 중..."

# 기본 패키지 설치
pip install --upgrade pip > /dev/null 2>&1

# 필수 패키지 목록
PACKAGES=(
    "anthropic==0.47.0"
    "pyautogui>=0.9.54"
    "Pillow>=10.0.0"
    "keyboard>=0.13.5"
    "pynput>=1.7.6"
    "rich>=13.9.4"
    "prompt-toolkit>=3.0.50"
)

for package in "${PACKAGES[@]}"; do
    print_info "설치 중: $package"
    pip install "$package" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "$package 설치 완료"
    else
        print_error "$package 설치 실패"
        exit 1
    fi
done

# 5. API 키 설정
echo ""
print_info "API 키 설정..."

if [ ! -f ".env" ]; then
    echo ""
    echo "API 키를 설정해야 합니다:"
    echo "1. OpenAI API 키 (필수) - https://platform.openai.com"
    echo "2. Anthropic API 키 (필수) - https://console.anthropic.com"
    echo ""
    
    read -p "OpenAI API 키를 입력하세요: " OPENAI_KEY
    read -p "Anthropic API 키를 입력하세요: " ANTHROPIC_KEY
    
    if [ -z "$OPENAI_KEY" ] || [ -z "$ANTHROPIC_KEY" ]; then
        print_error "API 키가 입력되지 않았습니다."
        exit 1
    fi
    
    # .env 파일 생성
    cat > .env << EOF
# API Keys for Smart Coding Assistant
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# OpenAI API Key
OPENAI_API_KEY=$OPENAI_KEY

# Anthropic API Key
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
EOF
    
    print_success "API 키 설정 완료"
else
    print_success ".env 파일이 이미 존재합니다"
fi

# 6. 실행 스크립트 생성
echo ""
print_info "실행 스크립트 생성 중..."

# 기본 실행 스크립트
cat > start_screen_assistant.sh << 'EOF'
#!/bin/bash
echo "🎯 스마트 코딩 어시스턴트 시작 중..."
cd "$(dirname "$0")"

# 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 가상환경 활성화
source .venv/bin/activate

# 프로그램 실행
python3 screen_assistant.py
EOF

# 백그라운드 서비스 실행 스크립트
cat > start_background_service.sh << 'EOF'
#!/bin/bash
echo "🎯 스마트 코딩 어시스턴트 백그라운드 서비스 시작 중..."
cd "$(dirname "$0")"

# 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 가상환경 활성화
source .venv/bin/activate

# 백그라운드 서비스 실행
python3 simple_background_service.py
EOF

# 실행 권한 부여
chmod +x start_screen_assistant.sh
chmod +x start_background_service.sh

print_success "실행 스크립트 생성 완료"

# 7. 바탕화면 바로가기 생성 (macOS)
echo ""
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_info "macOS 바탕화면 바로가기 생성 중..."
    
    DESKTOP_DIR="$HOME/Desktop"
    CURRENT_DIR="$(pwd)"
    
    # 심볼릭 링크 생성
    if [ -d "$DESKTOP_DIR" ]; then
        ln -sf "$CURRENT_DIR/start_screen_assistant.sh" "$DESKTOP_DIR/스마트 코딩 어시스턴트"
        ln -sf "$CURRENT_DIR/start_background_service.sh" "$DESKTOP_DIR/백그라운드 서비스"
        print_success "바탕화면 바로가기 생성 완료"
    else
        print_warning "바탕화면 폴더를 찾을 수 없습니다"
    fi
fi

# 8. 제거 스크립트 생성
echo ""
print_info "제거 스크립트 생성 중..."

cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "🗑️ 스마트 코딩 어시스턴트 제거 중..."

# 실행 중인 프로세스 종료
pkill -f "screen_assistant.py" 2>/dev/null
pkill -f "simple_background_service.py" 2>/dev/null

# 바탕화면 바로가기 제거
rm -f "$HOME/Desktop/스마트 코딩 어시스턴트" 2>/dev/null
rm -f "$HOME/Desktop/백그라운드 서비스" 2>/dev/null

# 생성된 파일들 제거
rm -rf screenshots/ 2>/dev/null
rm -f config.json 2>/dev/null

echo "✅ 제거 완료"
echo "가상환경과 소스 파일은 수동으로 삭제해주세요."
EOF

chmod +x uninstall.sh
print_success "제거 스크립트 생성 완료"

# 9. 테스트
echo ""
print_info "설치 테스트 중..."

# 환경변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 간단한 import 테스트
python3 -c "
import pyautogui
import anthropic
from screen_assistant import ScreenAssistant
print('✅ 모든 모듈 import 성공')
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "설치 테스트 통과"
else
    print_error "설치 테스트 실패"
    exit 1
fi

# 10. 완료 메시지
echo ""
echo "=================================="
print_success "🎉 설치 완료!"
echo ""
echo "사용 방법:"
echo "1. 기본 모드: ./start_screen_assistant.sh"
echo "2. 백그라운드 서비스: ./start_background_service.sh"
echo ""
echo "바탕화면 바로가기도 생성되었습니다!"
echo ""
echo "📁 결과는 screenshots/ 폴더에서 확인하세요"
echo "🗑️ 제거: ./uninstall.sh"
echo ""
print_info "즐거운 코딩 되세요! 🚀"
