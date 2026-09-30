from typing import List, Optional

from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    title: str = Field(
        default="Unknown",
        description="Job title"
    )

    company: Optional[str] = Field(
        default=None,
        description="Company name"
    )

    required_skills: List[str] = Field(
        default_factory=list,
        description="Required technical and professional skills"
    )

    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Preferred or nice-to-have skills"
    )

    experience_required: Optional[str] = Field(
        default=None,
        description="Required years or type of experience"
    )

    education_required: List[str] = Field(
        default_factory=list,
        description="Required educational qualifications"
    )

    responsibilities: List[str] = Field(
        default_factory=list,
        description="Main responsibilities of the role"
    )

    qualifications: List[str] = Field(
        default_factory=list,
        description="Other qualifications or requirements"
    )