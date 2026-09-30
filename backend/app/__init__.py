from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    description = Column(Text, nullable=False)
    required_skills = Column(Text)
    preferred_skills = Column(Text)
    experience_required = Column(String(255))
    created_at = Column(DateTime, server_default=func.current_timestamp())


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)
    projects = Column(Text)
    certifications = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_path = Column(Text, nullable=False)
    extracted_text = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    overall_score = Column(Numeric(5, 2), nullable=False)
    required_skills_score = Column(Numeric(5, 2))
    experience_score = Column(Numeric(5, 2))
    projects_score = Column(Numeric(5, 2))
    education_score = Column(Numeric(5, 2))
    additional_skills_score = Column(Numeric(5, 2))

    matching_skills = Column(Text)
    missing_skills = Column(Text)
    ai_explanation = Column(Text)

    created_at = Column(DateTime, server_default=func.current_timestamp())