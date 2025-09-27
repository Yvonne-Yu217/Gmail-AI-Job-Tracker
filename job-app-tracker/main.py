# main.py
import json
import os
import signal
import sys
import time
import argparse
from datetime import datetime, timedelta
from tqdm import tqdm
from scripts.gmail_fetch import fetch_emails, get_email_snippet, get_email_content
from scripts.process_emails import is_job_application, classify_email

# Global variables
results = []
interrupted = False
processed_email_ids = set()  

def normalize_status(raw_status):
    """
    Normalize job application status based on the hiring process flow:
    Applied -> Assessment/Interview -> Offer/Declined
    
    Status hierarchy (later stages override earlier ones):
    1. Applied (initial application)
    2. Assessment (coding test, take-home, etc.)
    3. Interview (phone, video, onsite)
    4. Offer (job offer received)
    5. Declined (rejected at any stage)
    """
    raw = raw_status.lower().strip()
    
    # Declined - highest priority (can happen at any stage)
    declined_phrases = [
        "declined", "rejected", "not selected", "not moving forward", "not proceed",
        "selected other candidates", "selected individuals", "chosen other applicants",
        "decided to move forward with other candidates", "pursuing other candidates",
        "more closely meet our requirements", "regret to inform",
        "unable to offer", "cannot offer", "will not be moving forward",
        "have filled the position", "position has been filled", "no longer considering",
        "decided not to move forward", "will not be proceeding", "not the right fit"
    ]
    if any(phrase in raw for phrase in declined_phrases):
        return "Declined"
    
    # Offer - second highest priority
    elif any(word in raw for word in ["offer", "accepted", "congratulations"]):
        return "Offer"
    
    # Interview - third priority
    elif any(word in raw for word in ["interview", "phone screen", "video call", "onsite", "final round"]):
        return "Interviewed"
    
    # Assessment - fourth priority
    elif any(word in raw for word in [
        "assessment", "online assessment", "oa", "coding challenge", "code challenge",
        "take-home", "take home", "test", "hackerank", "hackerrank", "codility", "karat",
        "work sample", "case study", "exercise", "assignment", "online test", "coding test",
        "take home assignment", "code exercise", "skills assessment", "technical screening",
        "online challenge", "technical assessment", "technical test", "screening test"
    ]):
        return "Assessment"
    
    # Applied - lowest priority (default)
    elif any(word in raw for word in ["applied", "submitted", "received", "application"]):
        return "Applied"
    
    else:
        return "Applied"

