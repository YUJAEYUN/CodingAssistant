# 🐍 가상환경 설정 가이드

**코딩 테스트 도우미를 가상환경에서 안전하게 실행하는 방법**

## 🎯 가상환경을 사용하는 이유

### ✅ **장점**
- **패키지 충돌 방지**: 시스템 Python과 분리된 환경
- **버전 관리**: 프로젝트별 독립적인 패키지 버전
- **깔끔한 설치**: 필요한 패키지만 설치
- **안전한 테스트**: 시스템에 영향 없이 실험 가능

### ❌ **가상환경 없이 설치할 때 문제점**
- 시스템 Python 패키지와 충돌
- 다른 프로젝트에 영향
- 권한 문제 발생 가능
- 패키지 버전 관리 어려움

## 🚀 빠른 시작 (자동 설정)

### **1단계: 자동 설정 스크립트 실행**
```bash
# 가상환경 자동 설정
./setup_venv.sh
```

이 스크립트가 자동으로 처리하는 것들:
- ✅ Python 버전 확인
- ✅ 가상환경 생성
- ✅ 필요한 패키지 설치
- ✅ API 키 설정 (선택적)

### **2단계: 코딩 테스트 도우미 실행**
```bash
# 자동으로 가상환경 활성화하고 실행
./start_coding_test_helper.sh
```

## 🔧 수동 설정 (고급 사용자)

### **1단계: 가상환경 생성**
```bash
# Python 3.8 이상 필요
python3 -m venv .venv

# 또는 python 명령어 사용
python -m venv .venv
```

### **2단계: 가상환경 활성화**
```bash
# macOS/Linux
source .venv/bin/activate

# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### **3단계: 패키지 설치**

#### **옵션 1: 최소 설치 (기본 기능만)**
```bash
pip install -r requirements-minimal.txt
```

#### **옵션 2: 전체 설치 (AI 기능 포함)**
```bash
pip install -r requirements.txt
```

#### **옵션 3: 개별 설치**
```bash
# 기본 필수 패키지
pip install pyautogui Pillow rich python-dotenv

# AI 기능 추가
pip install langchain langchain-anthropic langchain-openai anthropic openai
```

### **4단계: 환경변수 설정 (선택적)**
```bash
# .env 파일 생성
echo "ANTHROPIC_API_KEY=your_anthropic_key" > .env
echo "OPENAI_API_KEY=your_openai_key" >> .env
```

### **5단계: 실행**
```bash
python coding_test_floating_helper.py
```

## 📋 설치 옵션별 기능

### **최소 설치 (requirements-minimal.txt)**
```
✅ 화면 캡처
✅ 기본 UI
❌ AI 분석
❌ 코딩 테스트 도우미
```

### **전체 설치 (requirements.txt)**
```
✅ 화면 캡처
✅ 기본 UI
✅ AI 분석 (Claude, GPT-4V)
✅ 코딩 테스트 도우미
✅ 단계별 힌트
✅ 코드 리뷰
✅ 문제 분석
```

## 🔍 문제 해결

### **가상환경 생성 실패**
```bash
# venv 모듈이 없는 경우
# Ubuntu/Debian
sudo apt install python3-venv

# macOS (Homebrew)
brew install python

# 또는 virtualenv 사용
pip install virtualenv
virtualenv .venv
```

### **tkinter 오류**
```bash
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

### **권한 오류 (macOS)**
```bash
# 화면 기록 권한 필요
# 시스템 환경설정 > 보안 및 개인정보보호 > 개인정보보호 > 화면 기록
# Python 또는 터미널 앱 권한 허용
```

### **패키지 설치 실패**
```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 클리어
pip cache purge

# 개별 설치 시도
pip install pyautogui
pip install Pillow
pip install rich
```

## 🎮 사용법

### **가상환경 활성화 확인**
```bash
# 프롬프트에 (.venv) 표시되는지 확인
(.venv) user@computer:~/CodingAssistant$

# Python 경로 확인
which python
# 출력: /path/to/CodingAssistant/.venv/bin/python
```

### **패키지 목록 확인**
```bash
pip list
```

### **가상환경 비활성화**
```bash
deactivate
```

## 📁 파일 구조

```
CodingAssistant/
├── .venv/                          # 가상환경 (자동 생성)
├── setup_venv.sh                   # 가상환경 자동 설정
├── start_coding_test_helper.sh     # 실행 스크립트
├── requirements.txt                # 전체 패키지 목록
├── requirements-minimal.txt        # 최소 패키지 목록
├── .env                           # API 키 (선택적)
├── coding_test_floating_helper.py  # 메인 애플리케이션
└── coding_test_helper/            # LangChain 모듈
```

## 💡 팁과 권장사항

### **개발 워크플로우**
1. **프로젝트 시작**: `./setup_venv.sh` 한 번만 실행
2. **일상 사용**: `./start_coding_test_helper.sh`로 실행
3. **패키지 추가**: 가상환경 활성화 후 `pip install`
4. **업데이트**: `pip install --upgrade package_name`

### **성능 최적화**
- 가상환경은 SSD에 생성 권장
- 불필요한 패키지는 설치하지 않기
- 정기적으로 `pip cache purge` 실행

### **백업 및 공유**
```bash
# 현재 패키지 목록 저장
pip freeze > my-requirements.txt

# 다른 환경에서 복원
pip install -r my-requirements.txt
```

## 🆘 도움이 필요한 경우

### **자주 묻는 질문**

**Q: 가상환경을 삭제하고 싶어요**
```bash
# 가상환경 비활성화 후
deactivate
rm -rf .venv
```

**Q: 다른 Python 버전을 사용하고 싶어요**
```bash
# 특정 Python 버전으로 가상환경 생성
python3.9 -m venv .venv
# 또는
/usr/bin/python3.8 -m venv .venv
```

**Q: 가상환경이 활성화되지 않아요**
```bash
# 경로 확인
ls -la .venv/bin/activate

# 권한 확인
chmod +x .venv/bin/activate

# 직접 실행
bash .venv/bin/activate
```

### **지원 채널**
- 🐛 버그 리포트: GitHub Issues
- 💬 질문: GitHub Discussions
- 📧 이메일: 프로젝트 메인테이너

---

**🎉 가상환경으로 안전하고 깔끔한 개발 환경을 만들어보세요!**
