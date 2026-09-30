import json
import re

import httpx

from app.schemas.candidate import CandidateProfile


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def extract_json(text: str) -> dict:
    """
    Extract a JSON object from the LLM response.
    """

    text = text.strip()

    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError(
            "No valid JSON object found in LLM response."
        )

    return json.loads(match.group())


async def extract_candidate_profile(
    resume_text: str
) -> CandidateProfile:

    prompt = f"""
You are a resume information extraction system.

Extract information from the resume below.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "name": "Candidate full name",
    "email": "Email or null",
    "phone": "Phone number or null",
    "skills": [],
    "experience": [],
    "education": [],
    "projects": [],
    "certifications": []
}}

Rules:
- Do not invent information.
- If information is missing, use null for email and phone.
- Use empty arrays when a section is missing.
- Keep skills concise.
- Keep experience as concise descriptions.
- Keep education as concise entries.
- Keep projects as concise entries.
- Keep certifications as concise entries.

RESUME:
{resume_text}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(
            timeout=180.0
        ) as client:

            response = await client.post(
                OLLAMA_URL,
                json=payload
            )

            response.raise_for_status()

            result = response.json()

        llm_response = result.get("response", "").strip()

        if not llm_response:
            raise ValueError(
                "LLM returned an empty response."
            )

        profile_data = extract_json(llm_response)

        return CandidateProfile(**profile_data)

    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running."
        ) from exc

    except httpx.TimeoutException as exc:
        raise RuntimeError(
            "Ollama request timed out. The local model may need more time."
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP {exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON."
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Candidate profile extraction failed: {str(exc)}"
        ) from exc