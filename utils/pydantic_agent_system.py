import os
from typing import List, Dict
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from Constants import Constants

# Ensure the OpenAI compatible environment variables are set for local models
os.environ.setdefault("OPENAI_BASE_URL", Constants.LLM_URL)
os.environ.setdefault("OPENAI_API_KEY", "local-key")


class PersonName(BaseModel):
    first_name: str = Field(alias="First Name")
    last_name: str = Field(alias="Last Name")


class NamesPayload(BaseModel):
    names: List[PersonName]


class NameExtractionAgent:
    """Multi-agent system for extracting and validating names."""

    def __init__(self) -> None:
        self.extract_agent = Agent(
            model=f"openai:{Constants.MODEL_NAME}",
            system_prompt=Constants.SYSTEM_PROMPT,
            output_type=NamesPayload,
        )
        self.verify_agent = Agent(
            model=f"openai:{Constants.MODEL_NAME}",
            system_prompt=(
                "You verify that the provided JSON only contains names of persons "
                "that are referenced in the given text. Remove entries that are not "
                "person names and return the corrected JSON using the same schema."
            ),
            output_type=NamesPayload,
        )

    def process_chunk(self, text: str) -> List[Dict[str, str]]:
        """Run extraction and validation agents on a text chunk."""
        extraction_prompt = Constants.USER_BASE_PROMPT + text
        extraction_result = self.extract_agent.run_sync(extraction_prompt)
        candidates = extraction_result.output.names
        if not candidates:
            return []

        candidate_json = [n.model_dump(by_alias=True) for n in candidates]
        validation_prompt = (
            f"Text:\n{text}\n\nCandidates: {candidate_json}\n"
            "Return the valid names as JSON."
        )
        verified = self.verify_agent.run_sync(validation_prompt)
        return [n.model_dump(by_alias=True) for n in verified.output.names]