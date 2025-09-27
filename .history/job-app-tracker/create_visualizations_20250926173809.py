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

def create_advanced_funnel_chart(data):
    """Create a conversion funnel showing the job application process"""
    status_counts = Counter(item.get('status', 'Unknown') for item in data)
    
    # Define the funnel stages in order
    funnel_stages = [
        ('Applied', status_counts.get('Applied', 0)),
        ('Assessment', status_counts.get('Assessment', 0)),
        ('Interviewed', status_counts.get('Interviewed', 0)),
        ('Offer', status_counts.get('Offer', 0))
    ]
    
    # Calculate cumulative values for funnel
    total_applied = sum(status_counts.values())
    declined = status_counts.get('Declined', 0)
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=[stage[0] for stage in funnel_stages],
        x=[stage[1] for stage in funnel_stages],
        textinfo="value+percent initial",
        textfont=dict(size=14),
        marker=dict(color=["#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"])
    ))
    
    fig.update_layout(
        title=dict(text='Job Application Conversion Funnel', x=0.5, font=dict(size=20)),
        font=dict(size=14),
        width=800,
        height=600,
        annotations=[
            dict(text=f"Total Declined: {declined}", 
                 x=0.5, y=-0.1, xref="paper", yref="paper",
                 showarrow=False, font=dict(size=12, color="red"))
        ]
    )
    
    fig.write_html("visualizations/conversion_funnel.html")
    print("Created: visualizations/conversion_funnel.html")

def create_heatmap_calendar(data):
    """Create a calendar heatmap showing application activity"""
    dated_data = [item for item in data if item.get('Date')]
    if not dated_data:
        print("No date information available for calendar heatmap")
        return
    
    # Process dates
    date_counts = {}
    for item in dated_data:
        try:
            date = datetime.strptime(item['Date'], '%Y-%m-%d').date()
            date_counts[date] = date_counts.get(date, 0) + 1
        except ValueError:
            continue
    
    if not date_counts:
        return
    
    # Create date range
    min_date = min(date_counts.keys())
    max_date = max(date_counts.keys())
    
    # Generate all dates in range
    all_dates = []
    current = min_date
    while current <= max_date:
        all_dates.append(current)
        current += timedelta(days=1)
    
    # Prepare data for heatmap
    dates = [d.strftime('%Y-%m-%d') for d in all_dates]
    values = [date_counts.get(d, 0) for d in all_dates]
    weekdays = [d.strftime('%A') for d in all_dates]
    weeks = [(d - min_date).days // 7 for d in all_dates]
    
    fig = go.Figure(data=go.Scatter(
        x=weeks,
        y=weekdays,
        mode='markers',
        marker=dict(
            size=[max(v*10, 5) for v in values],
            color=values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Applications")
        ),
        text=[f"{d}<br>{v} applications" for d, v in zip(dates, values)],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Application Activity Calendar', x=0.5, font=dict(size=20)),
        xaxis_title='Week',
        yaxis_title='Day of Week',
        width=1200,
        height=400
    )
    
    fig.write_html("visualizations/activity_calendar.html")
    print("Created: visualizations/activity_calendar.html")

def create_sankey_diagram(data):
    """Create a Sankey diagram showing flow from companies to statuses"""
    # Get top companies and their statuses
    company_status_pairs = []
    for item in data:
        company = item.get('Company', 'Unknown')
        status = item.get('status', 'Unknown')
        if company != 'Unknown' and status != 'Unknown':
            company_status_pairs.append((company, status))
    
    if not company_status_pairs:
        print("No company-status data available for Sankey diagram")
        return
    
    # Get top 10 companies
    company_counts = Counter(pair[0] for pair in company_status_pairs)
    top_companies = [comp for comp, _ in company_counts.most_common(10)]
    
    # Filter data for top companies
    filtered_pairs = [(comp, status) for comp, status in company_status_pairs if comp in top_companies]
    
    # Create nodes and links
    statuses = list(set(pair[1] for pair in filtered_pairs))
    all_nodes = top_companies + statuses
    
    # Create mapping
    node_map = {node: i for i, node in enumerate(all_nodes)}
    
    # Create links
    link_counts = Counter(filtered_pairs)
    sources = [node_map[comp] for comp, status in link_counts.keys()]
    targets = [node_map[status] for comp, status in link_counts.keys()]
    values = list(link_counts.values())
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color="blue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values
        )
    )])
    
    fig.update_layout(
        title=dict(text="Company → Status Flow", x=0.5, font=dict(size=20)),
        font_size=12,
        width=1200,
        height=600
    )
    
    fig.write_html("visualizations/company_status_flow.html")
    print("Created: visualizations/company_status_flow.html")

