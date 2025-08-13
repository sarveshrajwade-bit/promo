#!/usr/bin/env python3
"""
Dataset Upload Demo
This script demonstrates all the features of the dataset upload system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_uploader import DatasetUploader
from generate_dataset import generate_promotions_dataset
import pandas as pd

def demo_dataset_upload():
    """Comprehensive demo of dataset upload functionality"""
    
    print("🚀 DATASET UPLOAD SYSTEM DEMO")
    print("=" * 80)
    
    # Initialize the uploader
    uploader = DatasetUploader(upload_directory="demo_uploads")
    
    print("\n1. 📊 GENERATING SAMPLE DATASETS")
    print("-" * 40)
    
    # Generate datasets in different formats
    print("Generating small sample datasets...")
    
    # Small CSV dataset
    df_small = generate_promotions_dataset(num_rows=100, output_format='csv', output_file='sample_small.csv')
    print(f"✅ Created small CSV: sample_small.csv ({df_small.shape[0]} rows)")
    
    # Medium Excel dataset  
    df_medium = generate_promotions_dataset(num_rows=1000, output_format='excel', output_file='sample_medium.xlsx')
    print(f"✅ Created medium Excel: sample_medium.xlsx ({df_medium.shape[0]} rows)")
    
    # Large CSV dataset
    df_large = generate_promotions_dataset(num_rows=5000, output_format='csv', output_file='sample_large.csv')
    print(f"✅ Created large CSV: sample_large.csv ({df_large.shape[0]} rows)")
    
    print("\n2. 📁 UPLOADING DATASETS")
    print("-" * 40)
    
    # Upload the small dataset with full preview
    print("Uploading small dataset with full preview...")
    dataset_id_1 = uploader.upload_dataset('sample_small.csv', dataset_name='Small Sample', preview=True)
    
    print("\nUploading medium dataset...")
    dataset_id_2 = uploader.upload_dataset('sample_medium.xlsx', dataset_name='Medium Sample', preview=False)
    print(f"✅ Medium dataset uploaded with ID: {dataset_id_2}")
    
    print("\nUploading large dataset...")
    dataset_id_3 = uploader.upload_dataset('sample_large.csv', dataset_name='Large Sample', preview=False)
    print(f"✅ Large dataset uploaded with ID: {dataset_id_3}")
    
    print("\n3. 📚 LISTING UPLOADED DATASETS")
    print("-" * 40)
    uploader.list_datasets()
    
    print("\n4. 🔍 DATASET ANALYSIS")
    print("-" * 40)
    
    # Get a dataset and show detailed analysis
    df = uploader.get_dataset(dataset_id_1)
    print(f"Retrieved dataset '{dataset_id_1}' for analysis:")
    uploader.preview_dataset(df, n_rows=5)
    
    print("\n5. 💾 EXPORTING DATASETS")
    print("-" * 40)
    
    # Export to different formats
    print("Exporting small dataset to different formats...")
    uploader.export_dataset(dataset_id_1, 'exported_small.json', 'json')
    uploader.export_dataset(dataset_id_2, 'exported_medium.csv', 'csv')
    
    print("\n6. 📊 ADVANCED DATASET OPERATIONS")
    print("-" * 40)
    
    # Demonstrate data manipulation
    df = uploader.get_dataset(dataset_id_3)
    print(f"Original dataset shape: {df.shape}")
    
    # Filter high-value promotions
    high_value = df[df['sales_revenue'] > df['sales_revenue'].quantile(0.9)]
    print(f"High-value promotions (top 10%): {high_value.shape[0]} rows")
    print(f"Average sales revenue in top 10%: ${high_value['sales_revenue'].mean():.2f}")
    
    # Group by promo type
    promo_summary = df.groupby('promo_type').agg({
        'sales_revenue': ['count', 'mean', 'sum'],
        'margin_rate': 'mean',
        'discount_percent': 'mean'
    }).round(2)
    
    print("\nPromo Type Performance Summary:")
    print(promo_summary)
    
    print("\n7. ✅ DEMO COMPLETED")
    print("-" * 40)
    print("🎉 All dataset upload features demonstrated successfully!")
    print(f"📁 Demo files stored in: {uploader.upload_dir}")
    print("\nGenerated files:")
    print("  - sample_small.csv (100 rows)")
    print("  - sample_medium.xlsx (1,000 rows)")  
    print("  - sample_large.csv (5,000 rows)")
    print("  - exported_small.json")
    print("  - exported_medium.csv")
    
    return uploader

if __name__ == "__main__":
    try:
        uploader = demo_dataset_upload()
        print(f"\n📋 Final status: {len(uploader.datasets)} datasets uploaded successfully")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        sys.exit(1)