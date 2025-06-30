# 🧠 LangChain 기반 코딩 테스트 도우미

**정답 코드를 직접 제공하지 않고 학습 중심 가이드를 제공하는 AI 코딩 테스트 도우미**

## ✨ 주요 특징

### 🎯 **학습 중심 접근**
- ❌ 정답 코드를 직접 제공하지 않음
- ✅ 단계별 힌트와 사고 과정 유도
- ✅ 문제 해결 능력 향상에 집중
- ✅ 스스로 학습할 수 있도록 가이드

### 🤖 **LangChain 기반 AI 시스템**
- **Claude 3.5 Sonnet**: 학습 가이드 및 힌트 제공
- **GPT-4V**: 화면 분석 및 에러 진단
- **Few-shot Learning**: 일관된 학습 중심 응답
- **Agent 시스템**: 상황에 맞는 도구 자동 선택

### 🛠️ **전문 도구들**
- **문제 분석기**: 핵심 요구사항과 추상적 힌트 제공
- **코드 리뷰어**: 개선 방향 힌트 (수정 코드 제공 안함)
- **단계별 힌트**: 점진적 학습 가이드
- **테스트 케이스 생성기**: 자가 검증 도구
- **복잡도 분석기**: 성능 최적화 힌트
- **디버깅 도우미**: 에러 분석 및 해결 방향

### 🎮 **사용자 친화적 UI**
- **떠다니는 위젯**: 언제든 접근 가능
- **단계별 힌트 다이얼로그**: 점진적 학습 지원
- **학습 진행 추적**: 활동 기록 및 동기 부여
- **화면 캡처 분석**: 실시간 에러 진단

## 🚀 설치 및 실행

### 1. **환경 설정**
```bash
# 의존성 설치 (LangChain 포함)
pip install -r requirements.txt

# API 키 설정
echo "ANTHROPIC_API_KEY=your_anthropic_key" > .env
echo "OPENAI_API_KEY=your_openai_key" >> .env
```

### 2. **코딩 테스트 도우미 실행**
```bash
# 떠다니는 위젯 모드
./start_coding_test_helper.sh

# 또는 직접 실행
python coding_test_floating_helper.py
```

### 3. **테스트 및 검증**
```bash
# 시스템 테스트 실행
python test_coding_helper.py
```

## 📖 사용법

### 🎯 **기본 워크플로우**

#### 1. **문제 분석**
- 📋 **문제 분석** 버튼 클릭
- 문제 전문 입력
- AI가 핵심 요구사항과 추상적 힌트 제공

#### 2. **단계별 힌트 받기**
- 💡 **힌트 요청** 버튼 클릭
- 단계별 힌트 다이얼로그에서 점진적 학습
- 3단계 힌트: 다음 단계 → 알고리즘 방향 → 디버깅 팁

#### 3. **코드 리뷰**
- 🔍 **코드 리뷰** 버튼 클릭
- 작성한 코드와 문제 설명 입력
- 개선 방향 힌트 받기 (수정 코드는 제공 안함)

#### 4. **디버깅 도움**
- 🐛 **디버깅 도움** 버튼 클릭
- 화면 캡처를 통한 에러 분석
- 해결 방향 가이드 제공

### 💡 **사용 예시**

#### **문제 분석 결과 예시**
```
## 📋 문제 요약
두 배열에서 공통으로 나타나는 요소들을 찾아 중복 없이 반환하는 문제입니다.

## 🎯 핵심 요구사항
- 두 배열의 교집합 찾기
- 결과에서 중복 제거
- 순서는 상관없음

## 💭 사고 방향 힌트
- 두 배열의 요소를 효율적으로 비교하는 방법을 생각해보세요
- 중복을 제거하는 자료구조가 있을까요?
- 시간 복잡도를 O(n²)보다 개선할 수 있는 방법이 있을까요?
```