def create_interactive_scatter(data):
    """Create an interactive scatter plot with company size vs success rate"""
    # Calculate metrics per company
    company_data = {}
    for item in data:
        company = item.get('Company', 'Unknown')
        status = item.get('status', 'Unknown')
        
        if company == 'Unknown':
            continue
            
        if company not in company_data:
            company_data[company] = {'total': 0, 'positive': 0, 'statuses': []}
        
        company_data[company]['total'] += 1
        company_data[company]['statuses'].append(status)
        
        if status in ['Offer', 'Interviewed', 'Assessment']:
            company_data[company]['positive'] += 1
    
    # Filter companies with at least 2 applications
    filtered_companies = {k: v for k, v in company_data.items() if v['total'] >= 2}
    
    if not filtered_companies:
        print("Not enough data for scatter plot")
        return
    
    companies = list(filtered_companies.keys())
    total_apps = [filtered_companies[c]['total'] for c in companies]
    success_rates = [filtered_companies[c]['positive'] / filtered_companies[c]['total'] * 100 for c in companies]
    
    fig = go.Figure(data=go.Scatter(
        x=total_apps,
        y=success_rates,
        mode='markers+text',
        text=companies,
        textposition='top center',
        marker=dict(
            size=[t*5 for t in total_apps],
            color=success_rates,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Success Rate %")
        ),
        hovertemplate='<b>%{text}</b><br>Applications: %{x}<br>Success Rate: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Company Performance: Applications vs Success Rate', x=0.5, font=dict(size=20)),
        xaxis_title='Total Applications',
        yaxis_title='Success Rate (%)',
        width=1000,
        height=600
    )
    
    fig.write_html("visualizations/company_performance.html")
    print("Created: visualizations/company_performance.html")

