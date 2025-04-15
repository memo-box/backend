from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from ai.settings import back_card_llm, topic_generation_llm
from ai.prompts import BACKCARD_GENERATION_PROMPT, TOPIC_GENERATION_PROMPT
from ai.schemas import BackcardResponse, TopicGenerationResponse


class GenerateBackCardUsecase:
    def __init__(self, llm: ChatOpenAI, prompt: str):
        self.llm = llm.with_structured_output(BackcardResponse)
        self.prompt = prompt

    def generate(
        self, front_card: str, source_language: str, target_language: str
    ) -> BackcardResponse:
        user_message = f"front_card:```{front_card}```, source_language:{source_language}, target_language:{target_language}"
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        return response


generate_back_card_usecase = GenerateBackCardUsecase(
    llm=back_card_llm, prompt=BACKCARD_GENERATION_PROMPT
)


class GenerateTopicUsecase:
    def __init__(self, llm: ChatOpenAI, prompt: str):
        self.llm = llm.with_structured_output(TopicGenerationResponse)
        self.prompt = prompt

    def generate(
        self, topic: str, source_language: str, target_language: str, count: int = 10
    ) -> TopicGenerationResponse:
        if count < 1:
            raise ValueError("Count must be greater than 0")
        if count > 50:
            raise ValueError("Count must be less than 50")
        user_message = f"topic:```{topic}```, source_language:{source_language}, target_language:{target_language}, count:{count}"
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        return response


generate_topic_usecase = GenerateTopicUsecase(
    llm=topic_generation_llm, prompt=TOPIC_GENERATION_PROMPT
)
