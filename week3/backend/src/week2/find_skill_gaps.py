import sqlite3
import re   # for regex matching
from typing import List, Set   # type hinting for better code clarity
from pydantic import BaseModel # for structured result representation

ALIASES = {
    "c/c++": ["c", "c++"],
    "git/github": ["git", "github"],
    "js": ["javascript"],
    "py": ["python"],
    "ts": ["typescript"]
}   # known aliases for better skill matching

class SkillGapResult(BaseModel):
    """
    Structured result for skill gap analysis.
    - gaps: List of skills that are in the market but not in the resume.
    - resume_skills: List of skills found in the resume.
    - market_skills: List of skills found in the market (job postings).
    """
    gaps: List[str]     # easier to sort output
    resume_skills: List[str]
    market_skills: List[str]

def normalize(skill: str) -> str:
    """
    Normalize skill names for better matching, and avoid false skill gaps due to formatting differences.
    """
    return skill.strip().lower()

def load_resume(file_path: str) -> str:
    """
    Load the resume text from a file to read. If any error occurs, return an empty string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().lower()  # convert to lowercase for case-insensitive matching
    except Exception:
        return ""

def extract_resume_skills(resume_text: str, market_skills: Set[str]) -> Set[str]:
    """
    Extract skills from the resume text that are present in the market skills set.
    """
    match = set()   # to avoid duplicates and for efficient comparison

    for skill in market_skills:
        
        skill = normalize(skill)   # normalize the skill name for better matching
        
        if skill in ALIASES:
            # for skills with known aliases
            for alias in ALIASES[skill]:
                # use regex to match the skill as whole words, to avoid false positives (e.g., "sql" in "nosql")
                pattern = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"      # "(?<!\w)" is negative lookbehind to ensure the preceding character is not a word character [a-zA-Z0-9_], and "(?!\w)" is negative lookahead to ensure the following character is not a word character, re.escape safely handle special characters in skill names (e.g., "c++")

                # if match in the resume text
                if re.search(pattern, resume_text):
                    match.add(alias)  # add the skill name to the match set
                    break   # if any alias matches, we can stop checking other aliases for this skill
        else:
            pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"    
            
            if re.search(pattern, resume_text):
                match.add(skill)
            
    return match

def load_market_skills(db_url: str) -> Set[str]:
    """
    Build a set of market skills by getting all tech_stack entries, splitting them by comma, normalizing them, and collecting unique skills.
    """
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    # get all non-null tech_stack entries
    cursor.execute("SELECT tech_stack FROM jobs WHERE tech_stack IS NOT NULL")
    rows = cursor.fetchall()  

    skills = set()  # to store unique skills from the market job postings

    for row in rows:
        if not row[0]:  # if tech_stack is empty string, skip
            continue

        parts = row[0].split(",")   # split the tech_stack string by comma 

        for p in parts:
            cleaned = normalize(p)  # normalize the skill name
            
            if cleaned:     # if non-empty 
                if cleaned in ALIASES:
                    for alias in ALIASES[cleaned]:
                        skills.add(alias)
                else:
                    skills.add(cleaned)     # add to the set of market skills

    conn.close()
    return skills

def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    """
    Main function to find skill gaps between the resume and the market.
     - Load resume text and market skills
     - Extract the skills from the resume that exist in the market skills
     - Get the skill gaps as the difference between market skills and resume skills
     - Return the results in a structured format using SkillGapResult
     - Handle any exceptions and return empty results if any error occurs 
     
     Input:
        - input_file_path: path to the resume text file
        - db_url: path to the SQLite database containing job postings 
    Output:
        - SkillGapResult object containing the skill gaps, resume skills, and market skills
    """
    
    try:
        resume_text = load_resume(input_file_path)

        market_skills = load_market_skills(db_url)

        resume_skills = extract_resume_skills(resume_text, market_skills)

        # deterministic comparison
        # the difference between market skills and resume skills
        # e.g., if market has {python, sql, aws} and resume has {python, sql}, the gap is {aws}
        gaps = sorted(list(market_skills - resume_skills))
    
        # return in a structured format
        return SkillGapResult(
            gaps=gaps,
            resume_skills=sorted(list(resume_skills)),
            market_skills=sorted(list(market_skills))
        )

    except Exception:
        return SkillGapResult(
            gaps=[],
            resume_skills=[],
            market_skills=[]
        )   # avoid crashing the program and provide a consistent output format

def main():
    # result = find_skill_gaps("data/resume_d3_eval.txt", "data/jobs_d3_eval.db")
    result = find_skill_gaps("data/resume_d3.txt", "../week1/data/3_gold/jobs.db")
    print(result.model_dump())   # export model fields, convert Pydantic model object to dictionary, which can be easily converted to JSON if needed, and is more readable
    
if __name__ == "__main__":
    main()