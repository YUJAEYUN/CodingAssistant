# 🎯 스마트 코딩 어시스턴트

화면을 캡처하고 AI로 분석하여 코딩 문제를 자동으로 해결하는 혁신적인 도구입니다.

## ✨ 주요 기능

### 🔥 **핫키 기반 즉시 분석**
- **Ctrl+Shift+A** (기본값) 단축키로 즉시 화면 캡처
- 사용자 정의 핫키 설정 가능
- 백그라운드에서 항상 대기 상태

### 🤖 **AI 기반 문제 해결**
- **Claude Sonnet 4** 모델로 화면 내용 분석
- 코드 에러, UI 문제, 개발 이슈 자동 식별
- 실행 가능한 해결 코드 자동 생성

### 📸 **스마트 화면 캡처**
- 전체 화면 또는 특정 영역 캡처
- 이미지 자동 저장 및 관리
- 분석 결과와 함께 체계적 보관

### 🎮 **사용자 친화적 GUI**
- 직관적인 그래픽 인터페이스
- 실시간 서비스 상태 모니터링
- 설정 변경 및 수동 캡처 지원

## 🚀 설치 방법

### 1. **자동 설치 (권장)**
```bash
./install_screen_assistant.sh
```

### 2. **수동 설치**
```bash
# 의존성 설치
pip install anthropic pyautogui Pillow keyboard pynput rich prompt-toolkit

# API 키 설정 (.env 파일 생성)
echo "ANTHROPIC_API_KEY=your_key_here" > .env
echo "OPENAI_API_KEY=your_key_here" >> .env
```

## 🔑 API 키 설정

다음 API 키가 필요합니다:

1. **Anthropic API 키** (필수)
   - Claude 모델 사용을 위해 필요
   - https://console.anthropic.com 에서 발급

2. **OpenAI API 키** (선택사항)
   - 향후 기능 확장을 위해 권장
   - https://platform.openai.com 에서 발급

## 📖 사용법

### 🎯 **기본 사용법**

1. **GUI 프로그램 시작**
   ```bash
   # 웹 기반 GUI (추천)
   ./start_gui.sh

   # 또는
   ./start_floating_assistant.sh
   ```

2. **화면 캡처 및 분석**
   - 🌐 **브라우저 GUI에서**: `📸 화면 캡처` 버튼 클릭
   - 💬 **채팅으로**: 메시지 입력 후 Enter (자동으로 화면 캡처됨)
   - 🚀 **빠른 버튼**: 에러 해결, 코드 리뷰, UI 개선 버튼 클릭

3. **AI 분석 받기**
   - 프롬프트 입력 또는 빠른 버튼 선택
   - 예: "이 에러를 해결하는 코드를 작성해주세요"
   - AI가 화면을 분석하고 해결책 제공

4. **결과 확인**
   - 브라우저 채팅창에서 실시간 결과 확인
   - `screenshots/` 폴더에서 분석 결과 파일 저장

### ⚙️ **고급 설정**

#### 핫키 변경
- GUI에서 "⚙️ 핫키 변경" 버튼 클릭
- 새로운 핫키 조합 입력 (예: `alt+space`, `f12`)

#### 수동 캡처
- GUI에서 "📸 수동 캡처" 버튼 클릭
- 핫키 없이 즉시 화면 분석 실행

## 💡 사용 예시

### 🐛 **코드 에러 해결**
1. 에러가 발생한 화면을 띄워놓기
2. **Ctrl+Shift+A** 누르기
3. "이 에러를 해결해주세요" 입력
4. AI가 에러 분석 및 해결 코드 제공

### 🎨 **UI 개선 요청**
1. 개선하고 싶은 UI 화면 표시
2. **Ctrl+Shift+A** 누르기  
3. "이 UI를 더 사용자 친화적으로 개선해주세요" 입력
4. AI가 개선 방안 및 코드 제공

### 📚 **코드 리뷰**
1. 리뷰할 코드 화면 표시
2. **Ctrl+Shift+A** 누르기
3. "이 코드를 리뷰하고 개선점을 알려주세요" 입력
4. AI가 상세한 코드 리뷰 제공

## 📁 파일 구조

```
스마트 코딩 어시스턴트/
├── screen_assistant.py      # 핵심 화면 분석 모듈
├── background_service.py    # 백그라운드 서비스 및 GUI
├── setup_assistant.py       # 설치 스크립트
├── .env                     # API 키 설정 파일
├── config.json             # 사용자 설정 파일
├── screenshots/            # 캡처된 이미지 및 분석 결과
│   ├── screen_20240626_143022.png
│   └── analysis_20240626_143022.md
├── start_assistant.bat     # Windows 실행 스크립트
├── start_assistant.sh      # macOS/Linux 실행 스크립트
└── uninstall.*            # 제거 스크립트
```

## 🔧 문제 해결

### ❌ **일반적인 문제들**

#### "API 키 오류"
```bash
# .env 파일 확인
cat .env

# API 키 재설정
python setup_assistant.py
```

#### "핫키가 작동하지 않음"
- 다른 프로그램과 핫키 충돌 확인
- GUI에서 다른 핫키로 변경
- 관리자 권한으로 실행 시도

#### "화면 캡처 실패"
- 화면 녹화 권한 확인 (macOS)
- 보안 소프트웨어 예외 설정
- 다른 화면 캡처 프로그램 종료

### 🔍 **로그 확인**
- GUI 하단의 로그 영역에서 실시간 상태 확인
- 오류 발생 시 상세 메시지 표시

## 🗑️ 제거 방법

```bash
# Windows
uninstall.bat

# macOS/Linux
./uninstall.sh
```

## 🔒 보안 및 개인정보

- **로컬 처리**: 모든 화면 캡처는 로컬에서 처리
- **API 통신**: AI 분석을 위해서만 Anthropic API 사용
- **데이터 보관**: 캡처된 이미지는 로컬에만 저장
- **자동 삭제**: 오래된 캡처 파일 자동 정리 옵션

## 🤝 기여하기

1. 이슈 리포트: 버그나 개선사항 제안
2. 기능 요청: 새로운 기능 아이디어 공유
3. 코드 기여: Pull Request 환영

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🆘 지원

- **이슈 트래커**: GitHub Issues
- **이메일**: support@smartcodingassistant.com
- **문서**: 온라인 사용자 가이드

---

**🎯 스마트 코딩 어시스턴트와 함께 더 효율적인 개발을 경험하세요!**
