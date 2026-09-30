from typing import List, Optional, Union, Dict, Any

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str = Field(
        default="Unknown",
        description="Candidate's full name"
    )

    email: Optional[str] = Field(
        default=None,
        description="Candidate's email"
    )

    phone: Optional[str] = Field(
        default=None,
        description="Candidate's phone"
    )

    skills: List[str] = Field(
        default_factory=list,
        description="Technical and professional skills"
    )

    experience: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list,
        description="Candidate's work experience"
    )

    education: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list,
        description="Candidate's educational qualifications"
    )

    projects: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list,
        description="Candidate's projects"
    )

    certifications: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list,
        description="Candidate's certifications"
    )