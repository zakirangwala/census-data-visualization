import pandas as pd
import numpy as np
from pathlib import Path


def clean_census_data(input_file: Path, output_file: Path) -> pd.DataFrame:
    """
    Clean and process the census data CSV file.

    Args:
        input_file (Path): Path to the raw census data CSV
        output_file (Path): Path to save the processed data

    Returns:
        pd.DataFrame: Processed census data
    """
    # Skip the metadata headers and read the CSV
    df = pd.read_csv(input_file, skiprows=7)

    # Drop empty columns and rows
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)

    # Clean column names
    df.columns = ['occupation', 'total', 'men', 'women']

    # Remove footnote references from values
    df['occupation'] = df['occupation'].str.replace(
        r'\s*i\d+\s*$', '', regex=True)
    df['occupation'] = df['occupation'].str.replace(
        r'\s*\d+\s*$', '', regex=True)

    # Convert numeric columns to float, replacing any non-numeric values with NaN
    for col in ['total', 'men', 'women']:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')

    # Create a column for occupation level (based on indentation/hierarchy)
    df['level'] = df['occupation'].str.count(r'^\s*').fillna(0)
    df['occupation'] = df['occupation'].str.strip()

    # Extract essential services data
    essential_services = {
        'Nurses': '31301 Registered nurses and registered psychiatric nurses',
        'Police Officers': '42100 Police officers (except commissioned)',
        'Firefighters': '42101 Firefighters'
    }

    essential_df = df[df['occupation'].isin(
        essential_services.values())].copy()
    essential_df['service_type'] = essential_df['occupation'].map(
        {v: k for k, v in essential_services.items()})

    # Calculate percentages for essential services
    essential_df['men_pct'] = (
        essential_df['men'] / essential_df['total'] * 100).round(1)
    essential_df['women_pct'] = (
        essential_df['women'] / essential_df['total'] * 100).round(1)

    # Sort by total number of workers
    essential_df = essential_df.sort_values('total', ascending=True)

    # Extract engineering data
    engineering_occupations = {
        'Computer': '21311 Computer engineers (except software engineers and designers)',
        'Mechanical': '21301 Mechanical engineers',
        'Electrical': '21310 Electrical and electronics engineers'
    }

    engineering_df = df[df['occupation'].isin(
        engineering_occupations.values())].copy()
    engineering_df['engineering_type'] = engineering_df['occupation'].map(
        {v: k for k, v in engineering_occupations.items()})

    # Extract high-level NOC categories for gender analysis
    noc_categories = df[df['occupation'].str.match(r'^\d\s[A-Z].*')].copy()

    # Save processed dataframes
    processed_data = {
        'full_data': df,
        'essential_services': essential_df,
        'engineering': engineering_df,
        'noc_categories': noc_categories
    }

    # Save to processed directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(processed_data, output_file)

    return processed_data


if __name__ == "__main__":
    # Define paths
    data_dir = Path(__file__).parent / "data"
    input_file = data_dir / "raw" / "census-data.csv"
    output_file = data_dir / "processed" / "processed_data.pkl"

    # Process the data
    processed_data = clean_census_data(input_file, output_file)
    print("Data processing completed successfully!")

    # Print some basic statistics
    print("\nDataset statistics:")
    for name, df in processed_data.items():
        print(f"\n{name}:")
        print(f"Shape: {df.shape}")
        if 'total' in df.columns:
            print(f"Total workers: {df['total'].sum():,.0f}")
