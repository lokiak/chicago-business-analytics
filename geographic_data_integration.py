#!/usr/bin/env python3
"""
Geographic Data Integration Script
Integrates Chicago's geographic datasets with business data for spatial analysis
"""

import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os

# Add src to path to import modules
sys.path.append(str(Path(__file__).parent / "src"))

from sheets import open_sheet, upsert_worksheet, overwrite_with_dataframe
from config import load_settings, load_datasets_yaml
from logging_setup import setup_logger

logger = setup_logger()

class GeographicDataIntegrator:
    """Integrates geographic data with business data for spatial analysis"""

    def __init__(self, domain="data.cityofchicago.org"):
        self.domain = domain
        self.community_areas = None
        self.census_data = None

    def fetch_community_areas(self):
        """Fetch Chicago community areas with geographic boundaries"""
        logger.info("Fetching Chicago Community Areas...")

        url = f"https://{self.domain}/resource/igwz-8jzy.json"

        try:
            # Get all community areas
            r = requests.get(url, params={"$limit": 1000}, timeout=60)

            if r.status_code == 200:
                data = r.json()
                logger.info(f"Successfully fetched {len(data)} community areas")

                # Convert to DataFrame
                df = pd.DataFrame(data)

                # Clean up the data
                df['area_numbe'] = pd.to_numeric(df['area_numbe'], errors='coerce')
                df['shape_area'] = pd.to_numeric(df['shape_area'], errors='coerce')
                df['shape_len'] = pd.to_numeric(df['shape_len'], errors='coerce')

                # Extract coordinates from geometry for easier analysis
                df['has_geometry'] = df['the_geom'].apply(lambda x: isinstance(x, dict) and 'coordinates' in x)

                # Create a simplified version for analysis
                df_clean = df[['area_numbe', 'community', 'shape_area', 'shape_len', 'has_geometry']].copy()
                df_clean = df_clean.sort_values('area_numbe')

                self.community_areas = df_clean
                return df_clean

            else:
                logger.error(f"Failed to fetch community areas: {r.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching community areas: {e}")
            return None

    def fetch_census_data(self):
        """Fetch Chicago census block group data with demographic information"""
        logger.info("Fetching Chicago Census Data...")

        url = f"https://{self.domain}/resource/kn9c-c2s2.json"

        try:
            # Get all census data
            r = requests.get(url, params={"$limit": 1000}, timeout=60)

            if r.status_code == 200:
                data = r.json()
                logger.info(f"Successfully fetched {len(data)} census records")

                # Convert to DataFrame
                df = pd.DataFrame(data)

                # Clean up numeric fields
                numeric_fields = [
                    'ca', 'percent_of_housing_crowded', 'percent_households_below_poverty',
                    'percent_aged_16_unemployed', 'percent_aged_25_without_high_school_diploma',
                    'percent_aged_under_18_or_over_64', 'per_capita_income_', 'hardship_index'
                ]

                for field in numeric_fields:
                    if field in df.columns:
                        df[field] = pd.to_numeric(df[field], errors='coerce')

                # Group by community area to get averages
                census_summary = df.groupby('community_area_name').agg({
                    'percent_of_housing_crowded': 'mean',
                    'percent_households_below_poverty': 'mean',
                    'percent_aged_16_unemployed': 'mean',
                    'percent_aged_25_without_high_school_diploma': 'mean',
                    'percent_aged_under_18_or_over_64': 'mean',
                    'per_capita_income_': 'mean',
                    'hardship_index': 'mean'
                }).reset_index()

                self.census_data = census_summary
                return census_summary

            else:
                logger.error(f"Failed to fetch census data: {r.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching census data: {e}")
            return None

    def create_geographic_lookup_table(self):
        """Create a comprehensive geographic lookup table"""
        logger.info("Creating geographic lookup table...")

        if self.community_areas is None or self.census_data is None:
            logger.error("Must fetch community areas and census data first")
            return None

        # Merge community areas with census data
        lookup_table = pd.merge(
            self.community_areas,
            self.census_data,
            left_on='community',
            right_on='community_area_name',
            how='left'
        )

        # Clean up the merged data
        lookup_table = lookup_table.drop('community_area_name', axis=1)

        # Add additional geographic information
        lookup_table['area_sq_miles'] = lookup_table['shape_area'] / 2589988.11  # Convert sq meters to sq miles
        lookup_table['perimeter_miles'] = lookup_table['shape_len'] / 1609.34  # Convert meters to miles

        # Add geographic region classification
        lookup_table['geographic_region'] = lookup_table['community'].apply(self._classify_geographic_region)

        # Add economic classification
        lookup_table['economic_classification'] = lookup_table['per_capita_income_'].apply(self._classify_economic_status)

        logger.info(f"Created lookup table with {len(lookup_table)} community areas")
        return lookup_table

    def _classify_geographic_region(self, community_name):
        """Classify community areas into geographic regions"""
        community_lower = community_name.upper()

        # North Side
        if any(term in community_lower for term in ['ROGERS PARK', 'WEST RIDGE', 'UPTOWN', 'LINCOLN SQUARE', 'NORTH CENTER', 'LAKE VIEW', 'LINCOLN PARK', 'NEAR NORTH SIDE', 'EDISON PARK', 'NORWOOD PARK', 'JEFFERSON PARK', 'FOREST GLEN', 'NORTH PARK', 'ALBANY PARK', 'PORTAGE PARK', 'IRVING PARK', 'DUNNING', 'MONTCLARE', 'BELMONT CRAGIN', 'HERMOSA', 'AVONDALE', 'LOGAN SQUARE', 'HUMBOLDT PARK', 'WEST TOWN', 'AUSTIN']):
            return 'North Side'
        # South Side
        elif any(term in community_lower for term in ['ARMOUR SQUARE', 'DOUGLAS', 'OAKLAND', 'FULLER PARK', 'GRAND BOULEVARD', 'KENWOOD', 'WASHINGTON PARK', 'HYDE PARK', 'WOODLAWN', 'SOUTH SHORE', 'CHATHAM', 'AVALON PARK', 'SOUTH CHICAGO', 'BURNSIDE', 'CALUMET HEIGHTS', 'ROSELAND', 'PULLMAN', 'SOUTH DEERING', 'EAST SIDE', 'WEST PULLMAN', 'RIVERDALE', 'HEGEWISCH', 'GARFIELD RIDGE', 'ARCHER HEIGHTS', 'BRIGHTON PARK', 'MCKINLEY PARK', 'BRIDGEPORT', 'NEW CITY', 'WEST ELSDON', 'GAGE PARK', 'CLEARING', 'WEST LAWN', 'CHICAGO LAWN', 'WEST ENGLEWOOD', 'ENGLEWOOD', 'GREATER GRAND CROSSING', 'ASHBURN', 'AUBURN GRESHAM', 'BEVERLY', 'WASHINGTON HEIGHTS', 'MOUNT GREENWOOD', 'MORGAN PARK', 'OAKDALE', 'CREMORNE', 'WEST MORGAN PARK']):
            return 'South Side'
        # West Side
        elif any(term in community_lower for term in ['NEAR WEST SIDE', 'GARFIELD PARK', 'EAST GARFIELD PARK', 'WEST GARFIELD PARK', 'NORTH LAWNDALE', 'SOUTH LAWNDALE', 'LOWER WEST SIDE', 'LOOP', 'NEAR SOUTH SIDE']):
            return 'West Side'
        # Central
        else:
            return 'Central'

    def _classify_economic_status(self, per_capita_income):
        """Classify economic status based on per capita income"""
        if pd.isna(per_capita_income):
            return 'Unknown'
        elif per_capita_income < 20000:
            return 'Low Income'
        elif per_capita_income < 35000:
            return 'Lower Middle Income'
        elif per_capita_income < 50000:
            return 'Middle Income'
        elif per_capita_income < 75000:
            return 'Upper Middle Income'
        else:
            return 'High Income'

    def create_business_geographic_analysis(self, business_df, community_field='community_area'):
        """Analyze business data with geographic context"""
        logger.info("Creating business geographic analysis...")

        if self.community_areas is None:
            logger.error("Must fetch community areas first")
            return None

        # Ensure business_df has the community field
        if community_field not in business_df.columns:
            logger.error(f"Business data missing required field: {community_field}")
            return None

        # Create analysis by community area
        business_analysis = business_df.groupby(community_field).agg({
            'id': 'count',  # Count of businesses
        }).reset_index()

        business_analysis = business_analysis.rename(columns={'id': 'business_count'})

        # Merge with geographic lookup table
        geographic_analysis = pd.merge(
            business_analysis,
            self.community_areas,
            left_on=community_field,
            right_on='community',
            how='left'
        )

        # Add census data if available
        if self.census_data is not None:
            geographic_analysis = pd.merge(
                geographic_analysis,
                self.census_data,
                left_on='community',
                right_on='community_area_name',
                how='left'
            )

        logger.info(f"Created geographic analysis for {len(geographic_analysis)} community areas")
        return geographic_analysis

    def export_to_google_sheets(self, settings):
        """Export all geographic data to Google Sheets"""
        logger.info("Exporting geographic data to Google Sheets...")

        try:
            # Open Google Sheet
            sh = open_sheet(settings.sheet_id, settings.google_creds_path)

            # Export community areas
            if self.community_areas is not None:
                logger.info("Exporting community areas...")
                community_ws = upsert_worksheet(sh, "Community_Areas", rows=len(self.community_areas) + 100, cols=20)
                overwrite_with_dataframe(community_ws, self.community_areas)

            # Export census data
            if self.census_data is not None:
                logger.info("Exporting census data...")
                census_ws = upsert_worksheet(sh, "Census_Data", rows=len(self.census_data) + 100, cols=20)
                overwrite_with_dataframe(census_ws, self.census_data)

            # Export geographic lookup table
            lookup_table = self.create_geographic_lookup_table()
            if lookup_table is not None:
                logger.info("Exporting geographic lookup table...")
                lookup_ws = upsert_worksheet(sh, "Geographic_Lookup", rows=len(lookup_table) + 100, cols=30)
                overwrite_with_dataframe(lookup_ws, lookup_table)

            logger.info("Successfully exported all geographic data to Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {e}")
            return False

