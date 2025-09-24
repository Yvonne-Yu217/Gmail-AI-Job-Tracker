#!/usr/bin/env python3
# generate_stats.py - Generate job application statistics report

import json
import os
from collections import Counter
from datetime import datetime

def load_data():
    """Load job application data"""
    if not os.path.exists("data/job_applications.json"):
        print("Data file not found: data/job_applications.json")
        return []
    
    with open("data/job_applications.json", "r") as f:
        return json.load(f)

def generate_stats(data):
    """Generate statistics report based on hiring process flow"""
    if not data:
        print("No data available for analysis")
        return
    
    print("=" * 60)
    print("Job Application Statistics Report")
    print("=" * 60)
    
    # Basic statistics
    total_applications = len(data)
    print(f"\nTotal Applications: {total_applications}")
    
    # Status distribution with hiring process flow
    status_counts = Counter(item.get('status', 'Unknown') for item in data)
    
    # Define status order and descriptions
    status_info = {
        'Applied': 'Initial applications submitted',
        'Assessment': 'Coding tests/take-home assignments',
        'Interview': 'Phone/video/onsite interviews',
        'Offer': 'Job offers received',
        'Declined': 'Rejected at any stage'
    }
    
    print(f"\nHiring Process Flow Analysis:")
    print("-" * 40)
    
    # Show status distribution in process order
    for status in ['Applied', 'Assessment', 'Interview', 'Offer', 'Declined']:
        count = status_counts.get(status, 0)
        if count > 0:
            percentage = (count / total_applications) * 100
            description = status_info.get(status, '')
            print(f"  {status}: {count} ({percentage:.1f}%) - {description}")
    
    # Calculate conversion rates
    print(f"\nConversion Rates:")
    print("-" * 40)
    
    applied_count = status_counts.get('Applied', 0)
    assessment_count = status_counts.get('Assessment', 0)
    interview_count = status_counts.get('Interview', 0)
    offer_count = status_counts.get('Offer', 0)
    declined_count = status_counts.get('Declined', 0)
    
    # Calculate progression rates
    total_progressed = assessment_count + interview_count + offer_count
    if total_applications > 0:
        progression_rate = (total_progressed / total_applications) * 100
        print(f"  Application → Next Stage: {total_progressed}/{total_applications} ({progression_rate:.1f}%)")
    
    if assessment_count > 0:
        assessment_to_interview = min(assessment_count, interview_count)
        assessment_success = (assessment_to_interview / assessment_count) * 100
        print(f"  Assessment → Interview: {assessment_to_interview}/{assessment_count} ({assessment_success:.1f}%)")
    
    if interview_count > 0:
        interview_success = (offer_count / interview_count) * 100
        print(f"  Interview → Offer: {offer_count}/{interview_count} ({interview_success:.1f}%)")
    
    if total_applications > 0:
        overall_success = (offer_count / total_applications) * 100
        print(f"  Overall Success Rate: {offer_count}/{total_applications} ({overall_success:.1f}%)")
    
    # Company statistics (Top 5 only)
    company_counts = Counter(item.get('Company', 'Unknown') for item in data)
    print(f"\nTop 5 Companies Applied:")
    print("-" * 40)
    for company, count in company_counts.most_common(5):
        if company and company != 'Unknown':
            print(f"  {company}: {count}")
    
    # Date range
    dates = [item.get('Date', '') for item in data if item.get('Date')]
    if dates:
        print(f"\nApplication Date Range:")
        print(f"  Earliest: {min(dates)}")
        print(f"  Latest: {max(dates)}")
    
    # Job title keywords
    job_titles = [item.get('Job Title', '') for item in data if item.get('Job Title') and item.get('Job Title') not in ['Not specified', 'Not provided', '[Not provided]']]
    if job_titles:
        # Extract keywords
        keywords = []
        for title in job_titles:
            title_lower = title.lower()
            if 'data' in title_lower:
                keywords.append('Data')
            if 'scientist' in title_lower or 'science' in title_lower:
                keywords.append('Science')
            if 'analyst' in title_lower or 'analytics' in title_lower:
                keywords.append('Analytics')
            if 'intern' in title_lower:
                keywords.append('Intern')
            if 'engineer' in title_lower:
                keywords.append('Engineer')
            if 'machine learning' in title_lower or 'ml' in title_lower:
                keywords.append('ML')
        
        if keywords:
            keyword_counts = Counter(keywords)
            print(f"\nJob Title Keywords:")
            for keyword, count in keyword_counts.most_common():
                print(f"  {keyword}: {count}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    data = load_data()
    generate_stats(data)
