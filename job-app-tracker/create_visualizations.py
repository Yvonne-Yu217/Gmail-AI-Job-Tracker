#!/usr/bin/env python3
# create_visualizations.py - Generate beautiful HTML visualizations for job application data

import json
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from collections import Counter
from datetime import datetime, timedelta

def load_data():
    """Load job application data"""
    if not os.path.exists("data/job_applications.json"):
        print("Data file not found: data/job_applications.json")
        return []
    
    with open("data/job_applications.json", "r") as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} job application records")
    return data


def create_status_pie_chart(data):
    """Create a pie chart for application status distribution"""
    status_counts = Counter(item.get('status', 'Unknown') for item in data)
    
    # Define colors for each status
    status_colors = {
        'Applied': '#4ECDC4',
        'Assessment': '#45B7D1', 
        'Interview': '#96CEB4',
        'Offer': '#FFEAA7',
        'Declined': '#FF6B6B'
    }
    
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = [status_colors.get(label, '#DDA0DD') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        textinfo='label+percent+value',
        textfont_size=12,
        marker=dict(colors=colors)
    )])
    
    fig.update_layout(
        title=dict(text='Job Application Status Distribution', x=0.5, font=dict(size=20)),
        font=dict(size=14),
        showlegend=True,
        width=800,
        height=600
    )
    
    os.makedirs("visualizations", exist_ok=True)
    fig.write_html("visualizations/status_distribution.html")
    print("Created: visualizations/status_distribution.html")

def create_timeline_chart(data):
    """Create a timeline chart showing applications over time"""
    dated_data = [item for item in data if item.get('Date')]
    if not dated_data:
        print("No date information available for timeline chart")
        return
    
    df_data = []
    for item in dated_data:
        try:
            date = datetime.strptime(item['Date'], '%Y-%m-%d')
            df_data.append({
                'Date': date,
                'Status': item.get('status', 'Unknown'),
                'Company': item.get('Company', 'Unknown')
            })
        except ValueError:
            continue
    
    if not df_data:
        print("No valid date format found for timeline chart")
        return
    
    df = pd.DataFrame(df_data)
    timeline_data = df.groupby(['Date', 'Status']).size().reset_index(name='count')
    
    fig = px.line(timeline_data, x='Date', y='count', color='Status',
                  title='Job Applications Timeline',
                  labels={'count': 'Number of Applications'})
    
    fig.update_layout(
        title=dict(x=0.5, font=dict(size=20)),
        font=dict(size=14),
        width=1000,
        height=600,
        xaxis_title='Date',
        yaxis_title='Number of Applications'
    )
    
    fig.write_html("visualizations/applications_timeline.html")
    print("Created: visualizations/applications_timeline.html")

def create_company_bar_chart(data):
    """Create a horizontal bar chart for top companies"""
    company_counts = Counter(item.get('Company', 'Unknown') for item in data if item.get('Company') and item.get('Company') != 'Unknown')
    
    if not company_counts:
        print("No company information available for bar chart")
        return
    
    top_companies = company_counts.most_common(10)
    companies, counts = zip(*top_companies)
    
    fig = go.Figure(data=[go.Bar(
        x=list(counts),
        y=list(companies),
        orientation='h',
        marker=dict(color=list(counts), colorscale='viridis')
    )])
    
    fig.update_layout(
        title=dict(text='Top 10 Companies by Application Count', x=0.5, font=dict(size=20)),
        font=dict(size=14),
        width=1000,
        height=600,
        xaxis_title='Number of Applications',
        yaxis_title='Companies'
    )
    
    fig.write_html("visualizations/top_companies.html")
    print("Created: visualizations/top_companies.html")

def create_keyword_analysis(data):
    """Create a bar chart for job title keywords"""
    job_titles = [item.get('Job Title', '') for item in data if item.get('Job Title') and item.get('Job Title') not in ['Not specified', 'Not provided', '[Not provided]']]
    
    if not job_titles:
        print("No job title information available for keyword analysis")
        return
    
    keywords = []
    keyword_mapping = {
        'data': 'Data',
        'scientist': 'Scientist',
        'science': 'Science',
        'analyst': 'Analyst',
        'analytics': 'Analytics',
        'intern': 'Intern',
        'engineer': 'Engineer',
        'machine learning': 'ML',
        'ml': 'ML',
        'software': 'Software',
        'research': 'Research',
        'business': 'Business',
        'product': 'Product',
        'technical': 'Technical'
    }
    
    for title in job_titles:
        title_lower = title.lower()
        for key, value in keyword_mapping.items():
            if key in title_lower:
                keywords.append(value)
    
    if not keywords:
        print("No keywords found in job titles")
        return
    
    keyword_counts = Counter(keywords)
    top_keywords = keyword_counts.most_common(10)
    words, counts = zip(*top_keywords)
    
    fig = go.Figure(data=[go.Bar(
        x=list(words),
        y=list(counts),
        marker=dict(color=list(counts), colorscale='viridis')
    )])
    
    fig.update_layout(
        title=dict(text='Job Title Keywords Analysis', x=0.5, font=dict(size=20)),
        font=dict(size=14),
        width=1000,
        height=600,
        xaxis_title='Keywords',
        yaxis_title='Frequency'
    )
    
    fig.write_html("visualizations/keyword_analysis.html")
    print("Created: visualizations/keyword_analysis.html")

