#!/usr/bin/env python3
"""
Generate an HTML table from all YAML project data files.
"""

import os
import sys
import json
import random
from pathlib import Path
from ruamel.yaml import YAML
from typing import List, Dict, Any, Optional

yaml = YAML()
yaml.default_flow_style = False

YAML_DIR = "../data"
OUTPUT_FILE = "ecosystem_table.html"

def load_yaml_files() -> List[Dict[str, Any]]:
    """Load 20 random YAML files from the data directory for testing."""
    projects = []
    data_path = Path(YAML_DIR)
    
    if not data_path.exists():
        print(f"Error: Data directory {YAML_DIR} not found")
        sys.exit(1)
    
    # Get all YAML files and randomly select 20
    yaml_files = list(data_path.glob("*.yaml"))
    selected_files = random.sample(yaml_files, min(20, len(yaml_files)))
    
    for yaml_file in selected_files:
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

def generate_smart_filter_html(filter_values: Dict[str, List[str]]) -> str:
    """Generate HTML for smart filter section with dropdowns."""
    
    filter_html = '''
        <!-- Active Filters Bar -->
        <div class="active-filters-bar">
            <span class="active-filters-label">ACTIVE FILTERS:</span>
            <div id="active-filters-container">
                <span id="no-filters-msg" style="color: #6c757d; font-style: italic; font-size: 13px;">No filters active</span>
            </div>
            <div class="add-filter-btn" onclick="toggleAddFilterDropdown()" id="add-filter-btn">
                + Add Filter
                <div class="add-filter-dropdown" id="add-filter-dropdown">'''
    
    # Generate add filter options
    filter_types = [
        ('category', 'Category', 'multi-select'),
        ('ecosystem', 'Ecosystem', 'multi-select'), 
        ('layer', 'Layer', 'multi-select'),
        ('target_audience', 'Target Audience', 'multi-select'),
        ('technology', 'Technology Readiness', 'multi-select'),
        ('business', 'Business Readiness', 'multi-select'),
        ('treasury_funded', 'Treasury Funded', 'toggle'),
        ('audit', 'Audited', 'toggle')
    ]
    
    for filter_key, display_name, filter_type in filter_types:
        filter_html += f'''
                    <div class="add-filter-option" onclick="event.stopPropagation(); addFilter('{filter_key}', '{display_name}', '{filter_type}')">
                        <span>{display_name}</span>
                        <span class="data-type-badge">{filter_type}</span>
                    </div>'''
    
    filter_html += '''
                </div>
            </div>
            <div class="filter-status" id="filter-status">336 projects</div>
        </div>
        
        <!-- Controls Toolbar -->
        <div class="controls-toolbar">
            <button class="btn" onclick="clearAllFilters()">🔄 Clear All Filters</button>
            <button class="btn" onclick="saveView()">💾 Save View</button>
        </div>
        
        <!-- Hidden filter data for JavaScript -->
        <script type="application/json" id="filter-data">'''
    
    filter_html += json.dumps(filter_values)
    filter_html += '</script>'
    
    return filter_html

def generate_dynamic_html_table() -> str:
    """Generate lightweight dynamic HTML table that loads JSON data."""
    
    # Read the dynamic template
    template_path = os.path.join(os.path.dirname(__file__), 'dynamic_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    """Main function to generate the HTML table."""
    print("Loading YAML files...")
    projects = load_yaml_files()
    
    if not projects:
        print("No project data found!")
        sys.exit(1)
    
    print(f"Found {len(projects)} projects")
    
    print("Generating dynamic HTML table...")
    html_content = generate_dynamic_html_table()
    
    # Write HTML file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Write aggregated JSON file for dynamic loading
    import json
    from datetime import date, datetime
    
    def json_serializer(obj):
        """Custom JSON serializer for date objects"""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
    
    json_file = OUTPUT_FILE.replace('.html', '_projects.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2, ensure_ascii=False, default=json_serializer)
    
    print(f"Files generated:")
    print(f"- {OUTPUT_FILE} (full static version)")
    print(f"- {json_file} (aggregated data for dynamic loading)")
    print(f"Open {os.path.abspath(OUTPUT_FILE)} in your browser to view the table.")

if __name__ == "__main__":
    main()