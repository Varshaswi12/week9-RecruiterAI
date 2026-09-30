import json
import re

import httpx

from app.schemas.job import JobDescription


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def extract_json(text: str) -> dict:
    """
    Extract a JSON object from the LLM response.
    """

    text = text.strip()

    # Remove markdown code fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)

    # Find JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError(
            "No valid JSON object found in LLM response."
        )

    return json.loads(match.group())


async def extract_job_requirements(
    job_description_text: str
) -> JobDescription:
    """
    Extract structured job requirements from a job description
    using the local Ollama LLM.
    """

    prompt = f"""
You are a job description information extraction system.

Analyze the job description below and extract the structured
requirements.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "title": "Job title",
    "company": "Company name or null",
    "required_skills": [],
    "preferred_skills": [],
    "experience_required": "Experience requirement or null",
    "education_required": [],
    "responsibilities": [],
    "qualifications": []
}}

Rules:

- Do not invent information.
- If the company is not mentioned, use null.
- If experience is not mentioned, use null.
- Required skills are skills explicitly required for the role.
- Preferred skills are nice-to-have or preferred skills.
- Keep skills concise.
- Keep responsibilities concise.
- Keep qualifications concise.
- Preserve important technical requirements.
- Return empty arrays when information is not available.

JOB DESCRIPTION:
{job_description_text}
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

        llm_response = result.get(
            "response",
            ""
        ).strip()

        if not llm_response:
            raise ValueError(
                "LLM returned an empty response."
            )

        job_data = extract_json(
            llm_response
        )

        return JobDescription(
            **job_data
        )

    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from exc

    except httpx.TimeoutException as exc:
        raise RuntimeError(
            "Ollama request timed out."
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON."
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Job description extraction failed: "
            f"{str(exc)}"
        ) from exc