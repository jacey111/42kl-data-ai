from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from src.week2.find_skill_gaps import find_skill_gaps
from src.week2.prompt_model import prompt_model

import tempfile

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    resume_text: str

@app.post("/chat") 
async def chat(request: ChatRequest):

    try:

        # save resume text temporarily
        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".txt",
            encoding="utf-8"
        ) as temp_file:

            temp_file.write(request.resume_text)

            temp_path = temp_file.name

        skill_keywords = [
            "resume",
            "skill",
            "skills",
            "gap",
            "analyze",
            "analyse",
            "cv",
            "job"
        ]

        is_skill_request = any(msg in request.message.lower() for msg in skill_keywords)    
        
        if is_skill_request or request.resume_text:
            
            # resume analysis route, call find_skill_gaps function
            result = find_skill_gaps(
                input_file_path=temp_path,
                db_url="src/week2/data/jobs_d3_eval.db"
            )

            response_text = (
                f"Detected resume skills:\n"
                f"{', '.join(result.resume_skills[:15])}\n\n"
                f"Suggested skill gaps:\n"
                f"{', '.join(result.gaps[:15])}"
            )

        else:
            # casual chat, call prompt_model function with the user message
            response_text = prompt_model(
                model="phi3",
                prompt=request.message
            )

        return JSONResponse({
            "response": response_text
        })

    except Exception as e:

        return JSONResponse(
            {
                "error": str(e)
            },
            status_code=500
        )