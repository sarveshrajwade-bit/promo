# Dataset Upload System

A comprehensive Python-based dataset upload and management system with support for multiple file formats, data validation, and analysis capabilities.

## 🚀 Features

- **Multiple Format Support**: CSV, Excel (.xlsx/.xls), JSON, Parquet, Feather, and Pickle files
- **Automatic Data Validation**: Data type detection, missing value analysis, duplicate detection
- **Dataset Preview**: Comprehensive data summary with statistics and sample rows
- **Format Conversion**: Export datasets to different formats
- **Memory Efficient**: Optimized for large datasets
- **Command Line Interface**: Easy-to-use CLI for quick uploads
- **Python API**: Full programmatic access for integration

## 📦 Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **For system installations** (if using externally managed environments):
```bash
pip install --break-system-packages pandas numpy openpyxl
```

## 🎯 Quick Start

### Command Line Usage

Upload a dataset with automatic preview:
```bash
python3 dataset_uploader.py your_dataset.csv --name "My Dataset"
```

Upload without preview:
```bash
python3 dataset_uploader.py data.xlsx --name "Sales Data" --no-preview
```

### Python API Usage

```python
from dataset_uploader import DatasetUploader

# Initialize uploader
uploader = DatasetUploader(upload_directory="uploads")

# Upload dataset
dataset_id = uploader.upload_dataset('data.csv', dataset_name='Sales Data')

# List all datasets
uploader.list_datasets()

# Get dataset for analysis
df = uploader.get_dataset(dataset_id)

# Export to different format
uploader.export_dataset(dataset_id, 'output.json', 'json')
```

## 📊 Dataset Generation

Generate synthetic promotions datasets for testing:

```python
from generate_dataset import generate_promotions_dataset

# Generate 10,000 rows in Excel format
df = generate_promotions_dataset(num_rows=10000, output_format='excel')

# Generate CSV format
df = generate_promotions_dataset(num_rows=5000, output_format='csv', 
                                output_file='custom_name.csv')
```

## 🔧 Available Scripts

### 1. `generate_dataset.py`
Generates synthetic promotions datasets with the following columns:
- `sku`: Product SKU codes
- `sku_description`: Product descriptions  
- `promo_type`: Type of promotion (weekly flyer, vendor flyer, etc.)
- `regular_retail`: Original price
- `discount_percent`: Discount percentage
- `promo_retail`: Discounted price
- `margin_lift`: Margin improvement percentage
- `sales_lift`: Sales increase percentage
- `volume_lift`: Volume increase percentage
- `sales_revenue`: Total sales revenue
- `margin_dollars`: Margin in dollars
- `margin_rate`: Margin rate percentage

### 2. `dataset_uploader.py`
Comprehensive dataset upload utility with CLI and Python API.

**Command line options:**
- `file_path`: Path to the dataset file (required)
- `--name`: Custom name for the dataset
- `--no-preview`: Skip dataset preview
- `--upload-dir`: Custom upload directory

### 3. `demo_upload.py`
Complete demonstration of all features:
```bash
python3 demo_upload.py
```

## 📋 Supported File Formats

| Format | Extensions | Description |
|--------|------------|-------------|
| CSV | `.csv` | Comma-separated values |
| Excel | `.xlsx`, `.xls` | Microsoft Excel files |
| JSON | `.json` | JavaScript Object Notation |
| Parquet | `.parquet` | Columnar storage format |
| Feather | `.feather` | Fast binary columnar format |
| Pickle | `.pickle`, `.pkl` | Python binary format |

## 🔍 Data Validation Features

The system automatically validates and analyzes uploaded datasets:

- **Shape Analysis**: Row and column counts
- **Data Types**: Automatic type detection
- **Missing Values**: Count and percentage of missing data
- **Duplicate Detection**: Identifies duplicate rows
- **Memory Usage**: Calculates dataset memory footprint
- **Statistical Summary**: Descriptive statistics for numeric columns
- **Categorical Analysis**: Unique value counts and top values for categorical data

## 💡 Example Output

```
📊 DATASET PREVIEW
================================================================================
📏 Shape: 10,000 rows × 12 columns
💾 Memory Usage: 2.54 MB
🔢 Numeric Columns: 9
📝 Categorical Columns: 3
❓ Missing Values: 0
🔄 Duplicate Rows: 0

📋 COLUMNS (12):
   1. sku                  (object    ) - Missing: 0 (0.0%)
   2. sku_description      (object    ) - Missing: 0 (0.0%)
   3. promo_type           (object    ) - Missing: 0 (0.0%)
   4. regular_retail       (float64   ) - Missing: 0 (0.0%)
   ...
```

## 🛠️ API Reference

### DatasetUploader Class

#### Methods

- `upload_dataset(file_path, dataset_name=None, preview=True, **kwargs)`: Upload and process a dataset
- `list_datasets()`: Display all uploaded datasets
- `get_dataset(dataset_id)`: Retrieve a dataset by ID
- `export_dataset(dataset_id, output_path, format_type)`: Export dataset to different format
- `preview_dataset(df, n_rows=10)`: Show detailed dataset preview
- `validate_dataset(df)`: Perform comprehensive data validation

## 📁 Directory Structure

```
/workspace/
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies
├── generate_dataset.py       # Dataset generation script
├── dataset_uploader.py       # Main upload utility
├── demo_upload.py           # Demonstration script
├── uploads/                 # Default upload directory
├── demo_uploads/           # Demo files directory
└── *.csv, *.xlsx          # Generated dataset files
```

## ⚡ Performance Tips

1. **Large Files**: For files > 100MB, consider using Parquet format for better performance
2. **Memory Usage**: The system loads entire datasets into memory - monitor RAM usage for very large files
3. **Format Selection**: Use CSV for compatibility, Excel for business users, Parquet for analytics

## 🔧 Troubleshooting

### Common Issues

1. **Permission Denied**: Use `--break-system-packages` flag if in an externally managed environment
2. **Memory Errors**: Reduce dataset size or increase available RAM
3. **Format Errors**: Ensure file extensions match actual file formats

### Error Messages

- `"Unsupported file format"`: Check if file extension is supported
- `"File not found"`: Verify file path and permissions
- `"Dataset not found"`: Use `list_datasets()` to see available dataset IDs

## 📈 Use Cases

- **Data Analysis**: Quick dataset exploration and validation
- **ETL Pipelines**: Data format conversion and preprocessing
- **Business Intelligence**: Dataset preparation for analytics
- **Research**: Synthetic data generation for testing
- **Education**: Learning data manipulation and analysis

## 🤝 Contributing

Feel free to extend the system with additional features:
- New file format support
- Advanced data validation rules
- Integration with cloud storage
- Web interface
- Database connectivity

## 📄 License

This project is open source and available under the MIT License.
