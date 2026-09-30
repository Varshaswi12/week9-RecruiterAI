from typing import List, Dict

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobDescription
from app.services.matching_service import calculate_match_score


def rank_candidates(
    candidates: List[CandidateProfile],
    job: JobDescription
) -> List[Dict]:
    """
    Calculate match scores for multiple candidates
    and rank them from highest to lowest score.
    """

    ranked_candidates = []

    for candidate in candidates:

        match_result = calculate_match_score(
            candidate,
            job
        )

        ranked_candidates.append({
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "overall_score": match_result["overall_score"],
            "component_scores": match_result[
                "component_scores"
            ],
            "matching_skills": match_result[
                "matching_skills"
            ],
            "missing_skills": match_result[
                "missing_skills"
            ]
        })

    # Highest score first
    ranked_candidates.sort(
        key=lambda candidate: candidate["overall_score"],
        reverse=True
    )

    # Add ranking position
    for index, candidate in enumerate(
        ranked_candidates,
        start=1
    ):
        candidate["rank"] = index

    return ranked_candidates