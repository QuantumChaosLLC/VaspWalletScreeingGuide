#!/usr/bin/env python3
"""
OFAC SDN Advanced XML Downloader

Downloads the OFAC SDN Advanced XML file with integrity verification.
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import requests

OFAC_SDN_ADVANCED_URL = "https://www.treasury.gov/ofac/downloads/sdn_advanced.xml"
TIMEOUT_SECONDS = 60


def download_ofac_sdn(output_dir: Path = Path("data")) -> Tuple[Path, str, str]:
    """
    Download OFAC SDN Advanced XML file.
    
    Args:
        output_dir: Directory to save the file
    
    Returns:
        Tuple of (file_path, sha256_hash, timestamp)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading from {OFAC_SDN_ADVANCED_URL}...")
    
    try:
        response = requests.get(OFAC_SDN_ADVANCED_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading: {e}", file=sys.stderr)
        sys.exit(1)
    
    content = response.content
    sha256 = hashlib.sha256(content).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    
    # Save with timestamp and hash in filename
    filename = f"ofac_sdn_advanced_{timestamp.replace(':', '-')}_{sha256[:8]}.xml"
    file_path = output_dir / filename
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    print(f"Downloaded: {file_path}")
    print(f"SHA-256: {sha256}")
    print(f"Timestamp: {timestamp}")
    print(f"Size: {len(content):,} bytes")
    
    # Also save metadata
    metadata_path = file_path.with_suffix('.json')
    import json
    metadata = {
        "source": "OFAC_SDN_ADVANCED",
        "url": OFAC_SDN_ADVANCED_URL,
        "retrieved_at_utc": timestamp,
        "sha256": sha256,
        "size_bytes": len(content),
        "filename": filename
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata: {metadata_path}")
    
    return file_path, sha256, timestamp


if __name__ == "__main__":
    download_ofac_sdn()