#### **코드 리뷰 결과 예시**
```
## 👍 잘한 점
- 문제의 핵심 로직을 정확히 구현했습니다
- 중복 제거 로직을 포함했습니다

## 🤔 개선 포인트
- 시간 복잡도가 O(n×m×k)로 비효율적입니다
- 중복 검사가 매번 선형 탐색을 수행합니다

## 💡 개선 방향 힌트
- 중복 검사를 O(1)로 만들 수 있는 자료구조가 있을까요?
- 집합(Set) 연산을 활용해보는 것은 어떨까요?
```

## 🔧 시스템 구조

### **LangChain 컴포넌트**

#### **Agents**
- `CodingTestAgent`: 중앙 제어 시스템
- 사용자 요청 분석 후 적절한 Tool 선택
- 학습 중심 응답 보장

#### **Tools**
- `ProblemAnalysisTool`: 문제 분석 및 추상적 힌트
- `CodeReviewTool`: 코드 리뷰 및 개선 방향
- `HintProviderTool`: 단계별 힌트 제공
- `ExampleTestCaseGeneratorTool`: 테스트 케이스 생성
- `ComplexityAnalysisTool`: 성능 분석
- `KnowledgeBaseRetrievalTool`: 개념 설명
- `ScreenCaptureTool`: 화면 분석

#### **Chains**
- `ProblemOnboardingChain`: 문제 온보딩 워크플로우
- `CodeSubmissionReviewChain`: 코드 제출 리뷰
- `DebuggingGuidanceChain`: 디버깅 가이드

#### **Prompts**
- Few-shot Learning 적용
- 정답 코드 제공 방지
- 일관된 학습 중심 응답

### **UI 컴포넌트**
- `ProgressiveHintDialog`: 단계별 힌트 다이얼로그
- `ProblemInputDialog`: 문제 입력 인터페이스
- `LearningProgressTracker`: 학습 진행 추적

## 🎓 학습 효과

### **기존 AI 도우미의 문제점**
- ❌ 정답 코드를 즉시 제공
- ❌ 사고 과정 생략
- ❌ 학습 효과 저하
- ❌ 문제 해결 능력 미향상

### **우리 도우미의 장점**
- ✅ 단계별 사고 과정 유도
- ✅ 스스로 문제 해결하도록 가이드
- ✅ 개념 이해 중심 접근
- ✅ 장기적 학습 효과

## 🔒 보안 및 개인정보

- **로컬 처리**: 화면 캡처는 로컬에서만 처리
- **API 통신**: AI 분석을 위해서만 외부 API 사용
- **데이터 보관**: 캡처 이미지는 로컬 저장
- **학습 기록**: 진행 상황은 로컬에만 저장

## 🛠️ 개발 정보

### **주요 의존성**
```
langchain>=0.1.0
langchain-anthropic>=0.1.0
langchain-openai>=0.0.5
anthropic>=0.47.0
openai>=1.0.0
rich>=13.9.4
tkinter (Python 내장)
```

### **파일 구조**
```
coding_test_helper/
├── __init__.py              # 모듈 초기화
├── agents.py               # LangChain Agent
├── chains.py               # 워크플로우 Chain
├── tools.py                # 전문 도구들
├── prompts.py              # Few-shot 프롬프트
└── ui_components.py        # UI 컴포넌트

coding_test_floating_helper.py  # 메인 UI 애플리케이션
test_coding_helper.py          # 테스트 스크립트
start_coding_test_helper.sh    # 실행 스크립트
```

## 🤝 기여하기

1. **이슈 리포트**: 버그나 개선사항 제안
2. **기능 요청**: 새로운 학습 도구 아이디어
3. **프롬프트 개선**: Few-shot 예시 추가
4. **테스트 케이스**: 다양한 문제 유형 테스트

## 📄 라이선스

MIT License - 교육 목적으로 자유롭게 사용 가능

---

**🧠 AI와 함께하는 스마트한 코딩 테스트 학습을 경험하세요!**

*정답을 알려주는 것이 아니라, 스스로 답을 찾을 수 있도록 도와드립니다.*
