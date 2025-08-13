import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from typing import Union, Dict, List, Optional
import argparse

class DatasetUploader:
    """
    A comprehensive dataset upload utility supporting multiple formats
    """
    
    SUPPORTED_FORMATS = {
        '.csv': 'CSV',
        '.xlsx': 'Excel',
        '.xls': 'Excel',
        '.json': 'JSON',
        '.parquet': 'Parquet',
        '.feather': 'Feather',
        '.pickle': 'Pickle',
        '.pkl': 'Pickle'
    }
    
    def __init__(self, upload_directory: str = "uploads"):
        """
        Initialize the dataset uploader
        
        Args:
            upload_directory (str): Directory to store uploaded datasets
        """
        self.upload_dir = Path(upload_directory)
        self.upload_dir.mkdir(exist_ok=True)
        self.datasets = {}
    
    def detect_format(self, file_path: Union[str, Path]) -> str:
        """
        Detect file format based on extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Detected format
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension in self.SUPPORTED_FORMATS:
            return self.SUPPORTED_FORMATS[extension]
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def load_dataset(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Load dataset from file based on format
        
        Args:
            file_path: Path to the dataset file
            **kwargs: Additional arguments for pandas readers
            
        Returns:
            pd.DataFrame: Loaded dataset
        """
        file_path = Path(file_path)
        format_type = self.detect_format(file_path)
        
        print(f"Loading {format_type} file: {file_path.name}")
        
        try:
            if format_type == 'CSV':
                df = pd.read_csv(file_path, **kwargs)
            elif format_type == 'Excel':
                df = pd.read_excel(file_path, **kwargs)
            elif format_type == 'JSON':
                df = pd.read_json(file_path, **kwargs)
            elif format_type == 'Parquet':
                df = pd.read_parquet(file_path, **kwargs)
            elif format_type == 'Feather':
                df = pd.read_feather(file_path, **kwargs)
            elif format_type == 'Pickle':
                df = pd.read_pickle(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            print(f"✅ Successfully loaded dataset with shape: {df.shape}")
            return df
            
        except Exception as e:
            print(f"❌ Error loading dataset: {str(e)}")
            raise
    
    def validate_dataset(self, df: pd.DataFrame) -> Dict:
        """
        Validate and analyze the dataset
        
        Args:
            df: DataFrame to validate
            
        Returns:
            dict: Validation results
        """
        validation_results = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(df.select_dtypes(include=['object']).columns),
        }
        
        # Basic statistics for numeric columns
        if validation_results['numeric_columns']:
            validation_results['numeric_stats'] = df[validation_results['numeric_columns']].describe().to_dict()
        
        # Value counts for categorical columns (top 5)
        categorical_info = {}
        for col in validation_results['categorical_columns']:
            categorical_info[col] = {
                'unique_count': df[col].nunique(),
                'top_values': df[col].value_counts().head().to_dict()
            }
        validation_results['categorical_info'] = categorical_info
        
        return validation_results
    
    def preview_dataset(self, df: pd.DataFrame, n_rows: int = 10) -> None:
        """
        Print a preview of the dataset
        
        Args:
            df: DataFrame to preview
            n_rows: Number of rows to show
        """
        print("\n" + "="*80)
        print("📊 DATASET PREVIEW")
        print("="*80)
        
        validation = self.validate_dataset(df)
        
        print(f"📏 Shape: {validation['shape'][0]:,} rows × {validation['shape'][1]} columns")
        print(f"💾 Memory Usage: {validation['memory_usage']}")
        print(f"🔢 Numeric Columns: {len(validation['numeric_columns'])}")
        print(f"📝 Categorical Columns: {len(validation['categorical_columns'])}")
        print(f"❓ Missing Values: {sum(validation['missing_values'].values()):,}")
        print(f"🔄 Duplicate Rows: {validation['duplicate_rows']:,}")
        
        print(f"\n📋 COLUMNS ({len(validation['columns'])}):")
        for i, (col, dtype) in enumerate(zip(validation['columns'], validation['dtypes'].values()), 1):
            missing = validation['missing_values'][col]
            missing_pct = (missing / validation['shape'][0]) * 100
            print(f"  {i:2d}. {col:<20} ({str(dtype):<10}) - Missing: {missing:,} ({missing_pct:.1f}%)")
        
        print(f"\n👀 FIRST {min(n_rows, len(df))} ROWS:")
        print(df.head(n_rows).to_string())
        
        if validation['numeric_columns']:
            print(f"\n📈 NUMERIC STATISTICS:")
            numeric_stats = pd.DataFrame(validation['numeric_stats']).round(2)
            print(numeric_stats.to_string())
        
        if validation['categorical_info']:
            print(f"\n📊 CATEGORICAL SUMMARY:")
            for col, info in validation['categorical_info'].items():
                print(f"  {col}: {info['unique_count']} unique values")
                top_values = ", ".join([f"{k}({v})" for k, v in list(info['top_values'].items())[:3]])
                print(f"    Top values: {top_values}")
        
        print("="*80)
    
    def upload_dataset(self, file_path: Union[str, Path], dataset_name: Optional[str] = None, 
                      preview: bool = True, **load_kwargs) -> str:
        """
        Upload and process a dataset
        
        Args:
            file_path: Path to the dataset file
            dataset_name: Custom name for the dataset (optional)
            preview: Whether to show dataset preview
            **load_kwargs: Additional arguments for loading
            
        Returns:
            str: Dataset identifier
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate dataset name
        if dataset_name is None:
            dataset_name = file_path.stem
        
        print(f"🚀 Uploading dataset: {file_path.name}")
        print(f"📁 File size: {file_path.stat().st_size / 1024**2:.2f} MB")
        
        # Load the dataset
        df = self.load_dataset(file_path, **load_kwargs)
        
        # Store in uploads directory
        upload_path = self.upload_dir / file_path.name
        if upload_path != file_path:
            import shutil
            shutil.copy2(file_path, upload_path)
            print(f"📋 Copied to uploads directory: {upload_path}")
        
        # Store dataset info
        dataset_id = f"{dataset_name}_{len(self.datasets) + 1}"
        self.datasets[dataset_id] = {
            'name': dataset_name,
            'file_path': str(upload_path),
            'dataframe': df,
            'uploaded_at': pd.Timestamp.now(),
            'validation': self.validate_dataset(df)
        }
        
        if preview:
            self.preview_dataset(df)
        
        print(f"✅ Dataset uploaded successfully with ID: {dataset_id}")
        return dataset_id
    
    def list_datasets(self) -> None:
        """List all uploaded datasets"""
        if not self.datasets:
            print("No datasets uploaded yet.")
            return
        
        print("\n📚 UPLOADED DATASETS:")
        print("-" * 80)
        for dataset_id, info in self.datasets.items():
            df_shape = info['dataframe'].shape
            uploaded_time = info['uploaded_at'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"🗂️  {dataset_id}")
            print(f"   Name: {info['name']}")
            print(f"   Shape: {df_shape[0]:,} rows × {df_shape[1]} columns")
            print(f"   File: {Path(info['file_path']).name}")
            print(f"   Uploaded: {uploaded_time}")
            print()
    
    def get_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Get a dataset by ID"""
        if dataset_id not in self.datasets:
            raise KeyError(f"Dataset not found: {dataset_id}")
        return self.datasets[dataset_id]['dataframe']
    
    def export_dataset(self, dataset_id: str, output_path: Union[str, Path], 
                      format_type: str = 'csv') -> None:
        """
        Export a dataset to a different format
        
        Args:
            dataset_id: ID of the dataset to export
            output_path: Path for the exported file
            format_type: Format to export to ('csv', 'excel', 'json', 'parquet')
        """
        df = self.get_dataset(dataset_id)
        output_path = Path(output_path)
        
        print(f"💾 Exporting dataset {dataset_id} to {format_type.upper()}: {output_path}")
        
        if format_type.lower() == 'csv':
            df.to_csv(output_path, index=False)
        elif format_type.lower() == 'excel':
            df.to_excel(output_path, index=False)
        elif format_type.lower() == 'json':
            df.to_json(output_path, orient='records', indent=2)
        elif format_type.lower() == 'parquet':
            df.to_parquet(output_path, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        print(f"✅ Export completed: {output_path}")

def main():
    """Command line interface for the dataset uploader"""
    parser = argparse.ArgumentParser(description="Dataset Upload Utility")
    parser.add_argument("file_path", help="Path to the dataset file")
    parser.add_argument("--name", help="Custom name for the dataset")
    parser.add_argument("--no-preview", action="store_true", help="Skip dataset preview")
    parser.add_argument("--upload-dir", default="uploads", help="Upload directory")
    
    args = parser.parse_args()
    
    uploader = DatasetUploader(upload_directory=args.upload_dir)
    
    try:
        dataset_id = uploader.upload_dataset(
            file_path=args.file_path,
            dataset_name=args.name,
            preview=not args.no_preview
        )
        print(f"\n🎉 Upload completed! Dataset ID: {dataset_id}")
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())