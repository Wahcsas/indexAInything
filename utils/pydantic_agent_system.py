import os
from typing import List, Dict

from pydantic import BaseModel, Field
from pydantic_ai import Agent, UnexpectedModelBehavior, capture_run_messages, NativeOutput
from pydantic_ai.settings import ModelSettings
from pydantic_ai.exceptions import UnexpectedModelBehavior

from Constants import Constants
from pprint import pprint



os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4318'
os.environ.setdefault("OPENAI_BASE_URL", Constants.LLM_URL)
os.environ.setdefault("OPENAI_API_KEY", "local-key")




class PersonName(BaseModel):
    # first_name: Optional[str] = Field(default="-", alias="First_Name")
    # last_name: Optional[str] = Field(default="-", alias="Last_Name")
    first_name: str = Field(default="-", alias="First_Name")
    last_name: str = Field(default="-", alias="Last_Name")
    model_config = {"populate_by_name": True}


class NamesPayload(BaseModel):
    names: List[PersonName]


class NameExtractionAgent:
    """Multi-agent system for extracting and validating names."""

    def __init__(self) -> None:
        self.extract_agent = Agent(
            #error here evtl . agent not init with openai: in front
            model=f"openai:{Constants.MODEL_NAME}",
            system_prompt=Constants.SYSTEM_PROMPT,
            #instructions=Constants.SYSTEM_PROMPT,  # TODO: Check dif between system_prompt vs. instructions
            output_type=NativeOutput(NamesPayload),
            retries=2,
            history_processors=[debug_history]
        )
        self.model_settings = ModelSettings()
        self.model_settings['temperature'] = 0.0


    def process_chunk(self, text: str) -> List[Dict[str, str]]:
        """Run extraction and validation agents on a text chunk."""
        extraction_prompt = Constants.USER_BASE_PROMPT +  "```" + text + "```"
        try:
            extraction_result = self.extract_agent.run_sync(extraction_prompt, model_settings=self.model_settings)
            pprint(extraction_result.output.names)
            candidates = extraction_result.output.names
        except UnexpectedModelBehavior:
            with capture_run_messages() as messages:
                print(f"Extract agent: {messages}")
            candidates = None

        if not candidates:
            return []

        return [n.model_dump(by_alias=True) for n in extraction_result.output.names]


def debug_history(history):
    print("\n--- About to send history to model ---")
    for msg in history:
        # Different message types may expose content differently; be defensive.
        parts = getattr(msg, "parts", None)
        for part in parts:
            content = getattr(part, 'content', None)
            print(f"\n{part.part_kind.upper()}: \n {content}")
    print("*"*25)
    return history  # must return it unmodified

