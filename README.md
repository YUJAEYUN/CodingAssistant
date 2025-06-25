# 🤖 AI 코딩 어시스턴트 컬렉션

화면을 캡처하고 AI로 분석하여 코딩 문제를 해결하는 다양한 도구들의 모음입니다.

## ✨ 주요 기능

### 🔥 **다양한 실행 모드**
- **떠다니는 위젯**: 화면에 고정된 작은 도우미 위젯 (메인)
- **터미널 기반**: 명령줄에서 실행되는 간단한 인터페이스
- **백그라운드 서비스**: 핫키로 언제든 호출 가능

### 🤖 **AI 기반 문제 해결**
- **Claude 3.5 Sonnet**: 코딩 조언 및 문제 해결
- **OpenAI GPT-4V**: 화면 분석 (떠다니는 도우미)
- 코드 에러, UI 문제, 개발 이슈 자동 식별
- 실행 가능한 해결 코드 자동 생성

### 📸 **스마트 화면 캡처**
- 전체 화면 자동 캡처
- 이미지 자동 저장 및 관리 (`screenshots/` 폴더)
- 분석 결과와 함께 체계적 보관

### 🎮 **사용자 친화적 인터페이스**
- 떠다니는 위젯으로 언제든 접근 가능
- 버튼 클릭으로 즉시 화면 분석
- 드래그로 위치 이동 가능

## 🚀 설치 방법

### 1. **자동 설치 (권장)**
```bash
./install_screen_assistant.sh
```
- 가상환경 자동 생성
- 의존성 자동 설치
- API 키 대화형 설정
- 실행 스크립트 자동 생성

### 2. **수동 설치**
```bash
# 1. 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. API 키 설정 (.env 파일 생성)
echo "ANTHROPIC_API_KEY=your_key_here" > .env
echo "OPENAI_API_KEY=your_key_here" >> .env
```

### 3. **실행 전 확인사항**
- 가상환경이 활성화되어 있는지 확인
- `.env` 파일에 API 키가 올바르게 설정되어 있는지 확인
- 모든 실행 스크립트는 자동으로 가상환경을 활성화합니다

## 🔑 API 키 설정

다음 API 키가 필요합니다:

1. **Anthropic API 키** (필수)
   - Claude 모델 사용을 위해 필요
   - https://console.anthropic.com 에서 발급

2. **OpenAI API 키** (떠다니는 도우미용)
   - 화면 분석을 위해 필요
   - https://platform.openai.com 에서 발급

## 📖 사용법

### 🎯 **실행 모드 선택**

#### 1. **떠다니는 코딩 도우미 (추천)**
```bash
./start_coding_helper.sh
```
- 화면에 고정된 작은 위젯
- OpenAI GPT-4V로 화면 분석 + Claude로 코딩 조언
- 📸 캡처 버튼으로 즉시 분석
- 권한 설정 불필요

#### 2. **터미널 기반**
```bash
python screen_assistant.py
```
- 명령줄에서 실행
- 프롬프트 입력 후 화면 캡처 및 분석

#### 3. **백그라운드 서비스**
```bash
./start_background_service.sh
```
- 백그라운드에서 실행
- 핫키로 언제든 호출 가능

### 🎮 **기본 사용법**

#### **첫 실행 시**
```bash
# 1. 설치 (한 번만)
./install_screen_assistant.sh

# 2. 떠다니는 도우미 실행
./start_coding_helper.sh
```

#### **일반 사용법**
1. **화면 캡처 및 분석**
   - 📸 **떠다니는 위젯**: `📸 캡처` 버튼 클릭
   - 💬 **터미널**: 프롬프트 입력 후 Enter

2. **AI 분석 받기**
   - 프롬프트 입력 예시:
     - "이 에러를 해결해주세요"
     - "코드를 리뷰해주세요"
     - "UI를 개선하는 방법을 알려주세요"

3. **결과 확인**
   - 떠다니는 위젯에서 팝업으로 결과 확인
   - `screenshots/` 폴더에 이미지와 분석 결과 저장

#### **중요 참고사항**
- 모든 실행 스크립트는 자동으로 가상환경을 활성화합니다
- 수동으로 Python 파일을 실행할 때는 반드시 가상환경을 먼저 활성화하세요:
  ```bash
  source .venv/bin/activate
  python screen_assistant.py
  ```

## 💡 사용 예시

### 🐛 **코드 에러 해결**
1. 에러가 발생한 화면을 띄워놓기
2. 떠다니는 위젯의 **📸 캡처** 버튼 클릭
3. "이 에러를 해결해주세요" 입력
4. AI가 에러 분석 및 해결 코드 제공

