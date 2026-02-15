#!/usr/bin/env python3
"""
UK Sanctions List Downloader

Downloads the UK Sanctions List in XML format.
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import requests

# Note: This is the publications page. The actual XML download link
# can be found on this page and changes with each update.
UK_SANCTIONS_PAGE = "https://www.gov.uk/government/publications/the-uk-sanctions-list"

# Direct link to XML (update this URL as needed)
UK_SANCTIONS_XML_URL = "https://assets.publishing.service.gov.uk/media/LATEST/UK_Sanctions_List.xml"

TIMEOUT_SECONDS = 60


def download_uk_sanctions(output_dir: Path = Path("data")) -> Tuple[Path, str, str]:
    """
    Download UK Sanctions List XML file.
    
    Args:
        output_dir: Directory to save the file
    
    Returns:
        Tuple of (file_path, sha256_hash, timestamp)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading from {UK_SANCTIONS_XML_URL}...")
    print(f"Note: If this fails, check {UK_SANCTIONS_PAGE} for the latest XML link")
    
    try:
        response = requests.get(UK_SANCTIONS_XML_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading: {e}", file=sys.stderr)
        print(f"Please visit {UK_SANCTIONS_PAGE} to get the current XML URL", file=sys.stderr)
        sys.exit(1)
    
    content = response.content
    sha256 = hashlib.sha256(content).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    
    # Save with timestamp and hash in filename
    filename = f"uk_sanctions_list_{timestamp.replace(':', '-')}_{sha256[:8]}.xml"
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
        "source": "UK_SANCTIONS_LIST",
        "url": UK_SANCTIONS_XML_URL,
        "retrieved_at_utc": timestamp,
        "sha256": sha256,
        "size_bytes": len(content),
        "filename": filename,
        "license": "Open Government Licence v3.0",
        "license_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata: {metadata_path}")
    print(f"License: Open Government Licence v3.0")
    
    return file_path, sha256, timestamp


if __name__ == "__main__":
    download_uk_sanctions()
