DStarix RecruitAI

AI-powered recruitment and candidate matching platform that extracts structured information from job descriptions and resumes, performs semantic candidate matching, ranks candidates, identifies skill gaps, and generates AI-based recruitment analysis.



Overview

DStarix RecruitAI is a full-stack AI recruitment platform designed to simplify the candidate screening and matching process.

The platform allows recruiters to:

- Create and manage job descriptions
- Extract structured job requirements using an LLM
- Upload candidate resumes
- Process PDF and DOCX resumes
- Extract structured candidate information using an LLM
- Compare candidates against job requirements
- Calculate weighted candidate match scores
- Identify matching and missing skills
- Rank multiple candidates
- Generate AI-powered candidate analysis
- Store recruiter, job, candidate, resume, and matching data in PostgreSQL



Key Features

Job Description Processing

Recruiters can enter a job description and the system extracts:

- Job title
- Company
- Required skills
- Preferred skills
- Experience requirements
- Education requirements
- Responsibilities
- Qualifications

The extraction is performed using a local LLM through Ollama.



Resume Processing

The platform supports:

- PDF resumes
- DOCX resumes

The document processing pipeline:

```text
Resume Upload
      ↓
File Validation
      ↓
Text Extraction
      ↓
LLM Information Extraction
      ↓
Structured Candidate Profile
      ↓
PostgreSQL Storage
