import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_job(job):

    prompt = f"""
You are an expert career coach.

Analyze this job.

Job Title:
{job.get("job_title")}

Company:
{job.get("employer_name")}

Location:
{job.get("job_city")}

Description:
{job.get("job_description")}

Give the response in markdown.

Include:

## Job Summary

## Required Skills

## Who Should Apply

## Interview Preparation Tips

## Resume Improvement Tips

Keep the response concise.
"""

    response = model.generate_content(prompt)

    return response.text