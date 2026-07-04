import streamlit as st
from src.jobs import search_jobs
from src.ui import display_job_card

st.set_page_config(
    page_title="Job Search AI Agent",
    page_icon="💼",
    layout="wide"
)

if "jobs" not in st.session_state:
    st.session_state.jobs = []

st.title("💼 Job Search AI Agent")
st.write("Find jobs instantly using AI-powered search.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    job_title = st.text_input("Job Title")

with col2:
    location = st.text_input("Location")

st.subheader("Filters")

col1, col2 = st.columns(2)

with col1:
    employment_filter = st.selectbox(
        "Employment Type",
        [
            "All",
            "FULLTIME",
            "PARTTIME",
            "CONTRACTOR",
            "INTERN"
        ]
    )

with col2:
    keyword_filter = st.text_input("Company Name (Optional)")

if st.button("🔍 Search Jobs", use_container_width=True):

    query = job_title

    if location:
        query += f" jobs in {location}"

    with st.spinner("Searching..."):
        st.session_state.jobs = search_jobs(query)

filtered = []

for job in st.session_state.jobs:

    if employment_filter != "All":
        if employment_filter not in job.get("job_employment_types", []):
            continue

    if keyword_filter:
        if keyword_filter.lower() not in job.get("employer_name", "").lower():
            continue

    filtered.append(job)

st.success(f"Showing {len(filtered)} jobs")

for job in filtered:
    display_job_card(job)