def main():
    """Main function to integrate geographic data"""

    logger.info("Starting geographic data integration...")

    try:
        # Load configuration
        settings = load_settings()

        # Initialize integrator
        integrator = GeographicDataIntegrator()

        # Fetch geographic data
        community_areas = integrator.fetch_community_areas()
        if community_areas is None:
            logger.error("Failed to fetch community areas")
            return False

        census_data = integrator.fetch_census_data()
        if census_data is None:
            logger.warning("Failed to fetch census data, continuing without demographic information")

        # Create comprehensive lookup table
        lookup_table = integrator.create_geographic_lookup_table()
        if lookup_table is None:
            logger.error("Failed to create geographic lookup table")
            return False

        # Export to Google Sheets
        success = integrator.export_to_google_sheets(settings)

        if success:
            logger.info("Geographic data integration completed successfully!")
            logger.info("Available sheets:")
            logger.info("  - Community_Areas: Basic community area information")
            logger.info("  - Census_Data: Demographic and economic data")
            logger.info("  - Geographic_Lookup: Comprehensive geographic reference table")

            # Show summary statistics
            logger.info(f"\nSummary Statistics:")
            logger.info(f"  Total Community Areas: {len(community_areas)}")
            logger.info(f"  Areas with Geometry: {community_areas['has_geometry'].sum()}")
            logger.info(f"  Total Area (sq miles): {community_areas['shape_area'].sum() / 2589988.11:.1f}")

            if census_data is not None:
                logger.info(f"  Census Records: {len(census_data)}")
                logger.info(f"  Average Per Capita Income: ${census_data['per_capita_income_'].mean():,.0f}")
                logger.info(f"  Average Hardship Index: {census_data['hardship_index'].mean():.1f}")

            return True
        else:
            logger.error("Failed to export to Google Sheets")
            return False

    except Exception as e:
        logger.error(f"Error in geographic data integration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Geographic data integration completed successfully!")
    else:
        print("Geographic data integration failed. Check logs for details.")
        sys.exit(1)
