# Chicago Geographic Data Integration Guide

## Overview

This guide explains the geographic datasets available in Chicago's Socrata portal and how they can be integrated with your business data for comprehensive spatial analysis.

## Available Geographic Datasets

### 1. Community Areas (Dataset ID: `igwz-8jzy`)
**What it provides:**
- **77 community areas** covering all of Chicago
- **Geographic boundaries** with precise coordinates (MultiPolygon geometry)
- **Area measurements** in square meters and perimeter in meters
- **Community names** and area numbers for easy identification

**Key fields:**
- `area_numbe`: Unique numeric identifier for each community area
- `community`: Human-readable community area name
- `the_geom`: Geographic boundary coordinates (GeoJSON format)
- `shape_area`: Area in square meters
- `shape_len`: Perimeter in meters

**Use cases:**
- Geographic boundary mapping
- Spatial joins with business data
- Community area identification
- Area and perimeter calculations

### 2. Census Block Groups (Dataset ID: `kn9c-c2s2`)
**What it provides:**
- **Demographic and economic data** for each community area
- **Socioeconomic indicators** for business analysis
- **Population characteristics** for market research

**Key fields:**
- `community_area_name`: Community area name
- `percent_of_housing_crowded`: Housing density indicator
- `percent_households_below_poverty`: Poverty rate
- `percent_aged_16_unemployed`: Unemployment rate
- `percent_aged_25_without_high_school_diploma`: Education level
- `percent_aged_under_18_or_over_64`: Age distribution
- `per_capita_income_`: Economic indicator
- `hardship_index`: Composite socioeconomic score

**Use cases:**
- Market analysis and targeting
- Business location planning
- Demographic profiling
- Economic opportunity assessment

## Data Integration Results

### Summary Statistics
- **Total Community Areas**: 77
- **Areas with Geometry**: 77 (100% coverage)
- **Total Area**: 2,485.8 square miles
- **Census Records**: 78
- **Average Per Capita Income**: $25,597
- **Average Hardship Index**: 49.5

### Geographic Classifications
The system automatically classifies community areas into four regions:

1. **North Side**: Rogers Park, West Ridge, Uptown, Lincoln Square, North Center, Lake View, Lincoln Park, Near North Side, Edison Park, Norwood Park, Jefferson Park, Forest Glen, North Park, Albany Park, Portage Park, Irving Park, Dunning, Montclare, Belmont Cragin, Hermosa, Avondale, Logan Square, Humboldt Park, West Town, Austin

2. **South Side**: Armour Square, Douglas, Oakland, Fuller Park, Grand Boulevard, Kenwood, Washington Park, Hyde Park, Woodlawn, South Shore, Chatham, Avalon Park, South Chicago, Burnside, Calumet Heights, Roseland, Pullman, South Deering, East Side, West Pullman, Riverdale, Hegewisch, Garfield Ridge, Archer Heights, Brighton Park, McKinley Park, Bridgeport, New City, West Elsdon, Gage Park, Clearing, West Lawn, Chicago Lawn, West Englewood, Englewood, Greater Grand Crossing, Ashburn, Auburn Gresham, Beverly, Washington Heights, Mount Greenwood, Morgan Park, Oakdale, Cremorne, West Morgan Park

3. **West Side**: Near West Side, Garfield Park, East Garfield Park, West Garfield Park, North Lawndale, South Lawndale, Lower West Side, Loop, Near South Side

4. **Central**: Remaining areas not classified above

### Economic Classifications
Based on per capita income:
- **Low Income**: < $20,000
- **Lower Middle Income**: $20,000 - $34,999
- **Middle Income**: $35,000 - $49,999
- **Upper Middle Income**: $50,000 - $74,999
- **High Income**: $75,000+

## Google Sheets Integration

The geographic data has been exported to three sheets in your Google Sheets document:

### 1. Community_Areas
Basic community area information including:
- Area numbers and names
- Geographic measurements
- Geometry availability flags

### 2. Census_Data
Demographic and economic data including:
- Socioeconomic indicators
- Population characteristics
- Economic metrics

### 3. Geographic_Lookup
Comprehensive reference table combining:
- Community area information
- Census data
- Geographic classifications
- Economic classifications
- Calculated metrics (area in square miles, perimeter in miles)

## How to Use for Business Analysis

### 1. Business Location Analysis
```python
# Example: Analyze business density by community area
business_analysis = integrator.create_business_geographic_analysis(
    business_df,
    community_field='community_area'
)
```

### 2. Market Research
- Use demographic data to identify target markets
- Analyze economic indicators for business opportunities
- Assess market saturation by geographic area

### 3. Geographic Segmentation
- Group businesses by geographic region (North, South, West, Central)
- Analyze performance differences across regions
- Identify expansion opportunities

### 4. Spatial Analysis
- Calculate business density per square mile
- Analyze proximity to transportation hubs
- Assess accessibility across different areas

## Technical Implementation

### Data Sources
- **Community Areas**: `https://data.cityofchicago.org/resource/igwz-8jzy.json`
- **Census Data**: `https://data.cityofchicago.org/resource/kn9c-c2s2.json`

### Data Processing
- Automatic geometry validation
- Numeric field cleaning and conversion
- Geographic region classification
- Economic status classification
- Unit conversions (meters to miles)

### Integration Capabilities
- Merge with existing business data
- Create geographic business analysis
- Export to Google Sheets
- Real-time data updates from Socrata

## Benefits for Your Business Analysis

1. **Complete Geographic Coverage**: All 77 Chicago community areas included
2. **Rich Demographic Data**: Socioeconomic indicators for market analysis
3. **Spatial Boundaries**: Precise geographic boundaries for mapping
4. **Economic Classification**: Automatic categorization of economic status
5. **Easy Integration**: Seamless integration with existing business data
6. **Google Sheets Export**: Accessible data format for analysis and reporting

## Next Steps

1. **Review the exported data** in your Google Sheets
2. **Integrate with business data** using the provided functions
3. **Create geographic visualizations** using the boundary data
4. **Analyze market opportunities** using demographic indicators
5. **Plan business expansion** based on geographic insights

## Support and Maintenance

- **Data Updates**: Census data is updated periodically by the City of Chicago
- **API Reliability**: Socrata provides reliable access to official city data
- **Error Handling**: Comprehensive logging and error handling included
- **Scalability**: Can handle large datasets and multiple data sources

This geographic data integration provides you with a comprehensive foundation for spatial business analysis in Chicago, enabling data-driven decisions based on location, demographics, and economic factors.
