import pandas as pd
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import shutil

class DatasetUploader:
    """
    A comprehensive utility for uploading, managing, and organizing datasets.
    """
    
    def __init__(self, base_data_dir: str = "data"):
        """
        Initialize the DatasetUploader.
        
        Args:
            base_data_dir (str): Base directory for storing datasets
        """
        self.base_data_dir = base_data_dir
        self.metadata_file = os.path.join(base_data_dir, "dataset_metadata.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(base_data_dir, exist_ok=True)
        
        # Load existing metadata or create new
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load dataset metadata from file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"datasets": {}, "upload_history": []}
    
    def _save_metadata(self):
        """Save dataset metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def upload_file(self, 
                   source_path: str, 
                   dataset_name: str,
                   description: str = "",
                   tags: List[str] = None,
                   overwrite: bool = False) -> Dict[str, Any]:
        """
        Upload a dataset file to the data directory.
        
        Args:
            source_path (str): Path to the source file
            dataset_name (str): Name for the dataset (used for filename)
            description (str): Description of the dataset
            tags (List[str]): Tags for categorizing the dataset
            overwrite (bool): Whether to overwrite existing file
            
        Returns:
            Dict containing upload status and metadata
        """
        if not os.path.exists(source_path):
            return {"status": "error", "message": f"Source file not found: {source_path}"}
        
        # Get file extension
        _, ext = os.path.splitext(source_path)
        destination_path = os.path.join(self.base_data_dir, f"{dataset_name}{ext}")
        
        # Check if dataset already exists in metadata
        if dataset_name in self.metadata["datasets"] and not overwrite:
            return {"status": "error", "message": f"Dataset '{dataset_name}' already exists. Use overwrite=True to replace."}
        
        try:
            # Check if source and destination are the same file
            if os.path.abspath(source_path) == os.path.abspath(destination_path):
                # File is already in the correct location, just register it
                print("File is already in the data directory, registering...")
            else:
                # Copy file to data directory
                shutil.copy2(source_path, destination_path)
            
            # Get file info
            file_size = os.path.getsize(destination_path)
            upload_time = datetime.now()
            
            # Update metadata
            dataset_info = {
                "name": dataset_name,
                "filename": f"{dataset_name}{ext}",
                "description": description,
                "tags": tags or [],
                "file_size": file_size,
                "upload_date": upload_time,
                "source_path": source_path,
                "file_type": ext[1:] if ext else "unknown"
            }
            
            # Try to get dataset info if it's a supported format
            try:
                if ext.lower() in ['.csv', '.xlsx', '.xls']:
                    df = pd.read_csv(destination_path) if ext.lower() == '.csv' else pd.read_excel(destination_path)
                    dataset_info.update({
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns),
                        "data_types": df.dtypes.to_dict()
                    })
            except Exception as e:
                dataset_info["analysis_error"] = str(e)
            
            # Save to metadata
            self.metadata["datasets"][dataset_name] = dataset_info
            self.metadata["upload_history"].append({
                "dataset_name": dataset_name,
                "action": "upload",
                "timestamp": upload_time,
                "file_size": file_size
            })
            
            self._save_metadata()
            
            return {
                "status": "success",
                "message": f"Dataset '{dataset_name}' uploaded successfully",
                "dataset_info": dataset_info
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Upload failed: {str(e)}"}
    
    def upload_dataframe(self, 
                        df: pd.DataFrame,
                        dataset_name: str,
                        file_format: str = "xlsx",
                        description: str = "",
                        tags: List[str] = None,
                        overwrite: bool = False) -> Dict[str, Any]:
        """
        Upload a pandas DataFrame as a dataset.
        
        Args:
            df (pd.DataFrame): DataFrame to upload
            dataset_name (str): Name for the dataset
            file_format (str): Format to save ('csv', 'xlsx', 'json')
            description (str): Description of the dataset
            tags (List[str]): Tags for categorizing the dataset
            overwrite (bool): Whether to overwrite existing file
            
        Returns:
            Dict containing upload status and metadata
        """
        if dataset_name in self.metadata["datasets"] and not overwrite:
            return {"status": "error", "message": f"Dataset '{dataset_name}' already exists. Use overwrite=True to replace."}
        
        # Create filename
        filename = f"{dataset_name}.{file_format}"
        filepath = os.path.join(self.base_data_dir, filename)
        
        try:
            # Save DataFrame in specified format
            if file_format.lower() == 'csv':
                df.to_csv(filepath, index=False)
            elif file_format.lower() in ['xlsx', 'xls']:
                df.to_excel(filepath, index=False)
            elif file_format.lower() == 'json':
                df.to_json(filepath, orient='records', indent=2)
            else:
                return {"status": "error", "message": f"Unsupported file format: {file_format}"}
            
            # Get file info
            file_size = os.path.getsize(filepath)
            upload_time = datetime.now()
            
            # Create metadata
            dataset_info = {
                "name": dataset_name,
                "filename": filename,
                "description": description,
                "tags": tags or [],
                "file_size": file_size,
                "upload_date": upload_time,
                "source_path": "dataframe",
                "file_type": file_format,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict()
            }
            
            # Save to metadata
            self.metadata["datasets"][dataset_name] = dataset_info
            self.metadata["upload_history"].append({
                "dataset_name": dataset_name,
                "action": "upload_dataframe",
                "timestamp": upload_time,
                "file_size": file_size
            })
            
            self._save_metadata()
            
            return {
                "status": "success",
                "message": f"DataFrame uploaded as '{dataset_name}' successfully",
                "dataset_info": dataset_info
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Upload failed: {str(e)}"}
    
    def list_datasets(self, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        List all uploaded datasets.
        
        Args:
            tags (List[str]): Filter by tags (optional)
            
        Returns:
            List of dataset information
        """
        datasets = []
        for name, info in self.metadata["datasets"].items():
            if tags:
                if not any(tag in info.get("tags", []) for tag in tags):
                    continue
            datasets.append(info)
        
        return sorted(datasets, key=lambda x: x.get("upload_date", ""), reverse=True)
    
    def get_dataset_info(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific dataset."""
        return self.metadata["datasets"].get(dataset_name)
    
    def load_dataset(self, dataset_name: str) -> Optional[pd.DataFrame]:
        """
        Load a dataset as a pandas DataFrame.
        
        Args:
            dataset_name (str): Name of the dataset to load
            
        Returns:
            pandas DataFrame or None if not found
        """
        if dataset_name not in self.metadata["datasets"]:
            print(f"Dataset '{dataset_name}' not found")
            return None
        
        dataset_info = self.metadata["datasets"][dataset_name]
        filepath = os.path.join(self.base_data_dir, dataset_info["filename"])
        
        if not os.path.exists(filepath):
            print(f"Dataset file not found: {filepath}")
            return None
        
        try:
            file_type = dataset_info["file_type"].lower()
            if file_type == 'csv':
                return pd.read_csv(filepath)
            elif file_type in ['xlsx', 'xls']:
                return pd.read_excel(filepath)
            elif file_type == 'json':
                return pd.read_json(filepath)
            else:
                print(f"Unsupported file type: {file_type}")
                return None
        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            return None
    
    def delete_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Delete a dataset and its metadata.
        
        Args:
            dataset_name (str): Name of the dataset to delete
            
        Returns:
            Dict containing deletion status
        """
        if dataset_name not in self.metadata["datasets"]:
            return {"status": "error", "message": f"Dataset '{dataset_name}' not found"}
        
        try:
            dataset_info = self.metadata["datasets"][dataset_name]
            filepath = os.path.join(self.base_data_dir, dataset_info["filename"])
            
            # Delete file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from metadata
            del self.metadata["datasets"][dataset_name]
            
            # Add to history
            self.metadata["upload_history"].append({
                "dataset_name": dataset_name,
                "action": "delete",
                "timestamp": datetime.now()
            })
            
            self._save_metadata()
            
            return {
                "status": "success",
                "message": f"Dataset '{dataset_name}' deleted successfully"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Deletion failed: {str(e)}"}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all datasets."""
        datasets = self.metadata["datasets"]
        total_size = sum(info.get("file_size", 0) for info in datasets.values())
        
        file_types = {}
        for info in datasets.values():
            file_type = info.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            "total_datasets": len(datasets),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "datasets": list(datasets.keys())
        }

def main():
    """Example usage of the DatasetUploader."""
    uploader = DatasetUploader()
    
    print("=== Dataset Upload Utility ===\n")
    
    # Check if the generated dataset exists
    promotions_file = "data/promotions_dataset.xlsx"
    if os.path.exists(promotions_file):
        print("Found generated promotions dataset. Uploading...")
        result = uploader.upload_file(
            source_path=promotions_file,
            dataset_name="promotions_dataset",
            description="Synthetic promotions dataset with retail and performance metrics",
            tags=["retail", "promotions", "synthetic", "performance"],
            overwrite=True
        )
        print(f"Upload result: {result['status']} - {result['message']}\n")
    
    # Display summary
    summary = uploader.get_summary()
    print("=== Dataset Summary ===")
    print(f"Total datasets: {summary['total_datasets']}")
    print(f"Total size: {summary['total_size_mb']} MB")
    print(f"File types: {summary['file_types']}")
    
    if summary['datasets']:
        print(f"Datasets: {', '.join(summary['datasets'])}")
    
    print("\n=== Available Datasets ===")
    datasets = uploader.list_datasets()
    for dataset in datasets:
        print(f"- {dataset['name']}: {dataset.get('description', 'No description')}")
        if 'rows' in dataset and 'columns' in dataset:
            print(f"  Size: {dataset['rows']} rows × {dataset['columns']} columns")
        print(f"  File: {dataset['filename']} ({dataset['file_size']} bytes)")
        print(f"  Tags: {', '.join(dataset.get('tags', []))}")
        print()

if __name__ == "__main__":
    main()