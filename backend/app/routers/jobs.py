import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, User
from app.routers.auth import get_current_user
from app.services.jd_service import extract_job_requirements


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


class JobDescriptionRequest(BaseModel):
    text: str


def parse_json_list(value):
    if not value:
        return []

    try:
        parsed = json.loads(value)

        if isinstance(parsed, list):
            return parsed

        return []

    except Exception:
        return []


@router.post("/create")
async def create_job(
    request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    try:

        job_description = await extract_job_requirements(
            request.text
        )

        company = job_description.company

        if company == "null":
            company = None

        experience_required = (
            job_description.experience_required
        )

        if experience_required == "null":
            experience_required = None

        job = Job(
            user_id=current_user.id,
            title=job_description.title,
            company=company,
            description=request.text,
            required_skills=json.dumps(
                job_description.required_skills
            ),
            preferred_skills=json.dumps(
                job_description.preferred_skills
            ),
            experience_required=experience_required,
            education_required=json.dumps(
                job_description.education_required
            ),
            responsibilities=json.dumps(
                job_description.responsibilities
            ),
            qualifications=json.dumps(
                job_description.qualifications
            )
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return {
            "status": "success",
            "job": {
                "id": job.id,
                "user_id": job.user_id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "required_skills": job_description.required_skills,
                "preferred_skills": job_description.preferred_skills,
                "experience_required": job_description.experience_required,
                "education_required": job_description.education_required,
                "responsibilities": job_description.responsibilities,
                "qualifications": job_description.qualifications
            },
            "message": "Job created successfully."
        }

    except RuntimeError as error:

        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create job: {str(error)}"
        )


@router.post("/extract")
async def extract_job_description(
    request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user)
):

    if not request.text.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    try:

        job_description = await extract_job_requirements(
            request.text
        )

        return {
            "status": "success",
            "job_description": job_description.model_dump(),
            "message": "Job description processed successfully."
        }

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except ValueError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process job description: {str(error)}"
        )


@router.get("")
def get_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    jobs = (
        db.query(Job)
        .filter(Job.user_id == current_user.id)
        .order_by(Job.created_at.desc())
        .all()
    )

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "user_id": job.user_id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "required_skills": parse_json_list(
                job.required_skills
            ),
            "preferred_skills": parse_json_list(
                job.preferred_skills
            ),
            "experience_required": job.experience_required,
            "education_required": parse_json_list(
                job.education_required
            ),
            "responsibilities": parse_json_list(
                job.responsibilities
            ),
            "qualifications": parse_json_list(
                job.qualifications
            ),
            "created_at": (
                job.created_at.isoformat()
                if job.created_at
                else None
            )
        })

    return {
        "status": "success",
        "jobs": result,
        "count": len(result)
    }


@router.get("/{job_id}")
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.user_id == current_user.id
        )
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return {
        "status": "success",
        "job": {
            "id": job.id,
            "user_id": job.user_id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "required_skills": parse_json_list(
                job.required_skills
            ),
            "preferred_skills": parse_json_list(
                job.preferred_skills
            ),
            "experience_required": job.experience_required,
            "education_required": parse_json_list(
                job.education_required
            ),
            "responsibilities": parse_json_list(
                job.responsibilities
            ),
            "qualifications": parse_json_list(
                job.qualifications
            ),
            "created_at": (
                job.created_at.isoformat()
                if job.created_at
                else None
            )
        }
    }