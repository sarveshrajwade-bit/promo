#!/usr/bin/env python3
"""
Simple command-line interface for uploading datasets.
"""

import argparse
import sys
import os
from data_upload_utils import DatasetUploader

def main():
    parser = argparse.ArgumentParser(description="Upload and manage datasets")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a dataset file')
    upload_parser.add_argument('source_path', help='Path to the dataset file')
    upload_parser.add_argument('dataset_name', help='Name for the dataset')
    upload_parser.add_argument('-d', '--description', default='', help='Description of the dataset')
    upload_parser.add_argument('-t', '--tags', nargs='*', default=[], help='Tags for the dataset')
    upload_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing dataset')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all datasets')
    list_parser.add_argument('-t', '--tags', nargs='*', help='Filter by tags')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get info about a specific dataset')
    info_parser.add_argument('dataset_name', help='Name of the dataset')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a dataset')
    delete_parser.add_argument('dataset_name', help='Name of the dataset to delete')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show dataset summary')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize uploader
    uploader = DatasetUploader()
    
    # Handle commands
    if args.command == 'upload':
        if not os.path.exists(args.source_path):
            print(f"Error: Source file '{args.source_path}' not found")
            sys.exit(1)
        
        result = uploader.upload_file(
            source_path=args.source_path,
            dataset_name=args.dataset_name,
            description=args.description,
            tags=args.tags,
            overwrite=args.overwrite
        )
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
            dataset_info = result['dataset_info']
            if 'rows' in dataset_info and 'columns' in dataset_info:
                print(f"   📊 {dataset_info['rows']} rows × {dataset_info['columns']} columns")
            print(f"   📁 {dataset_info['file_size']} bytes")
        else:
            print(f"❌ {result['message']}")
            sys.exit(1)
    
    elif args.command == 'list':
        datasets = uploader.list_datasets(tags=args.tags)
        
        if not datasets:
            print("No datasets found.")
            return
        
        print(f"Found {len(datasets)} dataset(s):")
        print()
        
        for dataset in datasets:
            print(f"📊 {dataset['name']}")
            if dataset.get('description'):
                print(f"   Description: {dataset['description']}")
            if 'rows' in dataset and 'columns' in dataset:
                print(f"   Size: {dataset['rows']} rows × {dataset['columns']} columns")
            print(f"   File: {dataset['filename']} ({dataset['file_size']} bytes)")
            if dataset.get('tags'):
                print(f"   Tags: {', '.join(dataset['tags'])}")
            print(f"   Uploaded: {dataset.get('upload_date', 'Unknown')}")
            print()
    
    elif args.command == 'info':
        dataset_info = uploader.get_dataset_info(args.dataset_name)
        
        if not dataset_info:
            print(f"Dataset '{args.dataset_name}' not found.")
            sys.exit(1)
        
        print(f"📊 Dataset: {dataset_info['name']}")
        print(f"   Description: {dataset_info.get('description', 'No description')}")
        print(f"   File: {dataset_info['filename']}")
        print(f"   File type: {dataset_info['file_type']}")
        print(f"   File size: {dataset_info['file_size']} bytes")
        print(f"   Upload date: {dataset_info.get('upload_date', 'Unknown')}")
        
        if 'rows' in dataset_info and 'columns' in dataset_info:
            print(f"   Dimensions: {dataset_info['rows']} rows × {dataset_info['columns']} columns")
            print(f"   Columns: {', '.join(dataset_info['column_names'])}")
        
        if dataset_info.get('tags'):
            print(f"   Tags: {', '.join(dataset_info['tags'])}")
    
    elif args.command == 'delete':
        if not args.confirm:
            response = input(f"Are you sure you want to delete dataset '{args.dataset_name}'? (y/N): ")
            if response.lower() != 'y':
                print("Deletion cancelled.")
                return
        
        result = uploader.delete_dataset(args.dataset_name)
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            sys.exit(1)
    
    elif args.command == 'summary':
        summary = uploader.get_summary()
        
        print("📊 Dataset Summary")
        print(f"   Total datasets: {summary['total_datasets']}")
        print(f"   Total size: {summary['total_size_mb']} MB")
        
        if summary['file_types']:
            print(f"   File types: {summary['file_types']}")
        
        if summary['datasets']:
            print(f"   Datasets: {', '.join(summary['datasets'])}")

if __name__ == "__main__":
    main()