def create_success_rate_chart(data):
    """Create a chart showing success rates"""
    status_counts = Counter(item.get('status', 'Unknown') for item in data)
    total = len(data)
    
    if total == 0:
        return
    
    success_categories = {
        'Positive': ['Offer', 'Interviewed', 'Assessment'],
        'Pending': ['Applied'],
        'Negative': ['Declined']
    }
    
    category_counts = {}
    for category, statuses in success_categories.items():
        count = sum(status_counts.get(status, 0) for status in statuses)
        category_counts[category] = count
    
    categories = list(category_counts.keys())
    counts = list(category_counts.values())
    percentages = [count/total*100 for count in counts]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=percentages,
        text=[f'{p:.1f}%<br>({c})' for p, c in zip(percentages, counts)],
        textposition='auto',
        marker=dict(color=['#2ECC71', '#F39C12', '#E74C3C'])
    )])
    
    fig.update_layout(
        title=dict(text='Application Success Rate Analysis', x=0.5, font=dict(size=20)),
        font=dict(size=14),
        width=800,
        height=600,
        yaxis_title='Percentage'
    )
    
    fig.write_html("visualizations/success_rate.html")
    print("Created: visualizations/success_rate.html")

def create_summary_dashboard(data):
    """Create a summary dashboard with key metrics"""
    status_counts = Counter(item.get('status', 'Unknown') for item in data)
    company_counts = Counter(item.get('Company', 'Unknown') for item in data if item.get('Company') and item.get('Company') != 'Unknown')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Status Distribution', 'Top 5 Companies', 'Keywords', 'Key Metrics'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "table"}]]
    )
    
    # Status pie chart
    fig.add_trace(go.Pie(
        labels=list(status_counts.keys()),
        values=list(status_counts.values()),
        hole=0.3,
        textinfo='label+percent'
    ), row=1, col=1)
    
    # Top companies
    if company_counts:
        top_5_companies = company_counts.most_common(5)
        companies, counts = zip(*top_5_companies)
        fig.add_trace(go.Bar(
            x=list(companies),
            y=list(counts),
            name='Companies'
        ), row=1, col=2)
    
    # Keywords
    job_titles = [item.get('Job Title', '') for item in data if item.get('Job Title')]
    keywords = []
    for title in job_titles:
        title_lower = title.lower()
        if 'data' in title_lower: keywords.append('Data')
        if 'intern' in title_lower: keywords.append('Intern')
        if 'science' in title_lower: keywords.append('Science')
        if 'analyst' in title_lower: keywords.append('Analytics')
        if 'engineer' in title_lower: keywords.append('Engineer')
    
    if keywords:
        keyword_counts = Counter(keywords)
        top_keywords = keyword_counts.most_common(5)
        words, counts = zip(*top_keywords)
        fig.add_trace(go.Bar(
            x=list(words),
            y=list(counts),
            name='Keywords'
        ), row=2, col=1)
    
    # Key metrics table
    total_apps = len(data)
    metrics_data = [
        ['Total Applications', total_apps],
        ['Applied', status_counts.get('Applied', 0)],
        ['Assessment', status_counts.get('Assessment', 0)],
        ['Interviewed', status_counts.get('Interviewed', 0)],
        ['Offers', status_counts.get('Offer', 0)],
        ['Declined', status_counts.get('Declined', 0)],
        ['Success Rate', f"{((status_counts.get('Offer', 0) + status_counts.get('Interviewed', 0) + status_counts.get('Assessment', 0)) / total_apps * 100):.1f}%"]
    ]
    
    fig.add_trace(go.Table(
        header=dict(values=['Metric', 'Value']),
        cells=dict(values=[[row[0] for row in metrics_data], [row[1] for row in metrics_data]])
    ), row=2, col=2)
    
    fig.update_layout(
        title=dict(text='Job Application Dashboard', x=0.5, font=dict(size=24)),
        font=dict(size=12),
        width=1400,
        height=1000,
        showlegend=False
    )
    
    fig.write_html("visualizations/dashboard.html")
    print("Created: visualizations/dashboard.html")

def main():
    """Main function to generate job application visualizations"""
    print("Generating Job Application Status Distribution")
    print("=" * 50)
    
    data = load_data()
    if not data:
        return
    
    os.makedirs("visualizations", exist_ok=True)
    
    # Create status distribution pie chart
    create_status_pie_chart(data)
    
    print("\nVisualization created successfully!")
    print("Files saved in: visualizations/")
    print("   - status_distribution.html")

if __name__ == "__main__":
    main()
