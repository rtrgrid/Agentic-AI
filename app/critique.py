from vertexai.generative_models import GenerativeModel
from pydantic import BaseModel, Field
from typing import List
import json

class CritiqueResult(BaseModel):
    complete: bool = Field(..., description="Whether the answer is comprehensive and accurate.")
    follow_ups: List[str] = Field(default_factory=list, description="Specific research questions to fill gaps.")
    critique_notes: str = Field(..., description="Internal analysis of the answer's quality.")

def critique_response(query, answer):
    """Verified stable critique using raw Vertex AI with structured JSON output."""
    critique_prompt = f"""
    You are an expert research critic.
    Analyze the following research answer carefully.
    
    Original Question: {query}
    Generated Answer: {answer}
    
    Your task:
    1. Identify missing information.
    2. Detect weak reasoning or incomplete evidence.
    3. Suggest follow-up research questions if gaps exist.
    
    Output a JSON object with this schema:
    {{
        "complete": boolean,
        "follow_ups": ["question 1", "question 2"],
        "critique_notes": "detailed analysis here"
    }}
    """
    
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        critique_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        data = json.loads(response.text)
        # Validation using Pydantic
        CritiqueResult(**data)
        return data
    except Exception as e:
        # Fallback if JSON fails
        return {
            "complete": "COMPLETE" in response.text.upper(),
            "follow_ups": [],
            "critique_notes": f"Parser error: {str(e)}"
        }