### 🎨 **UI 개선 요청**
1. 개선하고 싶은 UI 화면 표시
2. 떠다니는 위젯의 **📸 캡처** 버튼 클릭
3. "이 UI를 더 사용자 친화적으로 개선해주세요" 입력
4. AI가 개선 방안 및 코드 제공

### 📚 **코드 리뷰**
1. 리뷰할 코드 화면 표시
2. 떠다니는 위젯의 **📸 캡처** 버튼 클릭
3. "이 코드를 리뷰하고 개선점을 알려주세요" 입력
4. AI가 상세한 코드 리뷰 제공

## 📁 파일 구조

```
AI 코딩 어시스턴트/
├── 📋 핵심 모듈
│   ├── screen_assistant.py          # 기본 화면 분석 모듈
│   ├── floating_coding_helper.py    # 떠다니는 도우미 위젯 (고급)
│   ├── simple_floating_helper.py    # 간단한 떠다니는 도우미
│   └── simple_background_service.py # 백그라운드 서비스
│
├── 🛠️ 유틸리티
│   ├── utils/
│   │   ├── common.py               # 공통 유틸리티
│   │   ├── llm_client.py          # LLM 클라이언트
│   │   └── __init__.py
│   └── requirements.txt            # 의존성 목록
│
├── 🚀 실행 스크립트
│   ├── start_coding_helper.sh      # 떠다니는 도우미 시작 (메인)
│   ├── start_background_service.sh # 백그라운드 서비스 시작
│   ├── start_screen_assistant.sh   # 터미널 어시스턴트 시작
│   ├── install_screen_assistant.sh # 설치 스크립트
│   └── load_env.sh                # 환경변수 로드
│
├── 📸 캡처 결과
│   └── screenshots/               # 캡처된 이미지 및 분석 결과
│       ├── screen_YYYYMMDD_HHMMSS.png
│       └── analysis_YYYYMMDD_HHMMSS.md
│
└── ⚙️ 설정 파일
    ├── .env                       # API 키 설정 파일
    └── floating_helper_config.json # 떠다니는 도우미 설정
```

## 🔧 문제 해결

### ❌ **일반적인 문제들**

#### "API 키 오류"
```bash
# .env 파일 확인
cat .env

# .env 파일 생성 (없는 경우)
echo "ANTHROPIC_API_KEY=your_key_here" > .env
echo "OPENAI_API_KEY=your_key_here" >> .env

# 환경변수 로드 테스트
source load_env.sh
```

#### "가상환경 오류"
```bash
# 가상환경이 없는 경우
python3 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

#### "핫키가 작동하지 않음"
- 다른 프로그램과 핫키 충돌 확인 (기본: Ctrl+R)
- 떠다니는 도우미에서 핫키 변경 가능
- 관리자 권한으로 실행 시도

#### "화면 캡처 실패"
- 화면 녹화 권한 확인 (macOS)
- 보안 소프트웨어 예외 설정
- pyautogui 권한 확인

#### "tkinter 오류" (떠다니는 도우미)
```bash
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk
```

### 🔍 **로그 확인**
- 터미널에서 실시간 상태 확인
- 오류 발생 시 상세 메시지 표시
- `screenshots/` 폴더에서 분석 결과 확인

## 🔒 보안 및 개인정보

- **로컬 처리**: 모든 화면 캡처는 로컬에서 처리
- **API 통신**: AI 분석을 위해서만 외부 API 사용
- **데이터 보관**: 캡처된 이미지는 로컬 `screenshots/` 폴더에만 저장
- **자동 저장**: 분석 결과는 마크다운 파일로 저장

## 🛠️ 개발 정보

### 주요 의존성
- **anthropic**: Claude AI 모델 사용
- **openai**: GPT-4V 모델 사용 (떠다니는 도우미)
- **pyautogui**: 화면 캡처
- **Flask**: 웹 인터페이스
- **tkinter**: GUI 위젯 (떠다니는 도우미)
- **rich**: 터미널 UI

### 아키텍처
- 모듈식 설계로 다양한 실행 모드 지원
- 공통 유틸리티 (`utils/`) 모듈 사용
- 웹 템플릿 기반 인터페이스

## 🤝 기여하기

1. 이슈 리포트: 버그나 개선사항 제안
2. 기능 요청: 새로운 기능 아이디어 공유
3. 코드 기여: Pull Request 환영

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🤖 AI 코딩 어시스턴트와 함께 더 효율적인 개발을 경험하세요!**
