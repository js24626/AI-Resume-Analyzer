import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-120b"

RESUME_SCHEMA = """{
  "name": "candidate name",
  "skills": ["skill1", "skill2"],
  "years_experience": 0,
  "education": "highest degree and field",
  "job_titles": ["previous job titles"]
}"""

JOB_SCHEMA = """{
  "required_skills": ["skill1", "skill2"],
  "nice_to_have_skills": ["skill1", "skill2"],
  "min_years_experience": 0
}"""

_client = None


def get_client() -> Groq:
    """Create the Groq client lazily so a missing key gives a readable error."""
    global _client
    if _client is None:
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file "
                "(copy .env.example) or export it as an environment variable."
            )
        _client = Groq()
    return _client


def _to_json(raw: str) -> dict:
    """Parse a model reply into a dict, tolerating prose or markdown fences."""
    cleaned = (raw or "").strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fall back to the outermost {...} block, which drops any surrounding prose.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"Model did not return JSON. Raw reply: {raw[:300]!r}")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse JSON from the model reply: {exc}") from exc


def _chat_json(prompt: str) -> dict:
    """Send a prompt and return the parsed JSON object from the reply."""
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return _to_json(response.choices[0].message.content)


def _as_skill_list(value) -> list:
    """Coerce whatever the model returned into a clean list of skill strings."""
    if isinstance(value, str):
        value = [part.strip() for part in re.split(r"[,\n;]", value)]
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _as_number(value, default: int = 0) -> float:
    """Coerce a possibly missing / text year value into a number."""
    if isinstance(value, bool) or value is None:
        return default
    if isinstance(value, (int, float)):
        return value
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else default


def extract_resume_data(resume_text: str) -> dict:
    """Ask the LLM to pull structured info out of raw resume text."""
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty - nothing to extract.")

    prompt = f"""
Extract the following from this resume and return ONLY valid JSON, no extra text:
{RESUME_SCHEMA}

Resume:
{resume_text}
"""
    data = _chat_json(prompt)
    data["skills"] = _as_skill_list(data.get("skills"))
    data["job_titles"] = _as_skill_list(data.get("job_titles"))
    data["years_experience"] = _as_number(data.get("years_experience", 0))
    data.setdefault("name", "")
    data.setdefault("education", "")
    return data


def extract_job_requirements(job_description: str) -> dict:
    """Ask the LLM to pull required skills out of a job posting."""
    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty - nothing to extract.")

    prompt = f"""
Extract the following from this job description and return ONLY valid JSON, no extra text:
{JOB_SCHEMA}

Job description:
{job_description}
"""
    data = _chat_json(prompt)
    data["required_skills"] = _as_skill_list(data.get("required_skills"))
    data["nice_to_have_skills"] = _as_skill_list(data.get("nice_to_have_skills"))
    data["min_years_experience"] = _as_number(data.get("min_years_experience", 0))
    return data


def calculate_match(resume_data: dict, job_data: dict) -> dict:
    """Compare resume skills against job requirements and score the match.

    Scoring rule is unchanged: the percentage is the share of required skills
    that appear in the resume. Matching is exact-after-normalisation, so
    synonyms such as "JS" vs "JavaScript" are not unified.
    """
    resume_skills = {s.lower().strip() for s in _as_skill_list(resume_data.get("skills"))}
    required = {s.lower().strip() for s in _as_skill_list(job_data.get("required_skills"))}
    nice_to_have = {
        s.lower().strip() for s in _as_skill_list(job_data.get("nice_to_have_skills"))
    }

    matched_required = resume_skills & required
    missing_required = required - resume_skills
    matched_nice = resume_skills & nice_to_have

    required_score = len(matched_required) / len(required) * 100 if required else 100

    years = _as_number(resume_data.get("years_experience", 0))
    needed = _as_number(job_data.get("min_years_experience", 0))
    experience_ok = years >= needed

    return {
        "match_percentage": round(required_score, 1),
        "matched_required_skills": sorted(matched_required),
        "missing_required_skills": sorted(missing_required),
        "matched_nice_to_have": sorted(matched_nice),
        "meets_experience": experience_ok,
    }