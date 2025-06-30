"""
코딩 테스트 도우미 Agent

LangChain Agent를 활용하여 사용자의 요청에 따라 적절한 Tool을 선택하고 실행
"""

import os
from typing import List, Dict, Any, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferWindowMemory

from .tools import (
    analyze_problem,
    review_code,
    provide_hint
)


class CodingTestAgent:
    """코딩 테스트 도우미 Agent
    
    사용자의 요청을 분석하여 적절한 도구를 선택하고 실행하는 중앙 제어 시스템
    학습 중심 접근 방식으로 정답 코드를 직접 제공하지 않고 힌트와 가이드 제공
    """
    
    def __init__(self, memory_window: int = 5):
        """Agent 초기화
        
        Args:
            memory_window: 기억할 대화 수 (기본값: 5)
        """
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.1
        )
        
        # Tools 초기화
        self.tools = self._initialize_tools()
        
        # Memory 설정
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=memory_window
        )
        
        # Agent 생성
        self.agent_executor = self._create_agent()
    
    def _initialize_tools(self) -> List[Tool]:
        """도구들 초기화"""
        # 함수 기반 도구들 사용
        tools = [
            analyze_problem,
            review_code,
            provide_hint
        ]

        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Agent 생성"""
        # 시스템 프롬프트 정의
        system_prompt = """
당신은 코딩 테스트 학습 도우미 AI입니다. 다음 원칙을 반드시 지켜주세요:

🎯 **핵심 원칙**
1. 정답 코드를 직접 제공하지 마세요
2. 사용자가 스스로 문제를 해결하도록 단계별 힌트와 가이드를 제공하세요
3. 학습 과정을 중시하고 사고 과정을 유도하세요
4. 격려하고 긍정적인 톤으로 응답하세요

🛠️ **사용 가능한 도구들**
- problem_analyzer: 문제 분석 및 추상적 힌트 제공
- code_reviewer: 코드 리뷰 및 개선 방향 힌트
- hint_provider: 단계별 힌트 제공
- example_test_case_generator: 테스트 케이스 생성
- complexity_analyzer: 시간/공간 복잡도 분석
- knowledge_base_retrieval: 개념 설명 및 학습 자료
- screen_capture: 화면 캡처 및 분석

📋 **응답 가이드라인**
- 사용자의 요청을 정확히 파악하고 적절한 도구를 선택하세요
- 여러 도구를 조합하여 종합적인 도움을 제공할 수 있습니다
- 항상 학습 효과를 최우선으로 고려하세요

사용자의 요청에 따라 적절한 도구를 사용하여 도움을 제공하세요.
"""
        
        # React Agent용 프롬프트 템플릿
        prompt = ChatPromptTemplate.from_template("""
{system_prompt}

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""").partial(system_prompt=system_prompt)
        
        # React Agent 생성
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        # Agent Executor 생성
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate"
        )
        
        return agent_executor
    
    def process_request(self, user_input: str) -> str:
        """사용자 요청 처리
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            Agent의 응답
        """
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response.get("output", "죄송합니다. 응답을 생성할 수 없습니다.")
            
        except Exception as e:
            return f"요청 처리 중 오류가 발생했습니다: {e}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 기록 조회
        
        Returns:
            대화 기록 리스트
        """
        try:
            return self.memory.chat_memory.messages
        except:
            return []
    
    def clear_memory(self):
        """메모리 초기화"""
        self.memory.clear()
    
    def add_custom_tool(self, tool: Tool):
        """사용자 정의 도구 추가
        
        Args:
            tool: 추가할 도구
        """
        self.tools.append(tool)
        # Agent 재생성
        self.agent_executor = self._create_agent()


# 편의를 위한 전역 인스턴스
_global_agent = None

def get_coding_test_agent() -> CodingTestAgent:
    """전역 코딩 테스트 Agent 인스턴스 반환"""
    global _global_agent
    if _global_agent is None:
        _global_agent = CodingTestAgent()
    return _global_agent
