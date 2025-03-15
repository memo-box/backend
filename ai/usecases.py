from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from ai.settings import back_card_llm
from ai.prompts import BACKCARD_GENERATION_PROMPT


class GenerateBackCardUsecase:
    def __init__(self, llm: ChatOpenAI, prompt: str):
        self.llm = llm
        self.prompt = prompt

    def generate(
        self, front_card: str, source_language: str, target_language: str
    ) -> str:
        user_message = f"front_card:```{front_card}```, source_language:{source_language}, target_language:{target_language}"
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        return response.content


generate_back_card_usecase = GenerateBackCardUsecase(
    llm=back_card_llm, prompt=BACKCARD_GENERATION_PROMPT
)
