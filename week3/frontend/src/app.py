from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
from pypdf import PdfReader

import requests
import os

load_dotenv()   # Load environment variables from .env file

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

BACKEND_URL = os.getenv("BACKEND_URL")  # Reads backend URL safely.
    
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={}
    )


@app.post("/chat")
async def chat(
    message: str = Form(...),
    pdf: UploadFile | None = File(default=None)
):

    pdf_text = ""

    try:

        # Extract PDF text if uploaded
        if pdf:

            reader = PdfReader(pdf.file)    # Create a PdfReader object to read the uploaded PDF file

            for page in reader.pages:
                text = page.extract_text()  # Extract text from each page of the PDF

                if text:
                    pdf_text += text + "\n"

        payload = {
            "message": message,
            "resume_text": pdf_text
        }

        response = requests.post(
            BACKEND_URL,
            json=payload,
            timeout=120
        )   # send JSON

        return JSONResponse(response.json())

    except Exception as e:

        return JSONResponse(
            {
                "error": str(e)
            },
            status_code=500
        )