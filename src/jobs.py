import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")


def search_jobs(query):
    url = "https://jsearch-mega.p.rapidapi.com/search"

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "country": "india"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()["data"]

    print(response.status_code)
    print(response.text)
    return []