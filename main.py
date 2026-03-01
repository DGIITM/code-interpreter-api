import os
import re
from typing import List
from io import StringIO
import sys
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Tool Function: Execute Code
# -----------------------------
def execute_python_code(code: str) -> dict:
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except Exception:
        output = traceback.format_exc()
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout


# -----------------------------
# Extract Error Line Numbers
# -----------------------------
def extract_error_lines(traceback_text: str) -> List[int]:
    """
    Extract line numbers from Python traceback.
    """
    line_numbers = re.findall(r'line (\d+)', traceback_text)
    return list(sorted(set(int(num) for num in line_numbers)))


# -----------------------------
# Request / Response Models
# -----------------------------
class CodeRequest(BaseModel):
    code: str


class CodeResponse(BaseModel):
    error: List[int]
    result: str


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "API running"}


# -----------------------------
# Code Interpreter Endpoint
# -----------------------------
@app.post("/code-interpreter", response_model=CodeResponse)
async def code_interpreter(request: CodeRequest):

    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    execution = execute_python_code(request.code)

    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    else:
        error_lines = extract_error_lines(execution["output"])

        return {
            "error": error_lines,
            "result": execution["output"]
        }