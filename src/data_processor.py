# --------------------------------------------------
# Assignment: Project
# File:    data_processor.py
# Author:  Zaki Rangwala (210546860)
# Version: 2025-04-04
# --------------------------------------------------

# import libraries
import pandas as pd
import numpy as np
from pathlib import Path


# load province and population data
def load_province_data(file_path: Path) -> pd.DataFrame:
    return pd.read_csv(file_path)


# clean census data (takes in raw census data and province data and returns processed data)
def clean_census_data(input_file: Path, province_file: Path, output_file: Path) -> dict:
    # load province data and skip metadata headers
    province_data = load_province_data(province_file)
    df = pd.read_csv(input_file, skiprows=7)

    # drop empty columns and rows and clean column names
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    df.columns = ['occupation', 'total', 'men', 'women']

    # remove footnote references from values
    df['occupation'] = df['occupation'].str.replace(
        r'\s*i\d+\s*$', '', regex=True)
    df['occupation'] = df['occupation'].str.replace(
        r'\s*\d+\s*$', '', regex=True)

    # convert numeric columns to float, replacing any non-numeric values with NaN
    for col in ['total', 'men', 'women']:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')

    # create a column for occupation level (based on indentation/hierarchy)
    df['level'] = df['occupation'].str.count(r'^\s*').fillna(0)
    df['occupation'] = df['occupation'].str.strip()

    # TODO: create provincial data frames
    provinces = province_data['province_code'].tolist()

    # mock provincial data frames
    provincial_dfs = []
    for _, row in province_data.iterrows():
        province_df = df.copy()
        pop_ratio = row['population'] / province_data['population'].sum()

        # adjust numbers based on population ratio with some random variation
        for col in ['total', 'men', 'women']:
            province_df[col] = (province_df[col] * pop_ratio *
                                np.random.uniform(0.8, 1.2)).round()

        province_df['province'] = row['province_code']
        province_df['province_name'] = row['province_name']
        province_df['population'] = row['population']

        # calculate per capita values (per 100,000 population)
        province_df['per_capita'] = (
            province_df['total'] / row['population'] * 100000).round(2)
        province_df['men_per_capita'] = (
            province_df['men'] / row['population'] * 100000).round(2)
        province_df['women_per_capita'] = (
            province_df['women'] / row['population'] * 100000).round(2)

        provincial_dfs.append(province_df)

    # combine all provincial data
    combined_df = pd.concat(provincial_dfs, ignore_index=True)

    # extract essential services data
    essential_services = {
        'Nurses': '31301 Registered nurses and registered psychiatric nurses',
        'Police Officers': '42100 Police officers (except commissioned)',
        'Firefighters': '42101 Firefighters'
    }

    essential_df = combined_df[combined_df['occupation'].isin(
        essential_services.values())].copy()
    essential_df['service_type'] = essential_df['occupation'].map(
        {v: k for k, v in essential_services.items()})

    # extract engineering data
    engineering_occupations = {
        'Computer': '21311 Computer engineers (except software engineers and designers)',
        'Mechanical': '21301 Mechanical engineers',
        'Electrical': '21310 Electrical and electronics engineers'
    }

    engineering_df = combined_df[combined_df['occupation'].isin(
        engineering_occupations.values())].copy()
    engineering_df['engineering_type'] = engineering_df['occupation'].map(
        {v: k for k, v in engineering_occupations.items()})

    # extract high-level NOC categories for gender analysis
    noc_categories = combined_df[combined_df['occupation'].str.match(
        r'^\d\s[A-Z].*')].copy()

    # process province data to ensure it's in the correct format
    province_data_processed = province_data.copy()
    province_data_processed['province'] = province_data_processed['province_code']

    # save processed dataframes
    processed_data = {
        'full_data': combined_df,
        'essential_services': essential_df,
        'engineering': engineering_df,
        'noc_categories': noc_categories,
        'province_data': province_data_processed
    }

    # save to processed directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(processed_data, output_file)

    return processed_data


if __name__ == "__main__":
    # define paths
    data_dir = Path(__file__).parent / "data"
    input_file = data_dir / "raw" / "census-data.csv"
    province_file = data_dir / "raw" / "province_population.csv"
    output_file = data_dir / "processed" / "processed_data.pkl"

    # process the data
    processed_data = clean_census_data(input_file, province_file, output_file)
    print("Data processing completed successfully!")

    # print some basic statistics
    print("\nDataset statistics:")
    for name, df in processed_data.items():
        print(f"\n{name}:")
        print(f"Shape: {df.shape}")
        if 'total' in df.columns:
            print(f"Total workers: {df['total'].sum():,.0f}")
