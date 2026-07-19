import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-3.5-flash")

SYSTEM_INSTRUCTION = """You are a friendly, knowledgeable career coach embedded inside a job search app.
You help the user with resume advice, interview prep, career planning, and questions about
the jobs they've searched for. Keep answers concise and practical. If the user has a resume
or job search results attached below, use them to personalize your answers. If they ask about
something unrelated to careers/jobs/resumes, gently steer the conversation back."""


def build_context(resume_text=None, jobs=None):
    context = ""
    if resume_text:
        context += f"\n\n### User's Resume\n{resume_text}\n"
    if jobs:
        job_lines = [f"- {j.get('job_title')} at {j.get('employer_name')} ({j.get('job_city')})" for j in jobs[:10]]
        context += "\n\n### User's Current Job Search Results\n" + "\n".join(job_lines)
    return context


def get_chat_response(user_message, chat_history, resume_text=None, jobs=None):
    """Sends the conversation to Gemini and returns the assistant's reply.

    chat_history is a list of {"role": "user"/"model", "content": str} dicts,
    oldest first, not including the new user_message.
    """
    context = build_context(resume_text, jobs)

    history_for_gemini = [
        {"role": "user", "parts": [SYSTEM_INSTRUCTION + context]},
        {"role": "model", "parts": ["Understood, I'm ready to help with careers, resumes, and job search questions."]},
    ]
    for msg in chat_history:
        history_for_gemini.append({"role": msg["role"], "parts": [msg["content"]]})

    chat = model.start_chat(history=history_for_gemini)
    response = chat.send_message(user_message)
    return response.text