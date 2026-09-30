from typing import Any, Dict, List, Tuple

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobDescription
from app.services.embedding_service import embedding_service


# ============================================================
# MATCHING WEIGHTS
# ============================================================

REQUIRED_SKILLS_WEIGHT = 40
EXPERIENCE_WEIGHT = 25
PROJECTS_WEIGHT = 20
EDUCATION_CERTIFICATIONS_WEIGHT = 10
ADDITIONAL_SKILLS_WEIGHT = 5


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def value_to_text(value: Any) -> str:
    """
    Convert strings, dictionaries, lists and other values
    into searchable text.

    This prevents errors when the LLM returns structured
    dictionaries instead of plain strings.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        parts = []

        for key, item in value.items():
            if item is not None:
                parts.append(str(item))

        return " ".join(parts).strip()

    if isinstance(value, list):
        return " ".join(
            value_to_text(item)
            for item in value
            if item is not None
        ).strip()

    return str(value).strip()


def normalize_skill(skill: Any) -> str:
    """
    Normalize a skill for exact comparison.
    """

    return value_to_text(skill).lower().strip()


def normalize_skills(skills: List[Any]) -> List[str]:
    """
    Convert all skills to normalized strings.
    """

    result = []

    for skill in skills or []:
        normalized = normalize_skill(skill)

        if normalized:
            result.append(normalized)

    return result


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def semantic_similarity(
    candidate_text: str,
    job_text: str
) -> float:
    """
    Calculate cosine similarity using normalized
    Sentence Transformer embeddings.

    Returns a value between 0 and 1.
    """

    candidate_text = value_to_text(candidate_text)
    job_text = value_to_text(job_text)

    if not candidate_text or not job_text:
        return 0.0

    candidate_embedding = embedding_service.generate_embedding(
        candidate_text
    )

    job_embedding = embedding_service.generate_embedding(
        job_text
    )

    similarity = sum(
        a * b
        for a, b in zip(
            candidate_embedding,
            job_embedding
        )
    )

    # Embeddings are normalized, therefore the dot product
    # represents cosine similarity.

    similarity = max(0.0, min(1.0, similarity))

    return similarity


# ============================================================
# REQUIRED SKILL MATCHING
# ============================================================

def calculate_skill_match(
    candidate_skills: List[Any],
    required_skills: List[Any]
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate required skill score.

    70% exact skill matching
    30% semantic similarity
    """

    candidate_normalized = normalize_skills(
        candidate_skills
    )

    required_normalized = normalize_skills(
        required_skills
    )

    if not required_normalized:
        return 100.0, [], []

    matching_skills = []
    missing_skills = []

    # --------------------------------------------------------
    # Exact matching
    # --------------------------------------------------------

    exact_matches = 0

    for original_required, required in zip(
        required_skills,
        required_normalized
    ):
        found = False

        for candidate in candidate_normalized:

            if (
                candidate == required
                or candidate in required
                or required in candidate
            ):
                found = True
                break

        if found:
            matching_skills.append(
                value_to_text(original_required)
            )
            exact_matches += 1
        else:
            missing_skills.append(
                value_to_text(original_required)
            )

    exact_score = (
        exact_matches / len(required_normalized)
    ) * 100

    # --------------------------------------------------------
    # Semantic matching
    # --------------------------------------------------------

    candidate_skill_text = " ".join(
        candidate_normalized
    )

    required_skill_text = " ".join(
        required_normalized
    )

    semantic_score = (
        semantic_similarity(
            candidate_skill_text,
            required_skill_text
        )
        * 100
    )

    final_score = (
        exact_score * 0.70
        + semantic_score * 0.30
    )

    return (
        round(final_score, 2),
        matching_skills,
        missing_skills
    )


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def calculate_experience_score(
    candidate_experience: List[Any],
    required_experience: Any
) -> float:
    """
    Compare candidate experience with job experience
    requirements using semantic similarity.
    """

    candidate_text = value_to_text(
        candidate_experience
    )

    job_text = value_to_text(
        required_experience
    )

    if not candidate_text or not job_text:
        return 0.0

    score = semantic_similarity(
        candidate_text,
        job_text
    )

    return round(score * 100, 2)


# ============================================================
# PROJECT MATCHING
# ============================================================