def parse_classification_details(classification):
    details = {
        "Company": "",
        "Job Title": "",
        "Location": "",
        "status": "",
        "Date": ""
    }
    for line in classification.splitlines():
        line = line.strip()
        if line.lower().startswith("company:"):
            details["Company"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("job title:"):
            details["Job Title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("location:"):
            details["Location"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("status:"):
            raw_status = line.split(":", 1)[1].strip()
            details["status"] = normalize_status(raw_status)
    return details

def save_results(filename="data/job_applications.json"):
    os.makedirs("data", exist_ok=True)
    # Create a copy of results without email_id
    results_to_save = [{k: v for k, v in r.items() if k != "email_id"} for r in results]
    with open(filename, "w") as f:
        json.dump(results_to_save, f, indent=4)
    print(f"Saved {len(results_to_save)} records to {filename}")

def load_existing_results(filename="data/job_applications.json"):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error reading {filename}: {e}")
            return []
    return []

def save_processed_ids(ids, filename="data/processed_ids.json"):
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(list(ids), f)
    print(f"Saved {len(ids)} processed IDs")

def load_processed_ids(filename="data/processed_ids.json"):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                content = f.read().strip()
                if not content:
                    return set()
                return set(json.loads(content))
        except json.JSONDecodeError as e:
            print(f"Error reading {filename}: {e}")
            return set()
    return set()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Extract job application data from Gmail")
    parser.add_argument("--since", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, help="Number of days back from today")
    parser.add_argument("--limit", type=int, help="Maximum number of emails to process")
    return parser.parse_args()

def signal_handler(sig, frame):
    global interrupted
    interrupted = True
    print("\nInterrupt received, saving progress...")
    save_results()
    save_processed_ids(processed_email_ids)
    sys.exit(0)

def process_all_emails(limit=None, since_hours=None, since_date=None, until_date=None):
    global results, interrupted, processed_email_ids
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load existing state
    results = load_existing_results()
    processed_email_ids = load_processed_ids()
    print(f"Loaded {len(results)} existing records, {len(processed_email_ids)} processed IDs")
    
    # Convert date parameters to since_hours if needed
    if since_date or until_date:
        if since_date:
            since_dt = datetime.strptime(since_date, '%Y-%m-%d')
            since_hours = int((datetime.now() - since_dt).total_seconds() / 3600)
            print(f"Searching emails since: {since_date} ({since_hours} hours ago)")
        if until_date:
            until_dt = datetime.strptime(until_date, '%Y-%m-%d')
            until_hours = int((datetime.now() - until_dt).total_seconds() / 3600)
            print(f"Searching emails until: {until_date} ({until_hours} hours ago)")
            # Note: Gmail API doesn't directly support "until" date, 
            # so we'll filter after fetching
    
    messages = fetch_emails(since_hours=since_hours)
    
    # Filter by until_date if specified
    if until_date:
        until_dt = datetime.strptime(until_date, '%Y-%m-%d')
        filtered_messages = []
        for msg in messages:
            # Get email date and compare
            email_data = get_email_snippet(msg['id'])  # This is lightweight
            # Note: We'll need to implement date filtering in gmail_fetch.py
            # For now, we'll process all and filter during processing
        messages = filtered_messages if 'filtered_messages' in locals() else messages
    
    print(f"Processing {len(messages)} emails...")
    
    processed = 0
    # Create progress bar
    with tqdm(total=len(messages), desc="Processing emails", unit="email") as pbar:
        for msg in messages:
            if interrupted:
                break
            
            msg_id = msg['id']
            if msg_id in processed_email_ids:
                pbar.update(1)
                continue
            
            if limit is not None and processed >= limit:
                print("Reached processing limit. Stopping.")
                break
            
            snippet = get_email_snippet(msg_id)
            # Add much longer delay to reduce API call frequency
            time.sleep(3.0)  # 3 second delay between Gmail API calls
            
            if not is_job_application(snippet):
                processed_email_ids.add(msg_id)
                time.sleep(1.0)  # Delay even for rejected emails
                pbar.update(1)
                continue
            
            email_data = get_email_content(msg_id)
            content = email_data["content"]
            email_date = email_data["date"]
            
            # Add much longer delay before OpenAI API call
            time.sleep(3.0)  # 3 second delay before OpenAI call to avoid overload
            
            classification = classify_email(content)
            processed_email_ids.add(msg_id)
            
            # Add longer delay after processing each email
            time.sleep(2.0)  # 2 second delay after processing
            
            if "not job application" in classification.lower():
                pbar.update(1)
                continue
            
            details = parse_classification_details(classification)
            details["Date"] = email_date
            details["email_id"] = msg_id  # Keep internally
            
            if details["Company"] or details["Job Title"] or details["Location"] or details["status"]:
                tqdm.write("Extracted Details:")
                tqdm.write(f"Email ID: {details['email_id']}")
                tqdm.write(f"Company: {details['Company']}")
                tqdm.write(f"Job Title: {details['Job Title']}")
                tqdm.write(f"Location: {details['Location']}")
                tqdm.write(f"Status: {details['status']}")
                tqdm.write(f"Date: {details['Date']}")
                tqdm.write("-" * 40)
                results.append(details)
                processed += 1
                
                if processed % 10 == 0:
                    save_results()
                    save_processed_ids(processed_email_ids)
            
            # Update progress bar
            pbar.update(1)
    
    if not interrupted:
        save_results()
        save_processed_ids(processed_email_ids)
    
    return results

if __name__ == '__main__':
    try:
        args = parse_args()
        
        # Handle different date options
        since_hours = None
        since_date = args.since
        until_date = args.until
        
        if args.days:
            since_hours = args.days * 24
            print(f"Processing emails from the last {args.days} days")
        elif args.since:
            print(f"Processing emails since: {args.since}")
        elif args.until:
            print(f"Processing emails until: {args.until}")
        else:
            print("Processing all emails")
        
        if args.limit:
            print(f"Limiting to {args.limit} emails")
        
        # Process emails with specified parameters
        process_all_emails(
            limit=args.limit, 
            since_hours=since_hours,
            since_date=since_date,
            until_date=until_date
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        save_results()
        save_processed_ids(processed_email_ids)