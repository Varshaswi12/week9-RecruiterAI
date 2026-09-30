from pathlib import Path
import json
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Candidate, Resume

from app.services.document_processor import (
    DocumentProcessingError,
    extract_text,
)

from app.services.llm_service import (
    extract_candidate_profile,
)


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def parse_json(value):

    if not value:
        return []

    try:

        result = json.loads(value)

        if isinstance(result, list):
            return result

        return []

    except Exception:

        return []


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in {".pdf", ".docx"}:

        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF and DOCX files are allowed."
        )

    unique_filename = (
        f"{uuid.uuid4()}{extension}"
    )

    file_path = (
        UPLOAD_DIR / unique_filename
    )

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        extracted_text = extract_text(
            str(file_path)
        )

        candidate_profile = (
            await extract_candidate_profile(
                extracted_text
            )
        )

        candidate = Candidate(

            name=candidate_profile.name,

            email=candidate_profile.email,

            phone=candidate_profile.phone,

            skills=json.dumps(
                candidate_profile.skills
            ),

            experience=json.dumps(
                candidate_profile.experience
            ),

            education=json.dumps(
                candidate_profile.education
            ),

            projects=json.dumps(
                candidate_profile.projects
            ),

            certifications=json.dumps(
                candidate_profile.certifications
            )
        )

        db.add(candidate)

        db.commit()

        db.refresh(candidate)

        resume = Resume(

            candidate_id=candidate.id,

            original_filename=file.filename,

            stored_filename=unique_filename,

            file_type=extension,

            file_path=str(file_path),

            extracted_text=extracted_text
        )

        db.add(resume)

        db.commit()

        db.refresh(resume)

        return {

            "status": "success",

            "candidate": {

                "id": candidate.id,

                "name": candidate.name,

                "email": candidate.email,

                "phone": candidate.phone,

                "skills": candidate_profile.skills,

                "experience": candidate_profile.experience,

                "education": candidate_profile.education,

                "projects": candidate_profile.projects,

                "certifications":
                    candidate_profile.certifications
            },

            "resume": {

                "id": resume.id,

                "original_filename":
                    resume.original_filename,

                "stored_filename":
                    resume.stored_filename,

                "file_type":
                    resume.file_type,

                "characters_extracted":
                    len(extracted_text)
            },

            "message":
                "Resume uploaded, processed, and saved successfully."
        }

    except DocumentProcessingError as error:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except ValueError as error:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(error)}"
        )

    finally:

        await file.close()


@router.get("/candidates")
def get_candidates(
    db: Session = Depends(get_db)
):

    candidates = (
        db.query(Candidate)
        .order_by(
            Candidate.created_at.desc()
        )
        .all()
    )

    result = []

    for candidate in candidates:

        result.append({

            "id": candidate.id,

            "name": candidate.name,

            "email": candidate.email,

            "phone": candidate.phone,

            "skills": parse_json(
                candidate.skills
            ),

            "experience": parse_json(
                candidate.experience
            ),

            "education": parse_json(
                candidate.education
            ),

            "projects": parse_json(
                candidate.projects
            ),

            "certifications": parse_json(
                candidate.certifications
            ),

            "created_at":
                (
                    candidate.created_at.isoformat()
                    if candidate.created_at
                    else None
                )
        })

    return {

        "status": "success",

        "candidates": result,

        "count": len(result)
    }


@router.get("/candidates/{candidate_id}")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id
        )
        .first()
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    return {

        "status": "success",

        "candidate": {

            "id": candidate.id,

            "name": candidate.name,

            "email": candidate.email,

            "phone": candidate.phone,

            "skills": parse_json(
                candidate.skills
            ),

            "experience": parse_json(
                candidate.experience
            ),

            "education": parse_json(
                candidate.education
            ),

            "projects": parse_json(
                candidate.projects
            ),

            "certifications": parse_json(
                candidate.certifications
            )
        }
    }