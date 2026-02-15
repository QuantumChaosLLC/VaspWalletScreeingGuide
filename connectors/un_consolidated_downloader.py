#!/usr/bin/env python3
"""
UN Consolidated List Downloader

Downloads the UN Security Council Consolidated List in XML format.
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import requests

UN_CONSOLIDATED_XML_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
TIMEOUT_SECONDS = 60


def download_un_consolidated(output_dir: Path = Path("data")) -> Tuple[Path, str, str]:
    """
    Download UN Consolidated List XML file.
    
    Args:
        output_dir: Directory to save the file
    
    Returns:
        Tuple of (file_path, sha256_hash, timestamp)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading from {UN_CONSOLIDATED_XML_URL}...")
    
    try:
        response = requests.get(UN_CONSOLIDATED_XML_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading: {e}", file=sys.stderr)
        sys.exit(1)
    
    content = response.content
    sha256 = hashlib.sha256(content).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    
    # Save with timestamp and hash in filename
    filename = f"un_consolidated_{timestamp.replace(':', '-')}_{sha256[:8]}.xml"
    file_path = output_dir / filename
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    print(f"Downloaded: {file_path}")
    print(f"SHA-256: {sha256}")
    print(f"Timestamp: {timestamp}")
    print(f"Size: {len(content):,} bytes")
    
    # Save metadata
    metadata_path = file_path.with_suffix('.json')
    import json
    metadata = {
        "source": "UN_CONSOLIDATED_LIST",
        "url": UN_CONSOLIDATED_XML_URL,
        "retrieved_at_utc": timestamp,
        "sha256": sha256,
        "size_bytes": len(content),
        "filename": filename,
        "note": "UN website terms and copyright apply"
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata: {metadata_path}")
    
    return file_path, sha256, timestamp


if __name__ == "__main__":
    download_un_consolidated()
