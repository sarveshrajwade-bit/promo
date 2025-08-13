import pandas as pd
import numpy as np

# Parameters
num_rows = 10000
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

# Save to Excel
df.to_excel("promotions_dataset.xlsx", index=False)
