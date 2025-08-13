import pandas as pd
import numpy as np
import os

def generate_promotions_dataset(num_rows=10000, output_format='excel', output_file=None):
    """
    Generate a synthetic promotions dataset
    
    Args:
        num_rows (int): Number of rows to generate
        output_format (str): Output format ('excel', 'csv', 'json', 'parquet')
        output_file (str): Output filename (optional, will auto-generate if not provided)
    
    Returns:
        pd.DataFrame: Generated dataset
    """
    print(f"Generating {num_rows} rows of promotions data...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # SKU and descriptions
    skus = [f"SKU{100000 + i}" for i in range(num_rows)]
    sku_descriptions = [f"Product Description {i}" for i in range(num_rows)]
    
    # Promo types
    promo_types = [
        "weekly a flyer",
        "vendor flyer", 
        "weekly b flyer",
        "temporary price reduction",
        "cm promo"
    ]
    
    # Generate data
    data = {
        "sku": skus,
        "sku_description": sku_descriptions,
        "promo_type": np.random.choice(promo_types, size=num_rows),
    }
    
    # Regular retail between $2 and $100
    data["regular_retail"] = np.round(np.random.uniform(2, 100, size=num_rows), 2)
    
    # Promo retail is 5% to 40% off regular retail
    discount_percents = np.random.uniform(5, 40, size=num_rows)
    data["discount_percent"] = np.round(discount_percents, 2)
    data["promo_retail"] = np.round(data["regular_retail"] * (1 - discount_percents / 100), 2)
    
    # Margin lift (random between 0.5% and 10.0%)
    data["margin_lift"] = np.round(np.random.uniform(0.5, 10, size=num_rows), 2)
    
    # Sales lift (random between 5% and 250%)
    data["sales_lift"] = np.round(np.random.uniform(5, 250, size=num_rows), 2)
    
    # Volume lift (random between 2% and 200%)
    data["volume_lift"] = np.round(np.random.uniform(2, 200, size=num_rows), 2)
    
    # Sales revenue (simulate as promo_retail * random units sold 50-500)
    units_sold = np.random.randint(50, 500, size=num_rows)
    data["sales_revenue"] = np.round(data["promo_retail"] * units_sold, 2)
    
    # Margin dollars (promo_retail minus cost, cost is 60%-90% of promo_retail)
    costs = data["promo_retail"] * np.random.uniform(0.6, 0.9, size=num_rows)
    data["margin_dollars"] = np.round(data["sales_revenue"] - (costs * units_sold), 2)
    
    # Margin rate (margin dollars divided by sales revenue)
    data["margin_rate"] = np.round(data["margin_dollars"] / data["sales_revenue"] * 100, 2)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate output filename if not provided
    if output_file is None:
        if output_format == 'excel':
            output_file = "promotions_dataset.xlsx"
        elif output_format == 'csv':
            output_file = "promotions_dataset.csv"
        elif output_format == 'json':
            output_file = "promotions_dataset.json"
        elif output_format == 'parquet':
            output_file = "promotions_dataset.parquet"
    
    # Save the dataset
    print(f"Saving dataset to {output_file}...")
    if output_format == 'excel':
        df.to_excel(output_file, index=False)
    elif output_format == 'csv':
        df.to_csv(output_file, index=False)
    elif output_format == 'json':
        df.to_json(output_file, orient='records', indent=2)
    elif output_format == 'parquet':
        df.to_parquet(output_file, index=False)
    
    print(f"Dataset generated successfully! Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows preview:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    # Generate dataset in multiple formats
    df = generate_promotions_dataset(num_rows=10000, output_format='excel')
    
    # Also generate CSV version
    generate_promotions_dataset(num_rows=10000, output_format='csv')