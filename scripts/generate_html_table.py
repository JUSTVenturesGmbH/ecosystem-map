#!/usr/bin/env python3
"""
Generate an HTML table from all YAML project data files.
"""

import os
import sys
from pathlib import Path
from ruamel.yaml import YAML
from typing import List, Dict, Any, Optional

yaml = YAML()
yaml.default_flow_style = False

YAML_DIR = "../data"
OUTPUT_FILE = "ecosystem_table.html"

def load_yaml_files() -> List[Dict[str, Any]]:
    """Load all YAML files from the data directory."""
    projects = []
    data_path = Path(YAML_DIR)
    
    if not data_path.exists():
        print(f"Error: Data directory {YAML_DIR} not found")
        sys.exit(1)
    
    for yaml_file in data_path.glob("*.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                project_data = yaml.load(f)
                if project_data:
                    projects.append(project_data)
        except Exception as e:
            print(f"Error loading {yaml_file}: {e}")
    
    return projects

def format_array_field(field: Optional[List[str]]) -> str:
    """Format array fields as comma-separated strings."""
    if not field:
        return ""
    return ", ".join(field)

def format_web_links(web: Dict[str, Any]) -> str:
    """Format web links as HTML links."""
    links = []
    
    if web.get('site'):
        links.append(f'<a href="{web["site"]}" target="_blank">Website</a>')
    if web.get('github'):
        links.append(f'<a href="{web["github"]}" target="_blank">GitHub</a>')
    if web.get('documentation'):
        links.append(f'<a href="{web["documentation"]}" target="_blank">Docs</a>')
    if web.get('twitter'):
        twitter_url = web["twitter"] if web["twitter"].startswith('http') else f'https://twitter.com/{web["twitter"]}'
        links.append(f'<a href="{twitter_url}" target="_blank">Twitter</a>')
    if web.get('discord'):
        links.append(f'<a href="{web["discord"]}" target="_blank">Discord</a>')
    if web.get('blog'):
        links.append(f'<a href="{web["blog"]}" target="_blank">Blog</a>')
    if web.get('contact'):
        contact_url = web["contact"] if web["contact"].startswith('http') else f'mailto:{web["contact"]}'
        links.append(f'<a href="{contact_url}" target="_blank">Contact</a>')
    if web.get('playstore'):
        links.append(f'<a href="{web["playstore"]}" target="_blank">Play Store</a>')
    if web.get('appstore'):
        links.append(f'<a href="{web["appstore"]}" target="_blank">App Store</a>')
    if web.get('webstore'):
        links.append(f'<a href="{web["webstore"]}" target="_blank">Web Store</a>')
    
    return " | ".join(links)

def get_latest_metric(metrics: Dict[str, Any], metric_type: str) -> str:
    """Get the latest value for a specific metric."""
    if not metrics or metric_type not in metrics:
        return ""
    
    metric_data = metrics[metric_type]
    if not metric_data:
        return ""
    
    # Get the latest entry (assuming sorted by date)
    latest = max(metric_data, key=lambda x: x.get('date', ''))
    return str(latest.get('value', ''))

def format_readiness(readiness: Optional[Dict[str, str]]) -> str:
    """Format readiness information."""
    if not readiness:
        return ""
    
    tech = readiness.get('technology', '')
    business = readiness.get('business', '')
    
    parts = []
    if tech:
        parts.append(f"Tech: {tech}")
    if business:
        parts.append(f"Business: {business}")
    
    return " | ".join(parts)

def collect_filter_values(projects: List[Dict[str, Any]]) -> Dict[str, set]:
    """Collect all unique values for filterable fields."""
    filters = {
        'category': set(),
        'ecosystem': set(),
        'layer': set(),
        'target_audience': set(),
        'technology': set(),
        'business': set(),
        'treasury_funded': set(),
        'audit': set()
    }
    
    for project in projects:
        # Array fields
        for field in ['category', 'ecosystem', 'layer', 'target_audience']:
            values = project.get(field, [])
            if values:
                filters[field].update(values)
        
        # Readiness fields
        readiness = project.get('readiness', {})
        if readiness.get('technology'):
            filters['technology'].add(readiness['technology'])
        if readiness.get('business'):
            filters['business'].add(readiness['business'])
        
        # Boolean fields
        treasury = project.get('treasury_funded')
        if treasury is not None:
            filters['treasury_funded'].add(str(treasury))
        
        audit = project.get('audit')
        if audit is not None:
            filters['audit'].add(str(audit))
    
    # Convert sets to sorted lists
    for key in filters:
        filters[key] = sorted(list(filters[key]))
    
    return filters

def generate_filter_html(filter_values: Dict[str, List[str]]) -> str:
    """Generate HTML for filter section."""
    
    filter_html = '''
        <div class="filter-section">
            <h3>Data Filters</h3>
            <div class="filter-controls">
                <button onclick="clearAllFilters()">Clear All Filters</button>
                <button onclick="applyFilters()">Apply Filters</button>
                <span id="filter-status" style="margin-left: 15px; font-size: 12px; color: #666;"></span>
            </div>
    '''
    
    # Category filter
    if filter_values.get('category'):
        filter_html += '''
            <div class="filter-group">
                <h4>Category</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['category']:
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-category-{value.replace(' ', '-').lower()}" value="{value}" onchange="updateFilters()">
                        <label for="filter-category-{value.replace(' ', '-').lower()}">{value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Ecosystem filter
    if filter_values.get('ecosystem'):
        filter_html += '''
            <div class="filter-group">
                <h4>Ecosystem</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['ecosystem']:
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-ecosystem-{value.replace(' ', '-').lower()}" value="{value}" onchange="updateFilters()">
                        <label for="filter-ecosystem-{value.replace(' ', '-').lower()}">{value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Layer filter
    if filter_values.get('layer'):
        filter_html += '''
            <div class="filter-group">
                <h4>Layer</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['layer']:
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-layer-{value.replace('-', '').lower()}" value="{value}" onchange="updateFilters()">
                        <label for="filter-layer-{value.replace('-', '').lower()}">{value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Target Audience filter
    if filter_values.get('target_audience'):
        filter_html += '''
            <div class="filter-group">
                <h4>Target Audience</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['target_audience']:
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-audience-{value.replace(' ', '-').lower()}" value="{value}" onchange="updateFilters()">
                        <label for="filter-audience-{value.replace(' ', '-').lower()}">{value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Technology Readiness filter
    if filter_values.get('technology'):
        filter_html += '''
            <div class="filter-group">
                <h4>Technology Readiness</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['technology']:
            safe_id = value.replace(' ', '-').replace('/', '-').lower()
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-tech-{safe_id}" value="{value}" onchange="updateFilters()">
                        <label for="filter-tech-{safe_id}">{value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Business Readiness filter
    if filter_values.get('business'):
        filter_html += '''
            <div class="filter-group">
                <h4>Business Readiness</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['business']:
            safe_id = value.replace(' ', '-').replace('/', '-').lower()
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-business-{safe_id}" value="{value}" onchange="updateFilters()">
                        <label for="filter-business-{safe_id}">{value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Treasury Funded filter
    if filter_values.get('treasury_funded'):
        filter_html += '''
            <div class="filter-group">
                <h4>Treasury Funded</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['treasury_funded']:
            display_value = 'Yes' if value == 'True' else 'No'
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-treasury-{value.lower()}" value="{value}" onchange="updateFilters()">
                        <label for="filter-treasury-{value.lower()}">{display_value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    # Audit filter
    if filter_values.get('audit'):
        filter_html += '''
            <div class="filter-group">
                <h4>Audited</h4>
                <div class="filter-checkboxes">
        '''
        for value in filter_values['audit']:
            display_value = 'Yes' if value == 'True' else 'No'
            filter_html += f'''
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filter-audit-{value.lower()}" value="{value}" onchange="updateFilters()">
                        <label for="filter-audit-{value.lower()}">{display_value}</label>
                    </div>
            '''
        filter_html += '</div></div>'
    
    filter_html += '</div>'
    return filter_html

def generate_html_table(projects: List[Dict[str, Any]]) -> str:
    """Generate HTML table from project data."""
    
    # Sort projects by name
    projects.sort(key=lambda x: x.get('name', ''))
    
    # Collect filter values
    filter_values = collect_filter_values(projects)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polkadot Ecosystem Map - All Projects</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: calc(100vw - 40px);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .table-wrapper {
            overflow-x: auto;
            margin-top: 20px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            position: relative;
        }
        .table-wrapper::after {
            content: "← Scroll horizontally to see all columns →";
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 123, 255, 0.1);
            color: #007bff;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 11px;
            opacity: 0.7;
            pointer-events: none;
            white-space: nowrap;
        }
        table {
            width: max-content;
            min-width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            white-space: nowrap;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f0f0f0;
        }
        .project-name {
            font-weight: 600;
            color: #2c3e50;
        }
        .description {
            max-width: 300px;
            word-wrap: break-word;
            white-space: normal;
        }
        .links a {
            color: #007bff;
            text-decoration: none;
            margin-right: 5px;
        }
        .links a:hover {
            text-decoration: underline;
        }
        .category, .ecosystem, .audience {
            font-size: 12px;
        }
        .status {
            font-size: 12px;
            color: #666;
        }
        .metrics {
            font-size: 11px;
            color: #666;
        }
        .boolean-yes {
            color: #28a745;
            font-weight: bold;
        }
        .boolean-no {
            color: #dc3545;
        }
        .summary {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        .column-selector {
            margin-bottom: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .column-selector h3 {
            margin-top: 0;
            margin-bottom: 15px;
            color: #495057;
        }
        .column-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-bottom: 15px;
        }
        .column-controls button {
            padding: 8px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .column-controls button:hover {
            background-color: #0056b3;
        }
        .column-checkboxes {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .column-checkbox {
            display: flex;
            align-items: center;
            padding: 5px;
        }
        .column-checkbox input[type="checkbox"] {
            margin-right: 8px;
        }
        .column-checkbox label {
            font-size: 13px;
            cursor: pointer;
            user-select: none;
        }
        .hidden-column {
            display: none !important;
        }
        .filter-section {
            margin-bottom: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .filter-section h3 {
            margin-top: 0;
            margin-bottom: 15px;
            color: #495057;
        }
        .filter-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-bottom: 15px;
        }
        .filter-controls button {
            padding: 8px 15px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .filter-controls button:hover {
            background-color: #218838;
        }
        .filter-group {
            margin-bottom: 15px;
        }
        .filter-group h4 {
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #495057;
        }
        .filter-checkboxes {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 8px;
        }
        .filter-checkbox {
            display: flex;
            align-items: center;
            padding: 3px;
        }
        .filter-checkbox input[type="checkbox"] {
            margin-right: 6px;
        }
        .filter-checkbox label {
            font-size: 12px;
            cursor: pointer;
            user-select: none;
        }
        .hidden-row {
            display: none !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Polkadot Ecosystem Map - All Projects</h1>
        <div class="summary">
            <strong>Total Projects:</strong> """ + str(len(projects)) + """
        </div>
        
        """ + generate_filter_html(filter_values) + """
        
        <div class="column-selector">
            <h3>Column Visibility</h3>
            <div class="column-controls">
                <button onclick="showAllColumns()">Show All</button>
                <button onclick="hideAllColumns()">Hide All</button>
                <button onclick="showCoreColumns()">Core Only</button>
                <button onclick="showWebColumns()">Web Links Only</button>
                <button onclick="showMetricsColumns()">Metrics Only</button>
            </div>
            <div class="column-checkboxes">
                <div class="column-checkbox">
                    <input type="checkbox" id="col-name" checked onchange="toggleColumn('name')">
                    <label for="col-name">Project Name</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-description" checked onchange="toggleColumn('description')">
                    <label for="col-description">Description</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-category" checked onchange="toggleColumn('category')">
                    <label for="col-category">Category</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-ecosystem" checked onchange="toggleColumn('ecosystem')">
                    <label for="col-ecosystem">Ecosystem</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-layer" checked onchange="toggleColumn('layer')">
                    <label for="col-layer">Layer</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-audience" checked onchange="toggleColumn('audience')">
                    <label for="col-audience">Target Audience</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-website" checked onchange="toggleColumn('website')">
                    <label for="col-website">Website</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-github" checked onchange="toggleColumn('github')">
                    <label for="col-github">GitHub</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-documentation" checked onchange="toggleColumn('documentation')">
                    <label for="col-documentation">Documentation</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-twitter" checked onchange="toggleColumn('twitter')">
                    <label for="col-twitter">Twitter</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-discord" checked onchange="toggleColumn('discord')">
                    <label for="col-discord">Discord</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-blog" checked onchange="toggleColumn('blog')">
                    <label for="col-blog">Blog</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-contact" checked onchange="toggleColumn('contact')">
                    <label for="col-contact">Contact</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-playstore" checked onchange="toggleColumn('playstore')">
                    <label for="col-playstore">Play Store</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-appstore" checked onchange="toggleColumn('appstore')">
                    <label for="col-appstore">App Store</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-webstore" checked onchange="toggleColumn('webstore')">
                    <label for="col-webstore">Web Store</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-logo" checked onchange="toggleColumn('logo')">
                    <label for="col-logo">Logo</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-readiness" checked onchange="toggleColumn('readiness')">
                    <label for="col-readiness">Readiness</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-github-stars" checked onchange="toggleColumn('github-stars')">
                    <label for="col-github-stars">GitHub Stars</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-twitter-followers" checked onchange="toggleColumn('twitter-followers')">
                    <label for="col-twitter-followers">Twitter Followers</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-discord-members" checked onchange="toggleColumn('discord-members')">
                    <label for="col-discord-members">Discord Members</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-treasury" checked onchange="toggleColumn('treasury')">
                    <label for="col-treasury">Treasury Funded</label>
                </div>
                <div class="column-checkbox">
                    <input type="checkbox" id="col-audit" checked onchange="toggleColumn('audit')">
                    <label for="col-audit">Audited</label>
                </div>
            </div>
        </div>
        <div class="table-wrapper">
            <table>
            <thead>
                <tr>
                    <th data-column="name">Project Name</th>
                    <th data-column="description">Description</th>
                    <th data-column="category">Category</th>
                    <th data-column="ecosystem">Ecosystem</th>
                    <th data-column="layer">Layer</th>
                    <th data-column="audience">Target Audience</th>
                    <th data-column="website">Website</th>
                    <th data-column="github">GitHub</th>
                    <th data-column="documentation">Documentation</th>
                    <th data-column="twitter">Twitter</th>
                    <th data-column="discord">Discord</th>
                    <th data-column="blog">Blog</th>
                    <th data-column="contact">Contact</th>
                    <th data-column="playstore">Play Store</th>
                    <th data-column="appstore">App Store</th>
                    <th data-column="webstore">Web Store</th>
                    <th data-column="logo">Logo</th>
                    <th data-column="readiness">Readiness</th>
                    <th data-column="github-stars">GitHub Stars</th>
                    <th data-column="twitter-followers">Twitter Followers</th>
                    <th data-column="discord-members">Discord Members</th>
                    <th data-column="treasury">Treasury Funded</th>
                    <th data-column="audit">Audited</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for project in projects:
        name = project.get('name', 'Unknown')
        description = project.get('description', '')
        category = format_array_field(project.get('category'))
        ecosystem = format_array_field(project.get('ecosystem'))
        layer = format_array_field(project.get('layer'))
        target_audience = format_array_field(project.get('target_audience'))
        
        web = project.get('web', {})
        
        # Individual web fields
        website = f'<a href="{web.get("site", "")}" target="_blank">Link</a>' if web.get('site') else ''
        github = f'<a href="{web.get("github", "")}" target="_blank">Link</a>' if web.get('github') else ''
        documentation = f'<a href="{web.get("documentation", "")}" target="_blank">Link</a>' if web.get('documentation') else ''
        
        twitter_handle = web.get('twitter', '')
        twitter_link = ''
        if twitter_handle:
            twitter_url = twitter_handle if twitter_handle.startswith('http') else f'https://twitter.com/{twitter_handle}'
            twitter_link = f'<a href="{twitter_url}" target="_blank">@{twitter_handle.replace("https://twitter.com/", "").replace("https://x.com/", "")}</a>'
        
        discord_link = f'<a href="{web.get("discord", "")}" target="_blank">Link</a>' if web.get('discord') else ''
        blog = f'<a href="{web.get("blog", "")}" target="_blank">Link</a>' if web.get('blog') else ''
        
        contact = web.get('contact', '')
        contact_link = ''
        if contact:
            contact_url = contact if contact.startswith('http') else f'mailto:{contact}'
            contact_link = f'<a href="{contact_url}" target="_blank">{contact}</a>'
        
        playstore = f'<a href="{web.get("playstore", "")}" target="_blank">Link</a>' if web.get('playstore') else ''
        appstore = f'<a href="{web.get("appstore", "")}" target="_blank">Link</a>' if web.get('appstore') else ''
        webstore = f'<a href="{web.get("webstore", "")}" target="_blank">Link</a>' if web.get('webstore') else ''
        logo = web.get('logo', '')
        
        readiness = format_readiness(project.get('readiness'))
        
        metrics = project.get('metrics', {})
        github_stars = get_latest_metric(metrics, 'github')
        twitter_followers = get_latest_metric(metrics, 'twitter')
        discord_members = get_latest_metric(metrics, 'discord')
        
        treasury_funded = project.get('treasury_funded', False)
        audit = project.get('audit', False)
        
        treasury_text = '<span class="boolean-yes">✓</span>' if treasury_funded else '<span class="boolean-no">✗</span>'
        audit_text = '<span class="boolean-yes">✓</span>' if audit else '<span class="boolean-no">✗</span>'
        
        # Create filter data attributes
        readiness_obj = project.get('readiness', {})
        tech_readiness = readiness_obj.get('technology', '')
        business_readiness = readiness_obj.get('business', '')
        
        filter_attrs = []
        filter_attrs.append(f'data-category="{"|".join(project.get("category", []))}"')
        filter_attrs.append(f'data-ecosystem="{"|".join(project.get("ecosystem", []))}"')
        filter_attrs.append(f'data-layer="{"|".join(project.get("layer", []))}"')
        filter_attrs.append(f'data-audience="{"|".join(project.get("target_audience", []))}"')
        filter_attrs.append(f'data-tech-readiness="{tech_readiness}"')
        filter_attrs.append(f'data-business-readiness="{business_readiness}"')
        filter_attrs.append(f'data-treasury="{str(treasury_funded)}"')
        filter_attrs.append(f'data-audit="{str(audit)}"')
        
        html += f"""
                <tr {" ".join(filter_attrs)}>
                    <td data-column="name" class="project-name">{name}</td>
                    <td data-column="description" class="description">{description}</td>
                    <td data-column="category" class="category">{category}</td>
                    <td data-column="ecosystem" class="ecosystem">{ecosystem}</td>
                    <td data-column="layer">{layer}</td>
                    <td data-column="audience" class="audience">{target_audience}</td>
                    <td data-column="website" class="links">{website}</td>
                    <td data-column="github" class="links">{github}</td>
                    <td data-column="documentation" class="links">{documentation}</td>
                    <td data-column="twitter" class="links">{twitter_link}</td>
                    <td data-column="discord" class="links">{discord_link}</td>
                    <td data-column="blog" class="links">{blog}</td>
                    <td data-column="contact" class="links">{contact_link}</td>
                    <td data-column="playstore" class="links">{playstore}</td>
                    <td data-column="appstore" class="links">{appstore}</td>
                    <td data-column="webstore" class="links">{webstore}</td>
                    <td data-column="logo">{logo}</td>
                    <td data-column="readiness" class="status">{readiness}</td>
                    <td data-column="github-stars" class="metrics">{github_stars}</td>
                    <td data-column="twitter-followers" class="metrics">{twitter_followers}</td>
                    <td data-column="discord-members" class="metrics">{discord_members}</td>
                    <td data-column="treasury">{treasury_text}</td>
                    <td data-column="audit">{audit_text}</td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
        </div>
    </div>
    <script>
        // Filter functionality
        let activeFilters = {
            category: [],
            ecosystem: [],
            layer: [],
            audience: [],
            technology: [],
            business: [],
            treasury_funded: [],
            audit: []
        };
        
        function updateFilters() {
            // Collect all checked filters
            activeFilters.category = Array.from(document.querySelectorAll('input[id^="filter-category-"]:checked')).map(cb => cb.value);
            activeFilters.ecosystem = Array.from(document.querySelectorAll('input[id^="filter-ecosystem-"]:checked')).map(cb => cb.value);
            activeFilters.layer = Array.from(document.querySelectorAll('input[id^="filter-layer-"]:checked')).map(cb => cb.value);
            activeFilters.audience = Array.from(document.querySelectorAll('input[id^="filter-audience-"]:checked')).map(cb => cb.value);
            activeFilters.technology = Array.from(document.querySelectorAll('input[id^="filter-tech-"]:checked')).map(cb => cb.value);
            activeFilters.business = Array.from(document.querySelectorAll('input[id^="filter-business-"]:checked')).map(cb => cb.value);
            activeFilters.treasury_funded = Array.from(document.querySelectorAll('input[id^="filter-treasury-"]:checked')).map(cb => cb.value);
            activeFilters.audit = Array.from(document.querySelectorAll('input[id^="filter-audit-"]:checked')).map(cb => cb.value);
            
            applyFilters();
        }
        
        function applyFilters() {
            const rows = document.querySelectorAll('tbody tr');
            let visibleCount = 0;
            
            rows.forEach(row => {
                let shouldShow = true;
                
                // Check each filter category
                if (activeFilters.category.length > 0) {
                    const rowCategories = (row.getAttribute('data-category') || '').split('|');
                    const hasMatch = activeFilters.category.some(filter => rowCategories.includes(filter));
                    if (!hasMatch) shouldShow = false;
                }
                
                if (activeFilters.ecosystem.length > 0) {
                    const rowEcosystems = (row.getAttribute('data-ecosystem') || '').split('|');
                    const hasMatch = activeFilters.ecosystem.some(filter => rowEcosystems.includes(filter));
                    if (!hasMatch) shouldShow = false;
                }
                
                if (activeFilters.layer.length > 0) {
                    const rowLayers = (row.getAttribute('data-layer') || '').split('|');
                    const hasMatch = activeFilters.layer.some(filter => rowLayers.includes(filter));
                    if (!hasMatch) shouldShow = false;
                }
                
                if (activeFilters.audience.length > 0) {
                    const rowAudiences = (row.getAttribute('data-audience') || '').split('|');
                    const hasMatch = activeFilters.audience.some(filter => rowAudiences.includes(filter));
                    if (!hasMatch) shouldShow = false;
                }
                
                if (activeFilters.technology.length > 0) {
                    const rowTech = row.getAttribute('data-tech-readiness') || '';
                    if (!activeFilters.technology.includes(rowTech)) shouldShow = false;
                }
                
                if (activeFilters.business.length > 0) {
                    const rowBusiness = row.getAttribute('data-business-readiness') || '';
                    if (!activeFilters.business.includes(rowBusiness)) shouldShow = false;
                }
                
                if (activeFilters.treasury_funded.length > 0) {
                    const rowTreasury = row.getAttribute('data-treasury') || '';
                    if (!activeFilters.treasury_funded.includes(rowTreasury)) shouldShow = false;
                }
                
                if (activeFilters.audit.length > 0) {
                    const rowAudit = row.getAttribute('data-audit') || '';
                    if (!activeFilters.audit.includes(rowAudit)) shouldShow = false;
                }
                
                // Show/hide row
                row.classList.toggle('hidden-row', !shouldShow);
                if (shouldShow) visibleCount++;
            });
            
            // Update status
            const totalCount = rows.length;
            const statusElement = document.getElementById('filter-status');
            if (statusElement) {
                const activeFilterCount = Object.values(activeFilters).reduce((sum, arr) => sum + arr.length, 0);
                if (activeFilterCount === 0) {
                    statusElement.textContent = `Showing all ${totalCount} projects`;
                } else {
                    statusElement.textContent = `Showing ${visibleCount} of ${totalCount} projects (${activeFilterCount} filters active)`;
                }
            }
        }
        
        function clearAllFilters() {
            // Uncheck all filter checkboxes
            document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });
            
            // Clear active filters
            Object.keys(activeFilters).forEach(key => {
                activeFilters[key] = [];
            });
            
            applyFilters();
        }
        
        // Column visibility functionality
        function toggleColumn(columnName) {
            const checkbox = document.getElementById('col-' + columnName);
            const isVisible = checkbox.checked;
            
            // Toggle header
            const header = document.querySelector('th[data-column="' + columnName + '"]');
            if (header) {
                header.classList.toggle('hidden-column', !isVisible);
            }
            
            // Toggle all data cells for this column
            const cells = document.querySelectorAll('td[data-column="' + columnName + '"]');
            cells.forEach(cell => {
                cell.classList.toggle('hidden-column', !isVisible);
            });
        }
        
        function showAllColumns() {
            const checkboxes = document.querySelectorAll('.column-checkbox input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
                const columnName = checkbox.id.replace('col-', '');
                toggleColumn(columnName);
            });
        }
        
        function hideAllColumns() {
            const checkboxes = document.querySelectorAll('.column-checkbox input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
                const columnName = checkbox.id.replace('col-', '');
                toggleColumn(columnName);
            });
        }
        
        function showCoreColumns() {
            hideAllColumns();
            const coreColumns = ['name', 'description', 'category', 'ecosystem', 'layer'];
            coreColumns.forEach(columnName => {
                const checkbox = document.getElementById('col-' + columnName);
                if (checkbox) {
                    checkbox.checked = true;
                    toggleColumn(columnName);
                }
            });
        }
        
        function showWebColumns() {
            hideAllColumns();
            const webColumns = ['name', 'website', 'github', 'documentation', 'twitter', 'discord', 'blog', 'contact', 'playstore', 'appstore', 'webstore'];
            webColumns.forEach(columnName => {
                const checkbox = document.getElementById('col-' + columnName);
                if (checkbox) {
                    checkbox.checked = true;
                    toggleColumn(columnName);
                }
            });
        }
        
        function showMetricsColumns() {
            hideAllColumns();
            const metricsColumns = ['name', 'github-stars', 'twitter-followers', 'discord-members', 'treasury', 'audit'];
            metricsColumns.forEach(columnName => {
                const checkbox = document.getElementById('col-' + columnName);
                if (checkbox) {
                    checkbox.checked = true;
                    toggleColumn(columnName);
                }
            });
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            // All columns are shown by default, no additional initialization needed
            console.log('Column selector initialized - ' + document.querySelectorAll('th[data-column]').length + ' columns available');
        });
    </script>
</body>
</html>"""
    
    return html

def main():
    """Main function to generate the HTML table."""
    print("Loading YAML files...")
    projects = load_yaml_files()
    
    if not projects:
        print("No project data found!")
        sys.exit(1)
    
    print(f"Found {len(projects)} projects")
    
    print("Generating HTML table...")
    html_content = generate_html_table(projects)
    
    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML table generated: {OUTPUT_FILE}")
    print(f"Open {os.path.abspath(OUTPUT_FILE)} in your browser to view the table.")

if __name__ == "__main__":
    main()