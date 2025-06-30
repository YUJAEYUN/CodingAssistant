"""
코딩 테스트 도우미 전용 Tools

LangChain Tool 인터페이스를 구현하여 학습 중심 코딩 테스트 도움 기능 제공
"""

import os
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic

# 프롬프트는 직접 시스템 프롬프트로 대체


# LLM 인스턴스 전역 변수
_llm_anthropic = None

def get_anthropic_llm():
    """Anthropic LLM 인스턴스 반환"""
    global _llm_anthropic
    if _llm_anthropic is None:
        try:
            _llm_anthropic = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        except Exception as e:
            print(f"Anthropic LLM 초기화 실패: {e}")
            return None
    return _llm_anthropic

# OpenAI LLM은 현재 사용하지 않음


@tool
def analyze_problem(problem_description: str) -> str:
    """코딩 테스트 문제를 분석하여 핵심 요구사항과 추상적인 힌트를 제공합니다.

    Args:
        problem_description: 코딩 테스트 문제 전문

    Returns:
        문제 분석 결과 및 학습 힌트
    """
    try:
        llm = get_anthropic_llm()
        if llm is None:
            return "❌ AI 모델을 사용할 수 없습니다. API 키를 확인해주세요."

        # 기본 프롬프트 사용 (Few-shot 없이도 작동)
        system_prompt = """당신은 코딩 테스트 학습 도우미입니다. 문제를 분석할 때 다음 원칙을 지켜주세요:

1. 정답 알고리즘을 직접 명시하지 마세요
2. 추상적이고 사고를 유도하는 힌트만 제공하세요
3. 문제의 핵심 요구사항과 제약 조건을 명확히 설명하세요

응답 형식:
## 📋 문제 요약
[문제의 핵심 내용]

## 🎯 핵심 요구사항
[무엇을 구현해야 하는지]

## ⚠️ 제약 조건
[시간/공간 복잡도, 입력 범위 등]

## 💭 사고 방향 힌트
[직접적이지 않은 접근 방향 힌트 2-3개]"""

        user_message = f"다음 코딩 테스트 문제를 분석해주세요:\n\n{problem_description}"

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])

        return response.content

    except Exception as e:
        return f"문제 분석 중 오류가 발생했습니다: {e}"


@tool
def review_code(code: str, problem_description: str) -> str:
    """사용자의 코드를 리뷰하고 개선 방향에 대한 힌트를 제공합니다.

    Args:
        code: 사용자가 작성한 코드
        problem_description: 코딩 테스트 문제 전문

    Returns:
        코드 리뷰 결과 및 개선 힌트
    """
    try:
        llm = get_anthropic_llm()
        if llm is None:
            return "❌ AI 모델을 사용할 수 없습니다. API 키를 확인해주세요."

        system_prompt = """당신은 코딩 테스트 학습 도우미입니다. 코드를 리뷰할 때 다음 원칙을 지켜주세요:

1. 직접적인 수정 코드를 제공하지 마세요
2. 문제점을 지적하고 개선 방향을 힌트로 제시하세요
3. 사용자가 스스로 생각하고 수정할 수 있도록 유도하세요
4. 긍정적이고 격려하는 톤으로 피드백하세요

응답 형식:
## 👍 잘한 점
[코드에서 좋은 부분들]

## 🤔 개선 포인트
[문제가 될 수 있는 부분들과 왜 문제인지]

## 💡 개선 방향 힌트
[어떤 방향으로 개선하면 좋을지 힌트]

## 🚀 성능 고려사항
[시간/공간 복잡도 관련 힌트]"""

        user_message = f"""
문제: {problem_description}

코드:
```
{code}
```

위 코드를 리뷰하고 개선 방향을 힌트로 제공해주세요.
"""

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])

        return response.content

    except Exception as e:
        return f"코드 리뷰 중 오류가 발생했습니다: {e}"


@tool
def provide_hint(problem_description: str, current_progress: str = "", hint_type: str = "next_step") -> str:
    """코딩 테스트 문제에 대한 단계별 힌트를 제공합니다.

    Args:
        problem_description: 코딩 테스트 문제 전문
        current_progress: 사용자의 현재 진행 상황
        hint_type: 요청된 힌트 종류 (next_step, algorithm, debugging)

    Returns:
        단계별 힌트 및 학습 가이드
    """
    try:
        llm = get_anthropic_llm()
        if llm is None:
            return "❌ AI 모델을 사용할 수 없습니다. API 키를 확인해주세요."

        hint_prompts = {
            "next_step": "다음 단계로 무엇을 해야 할지 힌트를 주세요.",
            "algorithm": "어떤 접근 방식이나 자료구조를 고려해볼지 힌트를 주세요.",
            "debugging": "코드에서 확인해봐야 할 부분들에 대한 힌트를 주세요."
        }

        system_prompt = """당신은 코딩 테스트 학습 도우미입니다. 힌트를 제공할 때 다음 원칙을 지켜주세요:

1. 정답을 직접 알려주지 마세요
2. 사용자가 스스로 생각할 수 있도록 질문 형태로 유도하세요
3. 점진적으로 힌트를 제공하세요
4. 격려하는 톤으로 응답하세요

응답 형식:
## 🤔 생각해볼 점
[사용자가 고민해봐야 할 질문들]

## 💡 힌트
[단계별 힌트 2-3개]

## 🔍 확인사항
[체크해봐야 할 것들]"""

        user_message = f"""
문제: {problem_description}

현재 진행 상황: {current_progress if current_progress else "문제를 막 시작했습니다."}

힌트 종류: {hint_type}
요청: {hint_prompts.get(hint_type, hint_prompts["next_step"])}
"""

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ])

        return response.content

    except Exception as e:
        return f"힌트 제공 중 오류가 발생했습니다: {e}"


# 사용하지 않는 클래스들은 제거됨
# 현재 사용되는 함수 기반 도구들만 유지
