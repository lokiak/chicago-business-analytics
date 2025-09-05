# Chicago SMB Market Radar

<div class="hero-section">
  <h1>🏙️ Chicago SMB Market Radar</h1>
  <p>Business intelligence platform providing real-time visibility into Chicago's small business activity through automated data collection, analysis, and reporting.</p>
</div>

## 🚀 Quick Start

Get up and running with Chicago's business data in minutes:

```bash
# Clone and set up the project
git clone your-repo-url
cd chicago-smb-market-radar

# Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run your first analysis
make run

# Start exploring!
make docs-serve
```

[Get Started →](getting-started/README.md){ .md-button .md-button--primary }
[View Framework →](framework/README.md){ .md-button }

## 🎯 Key Features

<div class="grid cards" markdown>

-   :rocket: **Automated Data Pipeline**

    ---

    Daily data collection from Chicago Open Data Portal with robust error handling and retry logic

-   :chart_with_upwards_trend: **Business Intelligence**

    ---

    KPI calculations, trend analysis, and real-time insights for economic development decision-making

-   :jupyter: **Interactive Analysis**

    ---

    Jupyter notebooks for exploratory data analysis with reusable utility functions

-   :gear: **Great Expectations Integration**

    ---

    Advanced data quality framework with 60+ validation rules and automated cleaning

</div>

## 📊 Project Progress

Track our journey through the **BI 0→1 Framework** implementation:

<div class="progress-item">
  <strong>Step 1: Scope & Strategy</strong>
  <span class="status-badge status-completed">Completed</span>
</div>
<div class="progress-item">
  <strong>Step 2: Data Ingestion</strong>
  <span class="status-badge status-completed">Completed</span>
</div>
<div class="progress-item">
  <strong>Step 3: Transform & Model</strong>
  <span class="status-badge status-partial">In Progress</span>
</div>
<div class="progress-item">
  <strong>Step 4: Load & Validate</strong>
  <span class="status-badge status-pending">Pending</span>
</div>
<div class="progress-item">
  <strong>Step 5: Visualize & Report</strong>
  <span class="status-badge status-pending">Pending</span>
</div>
<div class="progress-item">
  <strong>Step 6: Automate & Scale</strong>
  <span class="status-badge status-pending">Pending</span>
</div>

<div class="progress-indicator">
  <span class="progress-text">Overall Progress: </span>
  <span class="progress-value">42% Complete</span>
</div>

## 📈 Latest Updates

!!! success "Great Expectations Integration"
    
    Added comprehensive data cleaning framework with pattern-based field detection and 60+ validation rules.
    
    [:octicons-arrow-right-24: Learn More](guides/great-expectations.md)

!!! info "Documentation Restructure"
    
    Completely reorganized documentation with modern MkDocs Material theme and improved user experience.
    
    You're experiencing it right now!

## 🏙️ Chicago Data Sources

- **Business Licenses** (r5kz-chrr): 50+ license types across all business sectors
- **Building Permits** (ydr8-5enu): Construction and renovation activity indicators  
- **CTA Ridership** (6iiy-9s97): Public transit as economic activity proxy

### Geographic Coverage
- **77 Community Areas**: Complete coverage of Chicago neighborhoods
- **50 Wards**: Political boundary analysis for policy insights
- **Downtown Focus**: Special attention to Loop and Near North business activity

## 🛠️ Technology Stack

**Core Framework**
- Python, pandas, Great Expectations, Jupyter

**Data Infrastructure** 
- Socrata API, Google Sheets, GitHub Actions, Markdown

**Quality & Reliability**
- Automated testing, fallback systems, comprehensive monitoring

## 🎯 Use Cases

**For Economic Development Professionals**
- Real-time business activity monitoring
- Neighborhood-level trend analysis
- Policy impact assessment

**For City Planners**
- Construction and development patterns
- Geographic business distribution
- Economic health indicators

**For Business Community**
- Market intelligence and opportunity identification
- Competition and trend analysis
- Location-based business insights

## 📚 Documentation Overview

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/README.md) | Setup, installation, and first analysis |
| [How-to Guides](guides/README.md) | Step-by-step task-oriented tutorials |
| [BI Framework](framework/README.md) | Strategic planning and architecture |
| [Technical Reference](technical/README.md) | API documentation and system details |
| [Reports & Analysis](reports/README.md) | Generated insights and analysis notebooks |

---

**Ready to dive in?** Start with our [Getting Started guide](getting-started/README.md) or explore the [BI Framework](framework/README.md) to understand our strategic approach.