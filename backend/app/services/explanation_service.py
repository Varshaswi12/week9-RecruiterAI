import json
import httpx

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobDescription


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def value_to_text(value):
    """
    Convert strings, dictionaries, lists and other values
    into readable text for the LLM.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return " ".join(
            str(item)
            for item in value.values()
            if item is not None
        )

    if isinstance(value, list):
        return " ".join(
            value_to_text(item)
            for item in value
            if item is not None
        )

    return str(value)


def list_to_text(values):
    """
    Convert a list of strings/dictionaries into readable text.
    """

    if not values:
        return "None"

    return "\n".join(
        f"- {value_to_text(value)}"
        for value in values
        if value_to_text(value).strip()
    )


async def generate_match_explanation(
    candidate: CandidateProfile,
    job: JobDescription,
    match_result: dict
) -> str:

    candidate_skills = list_to_text(
        candidate.skills
    )

    candidate_experience = list_to_text(
        candidate.experience
    )

    candidate_education = list_to_text(
        candidate.education
    )

    candidate_projects = list_to_text(
        candidate.projects
    )

    candidate_certifications = list_to_text(
        candidate.certifications
    )

    required_skills = list_to_text(
        job.required_skills
    )

    preferred_skills = list_to_text(
        job.preferred_skills
    )

    education_required = list_to_text(
        job.education_required
    )

    responsibilities = list_to_text(
        job.responsibilities
    )

    qualifications = list_to_text(
        job.qualifications
    )

    component_scores = match_result.get(
        "component_scores",
        {}
    )

    matching_skills = list_to_text(
        match_result.get(
            "matching_skills",
            []
        )
    )

    missing_skills = list_to_text(
        match_result.get(
            "missing_skills",
            []
        )
    )

    prompt = f"""
You are an AI recruitment analysis assistant.

Analyze the candidate against the job description.

Do NOT invent information.

Use only the candidate and job information provided below.

CANDIDATE
=========

Name:
{candidate.name}

Email:
{candidate.email or "Not provided"}

Skills:
{candidate_skills}

Experience:
{candidate_experience}

Education:
{candidate_education}

Projects:
{candidate_projects}

Certifications:
{candidate_certifications}


JOB
===

Title:
{job.title}

Company:
{job.company or "Not provided"}

Required Skills:
{required_skills}

Preferred Skills:
{preferred_skills}

Experience Required:
{job.experience_required or "Not specified"}

Education Required:
{education_required}

Responsibilities:
{responsibilities}

Qualifications:
{qualifications}


MATCHING RESULTS
================

Overall Score:
{match_result.get("overall_score", 0)}

Required Skills Score:
{component_scores.get("required_skills", 0)}

Relevant Experience Score:
{component_scores.get("relevant_experience", 0)}

Projects Score:
{component_scores.get("projects", 0)}

Education and Certification Score:
{component_scores.get("education_certifications", 0)}

Additional Skills Score:
{component_scores.get("additional_skills", 0)}

Matching Skills:
{matching_skills}

Missing Skills:
{missing_skills}


TASK
====

Generate a concise professional recruitment analysis.

Use exactly these sections:

1. Overall Assessment
2. Matching Strengths
3. Skill Gaps
4. Experience and Project Relevance
5. Final Summary

Explain the results based on the provided evidence.

Do not make hiring decisions.

Do not invent experience, skills, education or certifications.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
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

        explanation = result.get(
            "response",
            ""
        ).strip()

        if not explanation:
            raise ValueError(
                "LLM returned an empty explanation."
            )

        return explanation

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

    except Exception as exc:

        raise RuntimeError(
            f"AI explanation generation failed: {str(exc)}"
        ) from exc