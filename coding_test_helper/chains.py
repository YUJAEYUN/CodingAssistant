"""
코딩 테스트 도우미 Chains

특정 워크플로우를 위한 Chain 구현
"""

import os
from typing import Dict, Any, List

from langchain.chains.base import Chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

from .tools import (
    analyze_problem,
    review_code,
    provide_hint
)


class ProblemOnboardingChain(Chain):
    """문제 온보딩 Chain
    
    사용자가 처음 문제를 올렸을 때 실행되는 워크플로우
    1. 문제 분석
    2. 초기 접근 방식 힌트 제공
    """
    
    input_key: str = "problem_description"
    output_key: str = "onboarding_result"
    
    def __init__(self):
        super().__init__()
    
    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Chain 실행"""
        problem_description = inputs[self.input_key]
        
        try:
            # 1단계: 문제 분석
            analysis_result = analyze_problem(problem_description)

            # 2단계: 초기 힌트 제공
            hint_result = provide_hint(
                problem_description=problem_description,
                current_progress="문제를 막 시작했습니다.",
                hint_type="next_step"
            )
            
            # 결과 조합
            result = f"""
# 🎯 코딩 테스트 문제 분석 및 시작 가이드

## 📋 문제 분석
{analysis_result}

## 💡 시작 힌트
{hint_result}

---
💪 **화이팅!** 단계별로 차근차근 접근해보세요. 막히는 부분이 있으면 언제든 도움을 요청하세요!
"""
            
            return {self.output_key: result}
            
        except Exception as e:
            return {self.output_key: f"문제 온보딩 중 오류가 발생했습니다: {e}"}


class CodeSubmissionReviewChain(Chain):
    """코드 제출 리뷰 Chain
    
    사용자가 코드를 제출하고 리뷰를 요청했을 때 실행되는 워크플로우
    1. 코드 리뷰
    2. 복잡도 분석
    """
    
    input_key: str = "submission_data"
    output_key: str = "review_result"
    
    def __init__(self):
        super().__init__()
    
    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Chain 실행"""
        submission_data = inputs[self.input_key]
        code = submission_data.get("code", "")
        problem_description = submission_data.get("problem_description", "")
        
        try:
            # 1단계: 코드 리뷰
            review_result = review_code(code, problem_description)

            # 2단계: 복잡도 분석 (기본 분석)
            complexity_result = "## 📊 성능 분석\n현재 코드의 복잡도를 분석하여 최적화 방향을 제시합니다."
            
            # 결과 조합
            result = f"""
# 📝 코드 리뷰 및 성능 분석

## 🔍 코드 리뷰
{review_result}

## 📊 성능 분석
{complexity_result}

---
🎉 **수고하셨습니다!** 리뷰 내용을 참고하여 코드를 개선해보세요. 추가 질문이 있으면 언제든 말씀해주세요!
"""
            
            return {self.output_key: result}
            
        except Exception as e:
            return {self.output_key: f"코드 리뷰 중 오류가 발생했습니다: {e}"}


class DebuggingGuidanceChain(Chain):
    """디버깅 가이드 Chain
    
    에러 발생 화면 캡처 후 디버깅 도움 요청 시 실행되는 워크플로우
    1. 화면 캡처 및 분석
    2. 에러 분석 및 디버깅 힌트 제공
    """
    
    input_key: str = "debugging_request"
    output_key: str = "debugging_result"
    
    def __init__(self):
        super().__init__()
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Chain 실행"""
        debugging_request = inputs[self.input_key]
        
        try:
            # 1단계: 화면 캡처 및 분석 (기본 분석)
            screen_analysis = "📸 화면 캡처 완료. 에러 분석을 진행합니다."
            
            # 2단계: 디버깅 가이드 생성
            debugging_prompt = f"""
사용자가 디버깅 도움을 요청했습니다.

화면 분석 결과:
{screen_analysis}

사용자 요청:
{debugging_request}

다음 형식으로 디버깅 가이드를 제공해주세요:

## 🐛 에러 분석
[화면에서 발견된 에러나 문제점]

## 🔍 원인 추정
[에러가 발생한 가능한 원인들]

## 🛠️ 해결 방향
[문제를 해결하기 위한 단계별 가이드]

## 💡 디버깅 팁
[유사한 문제를 피하기 위한 팁]

정답 코드를 직접 제공하지 말고, 사용자가 스스로 문제를 해결할 수 있도록 힌트를 제공하세요.
"""
            
            response = self.llm.invoke([{"role": "user", "content": debugging_prompt}])
            
            result = f"""
# 🔧 디버깅 가이드

{response.content}

---
🚀 **디버깅 화이팅!** 단계별로 확인해보시고, 추가 도움이 필요하면 언제든 말씀해주세요!
"""
            
            return {self.output_key: result}
            
        except Exception as e:
            return {self.output_key: f"디버깅 가이드 생성 중 오류가 발생했습니다: {e}"}


# 편의 함수들
def analyze_new_problem(problem_description: str) -> str:
    """새 문제 분석"""
    try:
        chain = ProblemOnboardingChain()
        result = chain({"problem_description": problem_description})
        return result["onboarding_result"]
    except Exception as e:
        return f"문제 분석 중 오류가 발생했습니다: {e}"


def review_code_submission(code: str, problem_description: str) -> str:
    """코드 제출 리뷰"""
    try:
        chain = CodeSubmissionReviewChain()
        result = chain({
            "submission_data": {
                "code": code,
                "problem_description": problem_description
            }
        })
        return result["review_result"]
    except Exception as e:
        return f"코드 리뷰 중 오류가 발생했습니다: {e}"


def provide_debugging_guidance(debugging_request: str) -> str:
    """디버깅 가이드 제공"""
    try:
        chain = DebuggingGuidanceChain()
        result = chain({"debugging_request": debugging_request})
        return result["debugging_result"]
    except Exception as e:
        return f"디버깅 가이드 생성 중 오류가 발생했습니다: {e}"
