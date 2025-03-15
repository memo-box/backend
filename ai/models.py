import typing
import dataclasses


@dataclasses.dataclass
class LLMConfiguration:
    model_name: str
    temperature: float
    model_kwargs: typing.Dict = dataclasses.field(default_factory=dict)
    max_tokens: int = 2000
    top_p: typing.Optional[float] = None
    frequency_penalty: typing.Optional[float] = None
    presence_penalty: typing.Optional[float] = None
