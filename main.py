from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import query
from openai import OpenAI
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class recipeRequest(BaseModel):
   text: str

@app.get("/")
async def home():
    return JSONResponse(content={"message": "Working Fine"})

@app.post("/generate")
async def get_ingredients(data: recipeRequest):
    query_text = data.text  

    # Try to fetch from DB
    results = query("SELECT * FROM query WHERE text = %s", (query_text,))
    logger.info(f"Query result: {results}")

    if results:
        steps_from_db = results[0][2].split("\n")  # ans column
        return JSONResponse(content={"message": "Data from DB", "query": steps_from_db})

    try:
        gemini_key = "AIzaSyAdfD6yDtOF6vbmoxVvtHcuG4SVPTMx_fg"
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "You are an expert natural language to SQL query generator."},
                {"role": "user", "content": f"Give me SQL queries using this text: {query_text}"}
            ]
        )

        result_text = response.choices[0].message.content
        steps = result_text.split("\n")

        if not steps:
            return {"message": "No data found for this input"}

        steps_text = "\n".join(steps)

        # Save new result to DB
        query("INSERT INTO query (text, ans) VALUES (%s, %s)", (query_text, steps_text))

        return {"message": "Data fetched from Gemini API", "query": steps}

    except Exception as e:
        logger.error(str(e))
        return {"message": "Error fetching data", "error": str(e)}
