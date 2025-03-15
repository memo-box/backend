from models import LLMConfiguration
import getpass
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

back_card_setting = LLMConfiguration(
    model_name=os.getenv("OPENAI_MODEL_NAME"), temperature=1, max_tokens=1000
)

back_card_llm = ChatOpenAI(
    model=back_card_setting.model_name,
    temperature=back_card_setting.temperature,
    max_tokens=back_card_setting.max_tokens,
)
