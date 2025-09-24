# scripts/process_emails.py
import os
from dotenv import load_dotenv
import openai

load_dotenv(dotenv_path='config/.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")

openai.api_key = OPENAI_API_KEY

# Optional: allow custom OpenAI-compatible endpoint and model via env
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
if OPENAI_BASE_URL:
    openai.api_base = OPENAI_BASE_URL
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Heuristic blacklist to reject non-application content early
BLACKLIST_KEYWORDS = [
    "job alert", "jobs for you", "recommended jobs", "recommend jobs", "new jobs",
    "newsletter", "digest", "weekly update", "career tips", "invitation to apply",
    "hot jobs", "top jobs", "trending jobs", "hiring now",
    "subscribe", "unsubscribe", "marketing",
    # common noisy senders/brands in content
    "lensa", "ziprecruiter", "indeed", "jobcase", "linkedin", "glassdoor"
]

ALLOWED_STATUSES = {"applied", "assessment", "interviewed", "offer", "declined"}

def _looks_like_non_application(text: str) -> bool:
    t = (text or "").lower()
    return any(kw in t for kw in BLACKLIST_KEYWORDS)

def is_job_application(snippet):
    """Quick check if email is job application-related using snippet."""
    # Fast heuristic rejection
    if _looks_like_non_application(snippet):
        return False
    
    # Enhanced local pattern matching for common rejection phrases
    snippet_lower = snippet.lower()
    rejection_indicators = [
        "decided to move forward with other candidates",
        "move forward with other candidates", 
        "not selected", "not moving forward", "regret to inform",
        "application against the selection criteria",
        "thank you for taking the time to apply",
        "encourage you to apply to future opportunities"
    ]
    
    # If we detect clear rejection language, it's definitely a job application
    if any(phrase in snippet_lower for phrase in rejection_indicators):
        return True
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a filter for job application emails. Return exactly 'Yes' if the text indicates "
                    "real job application progress (application submitted/received, interview, assessment, coding challenge, "
                    "online test, offer, or rejection). Also return 'Yes' for assessment invitations, technical tests, "
                    "or any follow-up communications from companies you've applied to. "
                    "IMPORTANT: Rejection emails from companies are job applications too - return 'Yes' for them. "
                    "Return 'No' only for job alerts, recommended jobs, newsletters, invitations to apply, or marketing content."
                )
            },
            {"role": "user", "content": snippet}
        ]
    )
    return response.choices[0].message.content.strip().lower() == 'yes'

def classify_email(email_content):
    """Extract details from full email content."""
    # Reject obvious non-application emails
    if _looks_like_non_application(email_content):
        return "Not Job Application"
    
    system_prompt = (
        "You are an expert at analyzing job application emails. "
        "If the email is not clearly about a real application process (submission received, interview, assessment, offer, rejection), "
        "return exactly: 'Not Job Application'. Do NOT treat job alerts, recommended jobs, newsletters, or invitations to apply as job application emails. "
        "If it is related, extract fields strictly in this format (Status must be one of Applied, Assessment, Interviewed, Offer, Declined):\n"
        "Company: [company name]\n"
        "Job Title: [complete job title with all details, including department, level, program, year, etc.]\n"
        "Location: [location]\n"
        "Status: [Applied|Assessment|Interviewed|Offer|Declined]\n"
        "IMPORTANT: \n"
        "- For rejection emails, always use Status: Declined\n"
        "- Extract the FULL job title including all parenthetical information, department details, program years, degree requirements, etc.\n"
        "- Example: 'Data Scientist Intern (TikTok-Business Risk Integrated Control-Risk Measurement) - 2026 Summer (BS/MS)' not just 'Data Scientist Intern'\n"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": email_content}
        ],
        max_tokens=150,
        temperature=0
    )
    
    try:
        classification = response.choices[0].message.content.strip()
        if not classification.startswith("Company:"):
            return "Not Job Application"
        
        # Post validation
        lines = {k.strip().lower(): v.strip() for k, v in (line.split(":", 1) for line in classification.splitlines() if ":" in line)}
        status_val = (lines.get("status", "").strip() or "").lower()
        
        if status_val not in ALLOWED_STATUSES:
            return "Not Job Application"
        if _looks_like_non_application(email_content):
            return "Not Job Application"
        return classification
    except (IndexError, AttributeError, KeyError) as e:
        print(f"Error processing OpenAI response: {e}")
        return "Not Job Application"
