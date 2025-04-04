# Census Data Interactive Dashboard

This project creates an interactive dashboard using 2023 Census data from Statistics Canada to visualize and analyze various employment statistics across provinces and territories.


![image](https://github.com/user-attachments/assets/83516111-a284-4ca1-a11c-c44e720828c0)

## PRODUCTION URL : https://web-production-7f38.up.railway.app/

## Data Source

The data is sourced from Statistics Canada's 2023 Census:
https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810040401

## Project Structure

```
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── src/                    # Source code directory
│   ├── app.py             # Main Dash application
│   ├── data_processor.py  # Data processing functions
│   └── data/              # Data directory
│       ├── raw/           # Raw downloaded data
│       └── processed/     # Processed datasets
```

## Setup and Installation

1. Create and activate virtual environment:

```bash
python -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

1. Activate the virtual environment (if not already activated):

```bash
source env/bin/activate
```

2. Run the dashboard:

```bash
python src/app.py
```

3. Open your browser and navigate to `http://localhost:8050`

## Features

The dashboard includes interactive visualizations for:

- Distribution of essential services (nurses, police, firefighters) across provinces/territories
- Employment statistics by gender across different NOC groups
- Engineering manpower analysis
- Additional insights and trends

## Interactive Components

- Dropdown menus for province/territory selection
- Radio buttons for filtering service types
- Sliders for adjusting thresholds
- Checkboxes for data filtering
