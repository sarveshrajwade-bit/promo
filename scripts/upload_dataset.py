#!/usr/bin/env python3

import argparse
import os
import sys
import shutil
import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'data', 'raw'))
META_FILE = os.path.join(RAW_DIR, '_metadata.json')


def compute_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def ensure_dirs() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)


def load_metadata() -> dict:
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_metadata(metadata: dict) -> None:
    with open(META_FILE, 'w') as f:
        json.dump(metadata, f, indent=2, sort_keys=True)


def is_url(path_or_url: str) -> bool:
    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def download_file(url: str, dest_path: str) -> None:
    import requests
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def infer_format(path: str) -> str:
    lower = path.lower()
    if lower.endswith('.csv'):
        return 'csv'
    if lower.endswith('.tsv'):
        return 'tsv'
    if lower.endswith('.xlsx') or lower.endswith('.xls'):
        return 'excel'
    if lower.endswith('.parquet'):
        return 'parquet'
    return 'unknown'


def read_dataframe(file_path: str, file_format: str) -> pd.DataFrame:
    if file_format == 'csv':
        return pd.read_csv(file_path)
    if file_format == 'tsv':
        return pd.read_csv(file_path, sep='\t')
    if file_format == 'excel':
        return pd.read_excel(file_path)
    if file_format == 'parquet':
        return pd.read_parquet(file_path)
    raise ValueError(f'Unsupported file format for {file_path}')


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    missing = [c for c in required_columns if c not in df.columns]
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description='Upload/ingest a dataset into data/raw')
    parser.add_argument('source', help='Local file path or URL to the dataset (csv, tsv, xlsx, parquet)')
    parser.add_argument('--name', help='Optional dataset name to save as in data/raw. Defaults to basename of the source.')
    parser.add_argument('--required-cols', nargs='*', default=[], help='Optional list of required column names to validate')
    parser.add_argument('--no-preview', action='store_true', help='Skip printing dataframe preview')

    args = parser.parse_args()

    ensure_dirs()

    src = args.source
    given_name = args.name

    temp_download_path = None
    try:
        if is_url(src):
            file_name = os.path.basename(urlparse(src).path) or 'dataset'
            temp_download_path = os.path.join('/tmp', f'upload_{datetime.utcnow().strftime("%Y%m%dT%H%M%S")}_{file_name}')
            download_file(src, temp_download_path)
            source_path = temp_download_path
        else:
            if not os.path.exists(src):
                print(f'Error: source path does not exist: {src}', file=sys.stderr)
                sys.exit(1)
            source_path = os.path.abspath(src)

        dataset_name = given_name or os.path.basename(source_path)
        dest_path = os.path.join(RAW_DIR, dataset_name)

        # If destination exists, de-duplicate by hash
        if os.path.exists(dest_path):
            src_hash = compute_sha256(source_path)
            dest_hash = compute_sha256(dest_path)
            if src_hash == dest_hash:
                print(f'Dataset already uploaded with identical content: {dest_path}')
            else:
                base, ext = os.path.splitext(dataset_name)
                new_name = f"{base}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}{ext}"
                dest_path = os.path.join(RAW_DIR, new_name)
                shutil.copy2(source_path, dest_path)
                print(f'Existing dataset name existed with different content. Saved as: {dest_path}')
        else:
            shutil.copy2(source_path, dest_path)
            print(f'Saved dataset to: {dest_path}')

        file_format = infer_format(dest_path)
        if file_format == 'unknown':
            print('Warning: unknown file extension. Attempting to read as CSV...')
            file_format = 'csv'

        try:
            df = read_dataframe(dest_path, file_format)
        except Exception as e:
            print(f'Warning: could not read dataset for preview/validation: {e}', file=sys.stderr)
            df = None

        # Validate columns if requested
        if df is not None and args.required_cols:
            missing = validate_required_columns(df, args.required_cols)
            if missing:
                print(f'Error: missing required columns: {missing}', file=sys.stderr)
                sys.exit(2)

        # Preview
        if df is not None and not args.no_preview:
            print('\nSchema:')
            print(pd.DataFrame({'column': df.columns, 'dtype': df.dtypes.astype(str)}))
            print('\nPreview:')
            print(df.head(10))
            print('\nRow count:', len(df))

        # Update metadata
        metadata = load_metadata()
        file_hash = compute_sha256(dest_path)
        metadata[os.path.basename(dest_path)] = {
            'path': dest_path,
            'uploaded_at_utc': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            'sha256': file_hash,
            'format': file_format,
            'size_bytes': os.path.getsize(dest_path),
        }
        save_metadata(metadata)

    finally:
        if temp_download_path and os.path.exists(temp_download_path):
            try:
                os.remove(temp_download_path)
            except Exception:
                pass


if __name__ == '__main__':
    main()