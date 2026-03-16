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
SCHEMA_FILE = "../data.schema.yml"
OUTPUT_FILE = "ecosystem_table.html"

def load_yaml_files() -> List[Dict[str, Any]]:
    """Load all YAML files from the data directory."""
    projects = []
    data_path = Path(YAML_DIR)
    
    if not data_path.exists():
        print(f"Error: Data directory {YAML_DIR} not found")
        sys.exit(1)
    
    # Get all YAML files
    yaml_files = list(data_path.glob("*.yaml"))
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                project_data = yaml.load(f)
                if project_data:
                    projects.append(project_data)
        except Exception as e:
            print(f"Error loading {yaml_file}: {e}")
    
    return projects

def load_schema() -> Dict[str, Any]:
    """Load the data schema file."""
    schema_path = Path(SCHEMA_FILE)
    if not schema_path.exists():
        print(f"Error: Schema file {SCHEMA_FILE} not found")
        sys.exit(1)
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return yaml.load(f)

def parse_schema_fields(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Parse schema to extract all field definitions."""
    properties = schema.get('properties', {})
    flat_fields = {}
    
    def parse_property(prop_name: str, prop_def: Dict[str, Any], parent_path: str = ""):
        full_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
        
        if prop_def.get('type') == 'object' and 'properties' in prop_def:
            # Nested object - recurse into its properties and flatten them
            for nested_name, nested_def in prop_def['properties'].items():
                parse_property(nested_name, nested_def, full_path)
        elif prop_def.get('type') == 'array':
            # Array field
            items_def = prop_def.get('items', {})
            enum_values = items_def.get('enum', []) if isinstance(items_def, dict) else []
            flat_fields[full_path] = {
                'type': 'array',
                'enum': enum_values,
                'path': full_path,
                'description': prop_def.get('description', '')
            }
        else:
            # Simple field
            flat_fields[full_path] = {
                'type': prop_def.get('type', 'string'),
                'enum': prop_def.get('enum', []),
                'path': full_path,
                'description': prop_def.get('description', '')
            }
    
    for prop_name, prop_def in properties.items():
        parse_property(prop_name, prop_def)
    
    return flat_fields

def generate_column_tree_html(fields: Dict[str, Any]) -> str:
    """Generate HTML for the column selection tree based on schema fields."""
    
    # Group fields by top-level categories
    grouped_fields = {}
    default_visible = {'name', 'description', 'category', 'ecosystem'}
    
    for field_path, field_def in fields.items():
        if '.' in field_path:
            # Nested field
            top_level = field_path.split('.')[0]
            if top_level not in grouped_fields:
                grouped_fields[top_level] = []
            grouped_fields[top_level].append((field_path, field_def))
        else:
            # Top-level field
            if 'simple' not in grouped_fields:
                grouped_fields['simple'] = []
            grouped_fields['simple'].append((field_path, field_def))
    
    tree_html = '<div class="column-tree">'
    
    # Generate simple fields first
    if 'simple' in grouped_fields:
        for field_path, field_def in grouped_fields['simple']:
            field_id = field_path.replace('_', '-').replace('.', '-')
            display_name = field_path.replace('_', ' ').title()
            is_checked = field_path in default_visible
            
            tree_html += f'''
                <div class="tree-leaf">
                    <input type="checkbox" id="col-{field_id}" {'checked' if is_checked else ''} onchange="toggleColumn('{field_path}')">
                    <label for="col-{field_id}">{display_name}</label>
                </div>'''
    
    # Generate grouped fields
    for group_name, group_fields in grouped_fields.items():
        if group_name == 'simple':
            continue
            
        group_id = group_name.replace('_', '-')
        display_name = group_name.replace('_', ' ').title()
        
        # Check if any child is checked by default
        any_checked = any(field_path in default_visible for field_path, _ in group_fields)
        
        tree_html += f'''
            <div class="tree-node">
                <div class="tree-item" onclick="toggleBranch('{group_id}')">
                    <span class="tree-toggle">▼</span>
                    <input type="checkbox" id="{group_id}-branch" {'checked' if any_checked else ''} onchange="toggleBranchCheckboxes('{group_id}')">
                    <label for="{group_id}-branch">{display_name}</label>
                </div>
                <div class="tree-children" id="{group_id}-children">'''
        
        for field_path, field_def in group_fields:
            field_id = field_path.replace('_', '-').replace('.', '-')
            child_display_name = field_path.split('.')[-1].replace('_', ' ').title()
            is_checked = field_path in default_visible
            
            tree_html += f'''
                    <div class="tree-leaf">
                        <input type="checkbox" id="col-{field_id}" {'checked' if is_checked else ''} onchange="toggleColumn('{field_path}')">
                        <label for="col-{field_id}">{child_display_name}</label>
                    </div>'''
        
        tree_html += '''
                </div>
            </div>'''
    
    tree_html += '</div>'
    return tree_html

def generate_table_headers(fields: Dict[str, Any]) -> str:
    """Generate table headers based on schema fields."""
    headers_html = '<thead id="table-header">\n                    <tr>\n'
    
    default_visible = {'name', 'description', 'category', 'ecosystem'}
    
    for field_path, field_def in fields.items():
        # Generate display name
        if '.' in field_path:
            display_name = field_path.split('.')[-1].replace('_', ' ').title()
        else:
            display_name = field_path.replace('_', ' ').title()
            
        css_class = f"col-{field_path.replace('.', '-').replace('_', '-')}"
        is_visible = field_path in default_visible
        hidden_class = "" if is_visible else " hidden-column"
        
        headers_html += f'                        <th class="{css_class}{hidden_class}">{display_name}</th>\n'
    
    headers_html += '                    </tr>\n                </thead>'
    return headers_html

def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """Get value from nested object using dot notation path."""
    keys = path.split('.')
    value = obj
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def format_cell_value(value: Any, field_name: str, field_def: Dict[str, Any]) -> str:
    """Format cell value based on field type and name."""
    if value is None:
        return ""
    
    # Handle array fields
    if field_def['type'] == 'array' and isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    
    # Handle boolean fields
    if isinstance(value, bool):
        return "Yes" if value else "No"
    
    # Handle web links
    if field_name.startswith('web.'):
        if field_name == 'web.site' and value:
            return f'<a href="{value}" target="_blank" rel="noopener">{value}</a>'
        elif value:
            link_text = field_name.split('.')[-1].title()
            full_url = value if value.startswith('http') else f'https://{value}'
            return f'<a href="{full_url}" target="_blank" rel="noopener">{link_text}</a>'
    
    return str(value)

def generate_column_mapping(fields: Dict[str, Any]) -> Dict[str, int]:
    """Generate column mapping based on schema fields."""
    mapping = {}
    column_index = 0
    
    for field_path, field_def in fields.items():
        mapping[field_path] = column_index
        column_index += 1
    
    return mapping

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
    
    # Load schema and parse fields
    print("Loading schema...")
    schema = load_schema()
    fields = parse_schema_fields(schema)
    
    # Generate column tree HTML
    print("Generating column selection tree from schema...")
    column_tree_html = generate_column_tree_html(fields)
    
    # Read the dynamic template
    template_path = os.path.join(os.path.dirname(__file__), 'dynamic_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Generate table headers and column mapping
    print("Generating table headers and column mapping...")
    table_headers = generate_table_headers(fields)
    column_mapping = generate_column_mapping(fields)
    
    # Define default visible columns
    default_visible = {'name', 'description', 'category', 'ecosystem'}
    
    # Replace the hardcoded column tree with the dynamically generated one
    column_tree_placeholder = '<div class="column-tree">'
    column_tree_end = '</div>\n                </div>\n            </div>\n        </div>'
    
    start_index = template_content.find(column_tree_placeholder)
    if start_index != -1:
        end_index = template_content.find(column_tree_end, start_index)
        if end_index != -1:
            # Replace the hardcoded tree with the dynamic one
            before = template_content[:start_index]
            after = template_content[end_index:]
            template_content = before + column_tree_html + after
    
    # Replace hardcoded table headers
    header_start = template_content.find('<thead id="table-header">')
    header_end = template_content.find('</thead>', header_start) + len('</thead>')
    if header_start != -1 and header_end != -1:
        before = template_content[:header_start]
        after = template_content[header_end:]
        template_content = before + table_headers + after
    
    # Generate JavaScript functions for dynamic cell creation
    dynamic_js_functions = '''
    
        // Dynamic cell generation functions
        function getNestedValue(obj, path) {
            const keys = path.split('.');
            let value = obj;
            for (const key of keys) {
                if (value && typeof value === 'object' && key in value) {
                    value = value[key];
                } else {
                    return null;
                }
            }
            return value;
        }
        
        function formatCellValue(value, fieldPath) {
            if (value === null || value === undefined) {
                return '';
            }
            
            // Handle array fields
            if (Array.isArray(value)) {
                return value.filter(v => v).join(', ');
            }
            
            // Handle boolean fields
            if (typeof value === 'boolean') {
                return value ? 'Yes' : 'No';
            }
            
            // Handle web links
            if (fieldPath.startsWith('web.')) {
                if (fieldPath === 'web.site' && value) {
                    return `<a href="${value}" target="_blank" rel="noopener">${value}</a>`;
                } else if (value) {
                    const linkText = fieldPath.split('.').pop().replace(/^\\w/, c => c.toUpperCase());
                    const fullUrl = value.startsWith('http') ? value : `https://${value}`;
                    return `<a href="${fullUrl}" target="_blank" rel="noopener">${linkText}</a>`;
                }
            }
            
            return String(value);
        }
        
        function createDynamicCell(project, fieldPath) {
            const value = getNestedValue(project, fieldPath);
            const formattedValue = formatCellValue(value, fieldPath);
            const className = `col-${fieldPath.replace(/\\./g, '-').replace(/_/g, '-')}`;
            
            const cell = document.createElement('td');
            cell.className = className;
            
            if (fieldPath.startsWith('web.') && value) {
                cell.innerHTML = formattedValue;
            } else {
                cell.textContent = formattedValue;
            }
            
            // Apply initial visibility
            if (!visibleColumns.has(fieldPath)) {
                cell.classList.add('hidden-column');
            }
            
            return cell;
        }
'''
    
    # Update the default visible columns to use correct field paths
    default_visible_fields = list(default_visible)
    
    # Inject column mapping and dynamic functions as JavaScript
    column_mapping_js = f"\n        let dynamicColumnMapping = {json.dumps(column_mapping, indent=8)};\n        let schemaFields = {json.dumps(fields, indent=8, default=str)};\n        let defaultVisibleColumns = {json.dumps(default_visible_fields)};{dynamic_js_functions}\n"
    
    # Find and replace the visibleColumns initialization
    visible_start = template_content.find("let visibleColumns = new Set(['name', 'description', 'category', 'ecosystem', 'website']);")
    if visible_start != -1:
        visible_end = visible_start + len("let visibleColumns = new Set(['name', 'description', 'category', 'ecosystem', 'website']);")
        before = template_content[:visible_start]
        after = template_content[visible_end:]
        template_content = before + f"let visibleColumns = new Set({json.dumps(default_visible_fields)});" + after
    
    # Find the column mapping section and replace it
    mapping_start = template_content.find('let columnMapping = {')
    if mapping_start != -1:
        mapping_end = template_content.find('};', mapping_start) + 2
        before = template_content[:mapping_start]
        after = template_content[mapping_end:]
        template_content = before + f"let columnMapping = {json.dumps(column_mapping, indent=12)};" + column_mapping_js + after
    
    # Replace the hardcoded renderProjects function to use dynamic cell generation
    render_start = template_content.find('projects.forEach(project => {')
    if render_start != -1:
        render_end = template_content.find('tbody.appendChild(row);', render_start) + len('tbody.appendChild(row);')
        before = template_content[:render_start]
        after = template_content[render_end:]
        
        dynamic_render = '''projects.forEach(project => {
                const row = document.createElement('tr');
                
                // Create cells dynamically based on schema
                Object.keys(dynamicColumnMapping).forEach(fieldPath => {
                    const cell = createDynamicCell(project, fieldPath);
                    row.appendChild(cell);
                });
                
                tbody.appendChild(row);'''
        
        template_content = before + dynamic_render + after
    
    # Option to embed JSON data directly to avoid CORS issues
    # Read the JSON data
    json_file = OUTPUT_FILE.replace('.html', '_projects.json')
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = f.read()
        
        # Embed JSON data directly in HTML
        embed_js = f'''
    <script>
        // Embedded project data to avoid CORS issues
        const embeddedProjects = {json_data};
        
        // Override the loadProjectsFromJSON function to use embedded data
        async function loadProjectsFromJSON() {{
            try {{
                console.log('Using embedded project data...');
                projects = embeddedProjects;
                console.log('Total projects loaded:', projects.length);
                
                // Initialize UI
                initializeFilterOptions();
                renderProjects();
                updateProjectCount();
                
                console.log('Projects loaded successfully');
            }} catch (error) {{
                console.error('Error loading projects:', error);
                document.getElementById('table-body').innerHTML = '<tr><td colspan="5">Error loading projects. Please check console.</td></tr>';
            }}
        }}
    </script>'''
        
        # Insert before closing body tag
        template_content = template_content.replace('</body>', embed_js + '\n</body>')
    
    return template_content

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