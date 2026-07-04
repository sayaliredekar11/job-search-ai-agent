# 💼 Job Search AI Agent

An AI-powered Job Search Assistant built with Python and Streamlit.

## Features

- Search jobs from live job APIs
- Filter by employment type
- Filter by company
- AI-powered job analysis using Gemini
- Direct Apply button
- Expandable job descriptions
- Responsive Streamlit UI

## Tech Stack

- Python
- Streamlit
- Gemini API
- RapidAPI (JSearch)
- Requests
- dotenv

## Installation

```bash
git clone https://github.com/Itssonia7/job-search-ai-agent.git

cd job-search-ai-agent

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
```

## Environment Variables

Create a `.env`

```
GEMINI_API_KEY=YOUR_KEY
JOB_API_KEY=YOUR_RAPIDAPI_KEY
```



## Future Improvements

- Resume upload
- ATS Resume Match
- Job recommendations
- Salary prediction
- Email alerts
- Saved jobs