def calculate_project_score(
    candidate_projects: List[Any],
    job_responsibilities: List[Any]
) -> float:
    """
    Compare candidate projects against job responsibilities.
    """

    candidate_text = value_to_text(
        candidate_projects
    )

    job_text = value_to_text(
        job_responsibilities
    )

    if not candidate_text or not job_text:
        return 0.0

    score = semantic_similarity(
        candidate_text,
        job_text
    )

    return round(score * 100, 2)


# ============================================================
# EDUCATION + CERTIFICATION MATCHING
# ============================================================

def calculate_education_certification_score(
    candidate_education: List[Any],
    candidate_certifications: List[Any],
    job_education: List[Any],
    job_qualifications: List[Any]
) -> float:
    """
    Compare education and certifications with the
    job's educational and qualification requirements.
    """

    candidate_text = value_to_text(
        candidate_education
    )

    certification_text = value_to_text(
        candidate_certifications
    )

    job_education_text = value_to_text(
        job_education
    )

    qualification_text = value_to_text(
        job_qualifications
    )

    candidate_combined = " ".join(
        part
        for part in [
            candidate_text,
            certification_text
        ]
        if part
    )

    job_combined = " ".join(
        part
        for part in [
            job_education_text,
            qualification_text
        ]
        if part
    )

    if not candidate_combined or not job_combined:
        return 0.0

    score = semantic_similarity(
        candidate_combined,
        job_combined
    )

    return round(score * 100, 2)


# ============================================================
# ADDITIONAL / PREFERRED SKILLS
# ============================================================

def calculate_additional_skill_score(
    candidate_skills: List[Any],
    preferred_skills: List[Any]
) -> float:
    """
    Calculate matching percentage for preferred skills.
    """

    candidate_normalized = normalize_skills(
        candidate_skills
    )

    preferred_normalized = normalize_skills(
        preferred_skills
    )

    if not preferred_normalized:
        return 0.0

    matched = 0

    for preferred in preferred_normalized:

        for candidate in candidate_normalized:

            if (
                candidate == preferred
                or candidate in preferred
                or preferred in candidate
            ):
                matched += 1
                break

    score = (
        matched / len(preferred_normalized)
    ) * 100

    return round(score, 2)


# ============================================================
# COMPLETE MATCH SCORE
# ============================================================

def calculate_match_score(
    candidate: CandidateProfile,
    job: JobDescription
) -> Dict[str, Any]:
    """
    Calculate the complete candidate-job match.

    Weighting:

    Required Skills              = 40%
    Relevant Experience          = 25%
    Projects                    = 20%
    Education + Certifications  = 10%
    Additional Skills            = 5%
    """

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    required_skill_score, matching_skills, missing_skills = (
        calculate_skill_match(
            candidate.skills,
            job.required_skills
        )
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_score = calculate_experience_score(
        candidate.experience,
        job.experience_required
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    project_score = calculate_project_score(
        candidate.projects,
        job.responsibilities
    )

    # --------------------------------------------------------
    # Education + Certifications
    # --------------------------------------------------------

    education_score = (
        calculate_education_certification_score(
            candidate.education,
            candidate.certifications,
            job.education_required,
            job.qualifications
        )
    )

    # --------------------------------------------------------
    # Additional skills
    # --------------------------------------------------------

    additional_skill_score = (
        calculate_additional_skill_score(
            candidate.skills,
            job.preferred_skills
        )
    )

    # --------------------------------------------------------
    # Weighted overall score
    # --------------------------------------------------------

    overall_score = (
        required_skill_score
        * (REQUIRED_SKILLS_WEIGHT / 100)
        +
        experience_score
        * (EXPERIENCE_WEIGHT / 100)
        +
        project_score
        * (PROJECTS_WEIGHT / 100)
        +
        education_score
        * (EDUCATION_CERTIFICATIONS_WEIGHT / 100)
        +
        additional_skill_score
        * (ADDITIONAL_SKILLS_WEIGHT / 100)
    )

    overall_score = round(
        overall_score,
        2
    )

    return {
        "overall_score": overall_score,

        "component_scores": {
            "required_skills": required_skill_score,
            "relevant_experience": experience_score,
            "projects": project_score,
            "education_certifications": education_score,
            "additional_skills": additional_skill_score
        },

        "matching_skills": matching_skills,

        "missing_skills": missing_skills
    }