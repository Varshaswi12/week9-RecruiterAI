import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Candidate, Job, MatchResult

from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobDescription

from app.services.matching_service import calculate_match_score
from app.services.ranking_service import rank_candidates
from app.services.explanation_service import generate_match_explanation


router = APIRouter(
    prefix="/matching",
    tags=["Matching"]
)


def parse_list_field(value):
    if not value:
        return []

    try:
        parsed = json.loads(value)

        if isinstance(parsed, list):
            return parsed

    except (json.JSONDecodeError, TypeError):
        pass

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def candidate_to_profile(candidate):
    return CandidateProfile(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        skills=parse_list_field(candidate.skills),
        experience=parse_list_field(candidate.experience),
        education=parse_list_field(candidate.education),
        projects=parse_list_field(candidate.projects),
        certifications=parse_list_field(candidate.certifications)
    )


def job_to_profile(job):
    return JobDescription(
        title=job.title,
        company=job.company,
        required_skills=parse_list_field(job.required_skills),
        preferred_skills=parse_list_field(job.preferred_skills),
        experience_required=job.experience_required,
        education_required=[],
        responsibilities=[],
        qualifications=[]
    )


class MatchingRequest(BaseModel):
    candidate: CandidateProfile
    job: JobDescription


class RankingRequest(BaseModel):
    candidates: list[CandidateProfile]
    job: JobDescription


class DatabaseMatchingRequest(BaseModel):
    job_id: int
    candidate_id: int


@router.post("/score")
async def calculate_candidate_match(
    request: MatchingRequest
):
    try:
        result = calculate_match_score(
            request.candidate,
            request.job
        )

        return {
            "status": "success",
            "match_result": result,
            "message": "Candidate matching completed successfully."
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Matching failed: {str(error)}"
        )


@router.post("/rank")
async def rank_multiple_candidates(
    request: RankingRequest
):
    if not request.candidates:
        raise HTTPException(
            status_code=400,
            detail="At least one candidate is required."
        )

    try:
        ranked_candidates = rank_candidates(
            request.candidates,
            request.job
        )

        return {
            "status": "success",
            "total_candidates": len(ranked_candidates),
            "ranked_candidates": ranked_candidates,
            "message": "Candidates ranked successfully."
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Candidate ranking failed: {str(error)}"
        )


@router.post("/explain")
async def explain_candidate_match(
    request: MatchingRequest
):
    try:
        match_result = calculate_match_score(
            request.candidate,
            request.job
        )

        explanation = await generate_match_explanation(
            request.candidate,
            request.job,
            match_result
        )

        return {
            "status": "success",
            "match_result": match_result,
            "ai_explanation": explanation,
            "message": "AI match explanation generated successfully."
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation generation failed: {str(error)}"
        )


@router.post("/run")
async def run_database_matching(
    request: DatabaseMatchingRequest,
    db: Session = Depends(get_db)
):
    try:

        job = (
            db.query(Job)
            .filter(Job.id == request.job_id)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job with id {request.job_id} was not found."
            )

        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == request.candidate_id)
            .first()
        )

        if not candidate:
            raise HTTPException(
                status_code=404,
                detail=f"Candidate with id {request.candidate_id} was not found."
            )

        candidate_profile = candidate_to_profile(candidate)
        job_description = job_to_profile(job)

        match_result = calculate_match_score(
            candidate_profile,
            job_description
        )

        explanation = await generate_match_explanation(
            candidate_profile,
            job_description,
            match_result
        )

        database_result = MatchResult(
            job_id=job.id,
            candidate_id=candidate.id,
            overall_score=match_result["overall_score"],
            required_skills_score=match_result["component_scores"]["required_skills"],
            experience_score=match_result["component_scores"]["relevant_experience"],
            projects_score=match_result["component_scores"]["projects"],
            education_score=match_result["component_scores"]["education_certifications"],
            additional_skills_score=match_result["component_scores"]["additional_skills"],
            matching_skills=json.dumps(match_result["matching_skills"]),
            missing_skills=json.dumps(match_result["missing_skills"]),
            ai_explanation=explanation
        )

        db.add(database_result)
        db.commit()
        db.refresh(database_result)

        return {
            "status": "success",
            "match": {
                "match_result_id": database_result.id,
                "job_id": job.id,
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "job_title": job.title,
                "overall_score": match_result["overall_score"],
                "component_scores": match_result["component_scores"],
                "matching_skills": match_result["matching_skills"],
                "missing_skills": match_result["missing_skills"],
                "ai_explanation": explanation
            },
            "message": "Candidate matched successfully."
        }

    except HTTPException:
        db.rollback()
        raise

    except RuntimeError as error:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database matching failed: {str(error)}"
        )


@router.get("/job/{job_id}/rank")
async def rank_candidates_for_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all candidates from PostgreSQL and rank them
    against the selected job.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job with id {job_id} was not found."
        )

    candidates = db.query(Candidate).all()

    if not candidates:
        return {
            "status": "success",
            "job_id": job_id,
            "total_candidates": 0,
            "ranked_candidates": []
        }

    job_description = job_to_profile(job)

    candidate_profiles = [
        candidate_to_profile(candidate)
        for candidate in candidates
    ]

    ranked = rank_candidates(
        candidate_profiles,
        job_description
    )

    return {
        "status": "success",
        "job_id": job.id,
        "job_title": job.title,
        "total_candidates": len(ranked),
        "ranked_candidates": ranked,
        "message": "Candidates ranked successfully."
    }