def create_all_in_one_dashboard(data):
    """Create a clean dashboard with essential visualizations"""
    # Create 2x2 dashboard with logical grouping
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Status Distribution', 'Key Metrics',
            'Applications Timeline', 'Activity Calendar'
        ),
        specs=[
            [{"type": "pie"}, {"type": "table"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ],
        vertical_spacing=0.18,
        horizontal_spacing=0.15,
        column_widths=[0.5, 0.5],
        row_heights=[0.45, 0.55]
    )
    
    status_counts = Counter(item.get('status', 'Unknown') for item in data)
    
    # 1. Status Distribution Pie Chart - Beautiful gradient colors
    status_colors = {
        'Applied': '#6C5CE7',      # Soft purple
        'Assessment': '#74B9FF',   # Sky blue
        'Interviewed': '#FDCB6E',  # Warm yellow
        'Offer': '#00B894',        # Success green
        'Declined': '#FD79A8'      # Soft pink
    }
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = [status_colors.get(label, '#95A5A6') for label in labels]
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(
            colors=colors,
            line=dict(color='#FFFFFF', width=4)
        ),
        textinfo='label+percent',
        textfont=dict(size=12, color='white', family='Arial Black'),
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        pull=[0.05 if label == 'Offer' else 0 for label in labels]  # Highlight offers
    ), row=1, col=1)
    
    # 2. Key Metrics Table - Enhanced styling (moved to top right)
    total_apps = len(data)
    positive_outcomes = status_counts.get('Offer', 0) + status_counts.get('Interviewed', 0) + status_counts.get('Assessment', 0)
    success_rate = (positive_outcomes / total_apps * 100) if total_apps > 0 else 0
    
    metrics_data = [
        ['Total Applications', total_apps],
        ['Applied', status_counts.get('Applied', 0)],
        ['Assessment', status_counts.get('Assessment', 0)],
        ['Interviewed', status_counts.get('Interviewed', 0)],
        ['Offers', status_counts.get('Offer', 0)],
        ['Declined', status_counts.get('Declined', 0)],
        ['Success Rate', f"{success_rate:.1f}%"]
    ]
    
    # Create alternating row colors with special styling for formula
    row_colors = ['#F8F9FA', '#E9ECEF'] * 4
    
    # Create alternating row colors for the table
    formula_colors = ['#F8F9FA', '#EDF2F7'] * (len(metrics_data) // 2 + 1)  # Alternating light colors
    
    fig.add_trace(go.Table(
        header=dict(
            values=['<b>Metric</b>', '<b>Value</b>'],
            fill_color='#6C5CE7',
            font=dict(color='white', size=18, family='Arial Black'),
            align='center',
            height=50
        ),
        cells=dict(
            values=[[row[0] for row in metrics_data], [row[1] for row in metrics_data]],
            fill_color=[formula_colors[:len(metrics_data)], formula_colors[:len(metrics_data)]],
            font=dict(
                color='#2C3E50',
                size=15,
                family='Arial Black'
            ),
            align=['center', 'center'],
            height=42  # Use a slightly larger height for all rows
        )
    ), row=1, col=2)
    
    # 3. Applications Timeline - Enhanced styling (moved to bottom left)
    dated_data = [item for item in data if item.get('Date')]
    if dated_data:
        dates = []
        for item in dated_data:
            try:
                dates.append(datetime.strptime(item['Date'], '%Y-%m-%d'))
            except:
                continue
        
        if dates:
            date_counts = Counter(d.strftime('%Y-%m-%d') for d in dates)
            sorted_dates = sorted(date_counts.keys())
            
            # Create gradient effect for the line
            fig.add_trace(go.Scatter(
                x=sorted_dates,
                y=[date_counts[d] for d in sorted_dates],
                mode='lines+markers',
                line=dict(
                    color='#6C5CE7',
                    width=5,
                    shape='spline'
                ),
                marker=dict(
                    size=12,
                    color='#FDCB6E',
                    line=dict(color='#FFFFFF', width=3),
                    symbol='circle'
                ),
                fill='tonexty',
                fillcolor='rgba(108, 92, 231, 0.15)',
                hovertemplate='<b>Date: %{x}</b><br>Applications: %{y}<extra></extra>',
                name='Applications'
            ), row=2, col=1)
    
    # 4. Activity Calendar - Beautiful gradient bars (moved to bottom right)
    if dated_data:
        date_counts = {}
        for item in dated_data:
            try:
                date = datetime.strptime(item['Date'], '%Y-%m-%d').date()
                weekday = date.strftime('%A')
                date_counts[weekday] = date_counts.get(weekday, 0) + 1
            except:
                continue
        
        if date_counts:
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            counts = [date_counts.get(day, 0) for day in weekdays]
            
            # Beautiful gradient colors inspired by sunset
            weekday_colors = [
                '#FF6B9D',  # Monday - Pink
                '#C44569',  # Tuesday - Deep pink
                '#F8B500',  # Wednesday - Orange
                '#FDCB6E',  # Thursday - Yellow
                '#6C5CE7',  # Friday - Purple
                '#74B9FF',  # Saturday - Blue
                '#A29BFE'   # Sunday - Light purple
            ]
            
            fig.add_trace(go.Bar(
                x=weekdays,
                y=counts,
                marker=dict(
                    color=weekday_colors,
                    line=dict(color='#FFFFFF', width=3),
                    opacity=0.9
                ),
                text=counts,
                textposition='auto',
                textfont=dict(size=13, color='white', family='Arial Black'),
                hovertemplate='<b>%{x}</b><br>Applications: %{y}<extra></extra>',
                name='Daily Activity'
            ), row=2, col=2)
    
    # No formula annotation - keeping the dashboard clean and simple
    
    # Update layout with beautiful modern styling
    fig.update_layout(
        title=dict(
            text='<b>Job Application Analytics Dashboard</b>',
            x=0.5,
            font=dict(size=36, color='#2C3E50', family='Arial Black')
        ),
        font=dict(size=13, family='Arial, sans-serif'),
        width=1500,
        height=1100,
        showlegend=False,
        plot_bgcolor='#F8F9FA',
        paper_bgcolor='#FFFFFF',
        margin=dict(t=100, b=60, l=60, r=60)
    )
    
    # Update axis titles with enhanced styling
    fig.update_xaxes(
        title_text="<b>Date</b>",
        title_font=dict(size=15, color='#2C3E50', family='Arial Black'),
        tickfont=dict(size=12, color='#6C5CE7'),
        gridcolor='#E9ECEF',
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="<b>Applications</b>",
        title_font=dict(size=15, color='#2C3E50', family='Arial Black'),
        tickfont=dict(size=12, color='#6C5CE7'),
        gridcolor='#E9ECEF',
        row=2, col=1
    )
    fig.update_xaxes(
        title_text="<b>Day of Week</b>",
        title_font=dict(size=15, color='#2C3E50', family='Arial Black'),
        tickfont=dict(size=12, color='#6C5CE7'),
        row=2, col=2
    )
    fig.update_yaxes(
        title_text="<b>Applications</b>",
        title_font=dict(size=15, color='#2C3E50', family='Arial Black'),
        tickfont=dict(size=12, color='#6C5CE7'),
        gridcolor='#E9ECEF',
        row=2, col=2
    )
    
    # Add subtle background grid and styling
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E9ECEF', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E9ECEF', zeroline=False)
    
    # Add subtle shadows to subplots
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(showline=True, linewidth=2, linecolor='#DDD', row=i, col=j)
            fig.update_yaxes(showline=True, linewidth=2, linecolor='#DDD', row=i, col=j)
    
    fig.write_html("visualizations/complete_dashboard.html")
    print("Created: visualizations/complete_dashboard.html")

def main():
    """Main function to generate job application visualization dashboard"""
    print("Generating Job Application Analytics Dashboard")
    print("=" * 50)
    
    data = load_data()
    if not data:
        return
    
    os.makedirs("visualizations", exist_ok=True)
    
    print("\nCreating comprehensive dashboard...")
    
    # Create single comprehensive dashboard
    create_all_in_one_dashboard(data)
    
    print("\nVisualization created successfully!")
    print("File saved: visualizations/complete_dashboard.html")
    print("\nOpen the HTML file in your browser to view the interactive dashboard.")

if __name__ == "__main__":
    main()
