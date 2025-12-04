"""
Data loading and utility functions for Private Laws Dashboard
"""

import pandas as pd
import numpy as np
from config import SUBJECT_CATEGORIES, RELIEF_CATEGORIES


def load_data_from_csv(filepath):
    """Load private laws data from CSV file with robust date handling."""
    df = pd.read_csv(filepath)
    
    if 'id' not in df.columns:
        df['id'] = range(1, len(df) + 1)
    
    if 'date' in df.columns:
        for fmt in ['%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
            try:
                df['date'] = pd.to_datetime(df['date'], format=fmt)
                print(f"✓ Parsed dates with format: {fmt}")
                break
            except (ValueError, TypeError):
                continue
        else:
            try:
                df['date'] = pd.to_datetime(df['date'])
                print("✓ Parsed dates using pandas auto-detection")
            except Exception as e:
                print(f"⚠ Could not parse dates: {e}")
    
    if 'year' not in df.columns and 'date' in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df['date']):
            df['year'] = df['date'].dt.year
        else:
            df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
    
    df['year'] = df['year'].astype(int)
    
    if 'subject_category' in df.columns:
        df['subject_category'] = df['subject_category'].fillna('')
    
    if 'relief_category' in df.columns:
        df['relief_category'] = df['relief_category'].fillna('')
    
    for col in ['summary', 'pdf_link', 'details_link']:
        if col not in df.columns:
            df[col] = ''
    
    print(f"✓ Loaded {len(df):,} records")
    print(f"✓ Year range: {df['year'].min()} - {df['year'].max()}")
    
    return df


def generate_sample_data(n_records=5000):
    """Generate sample data for testing."""
    np.random.seed(42)
    
    years = []
    for _ in range(n_records):
        period = np.random.choice(['early', 'mid', 'peak', 'modern'], p=[0.1, 0.2, 0.5, 0.2])
        if period == 'early':
            years.append(np.random.randint(1789, 1860))
        elif period == 'mid':
            years.append(np.random.randint(1860, 1920))
        elif period == 'peak':
            years.append(np.random.randint(1920, 1970))
        else:
            years.append(np.random.randint(1970, 2025))
    
    years = np.array(years)
    congress_numbers = ((years - 1789) // 2) + 1
    
    subjects = []
    for _ in range(n_records):
        n_cats = np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05])
        cats = np.random.choice(SUBJECT_CATEGORIES, n_cats, replace=False)
        subjects.append(", ".join(cats))
    
    data = {
        'id': range(1, n_records + 1),
        'congress': congress_numbers,
        'volume': np.random.randint(1, 150, n_records),
        'chapter': np.random.randint(1, 500, n_records),
        'title': [f"An Act for the Relief of {np.random.choice(['John', 'Mary', 'James', 'Elizabeth', 'William', 'Sarah'])} {np.random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])}" for _ in range(n_records)],
        'date': pd.to_datetime([f"{y}-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}" for y in years]),
        'year': years,
        'subject_category': subjects,
        'relief_category': [''] * n_records,
        'summary': ["This private law provides relief to the named individual(s)." for _ in range(n_records)],
        'pdf_link': [f"https://www.govinfo.gov/content/pkg/STATUTE-{v}/pdf/STATUTE-{v}-Pg{c}.pdf" for v, c in zip(np.random.randint(1, 120, n_records), np.random.randint(1, 1000, n_records))],
        'details_link': [f"https://www.congress.gov/bill/{c}th-congress/private-law/{np.random.randint(1, 500)}" for c in congress_numbers]
    }
    
    return pd.DataFrame(data).sort_values('date').reset_index(drop=True)


def get_ordinal_suffix(n):
    """Return ordinal suffix for a number (1st, 2nd, 3rd, etc.)"""
    if 11 <= (n % 100) <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')


def truncate_label(text, max_length=25):
    """Truncate text to max length with ellipsis."""
    if len(str(text)) > max_length:
        return str(text)[:max_length-3] + "..."
    return str(text)


def count_categories(df, category_column, valid_categories):
    """Count category assignments from a column that may contain multiple categories."""
    counts = {cat: 0 for cat in valid_categories}
    sorted_categories = sorted(valid_categories, key=len, reverse=True)
    
    for value in df[category_column]:
        if pd.isna(value) or value == '':
            continue
        
        value_str = str(value).strip()
        
        for cat in sorted_categories:
            if cat in value_str:
                counts[cat] += 1
                value_str = value_str.replace(cat, '', 1)
    
    return counts
