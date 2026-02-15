# EU Financial Sanctions Files (FSF) Access Notes

The European Commission provides the EU financial sanctions consolidated list through the Financial Sanctions Files (FSF) platform.

## Access URL

Main platform: `https://webgate.ec.europa.eu/fsd/fsf`

## Available Formats

- XML (recommended for automated processing)
- CSV
- PDF

## Key Features

### Checksums

The FSF platform provides **SHA-256 checksums** for downloaded files. Always verify checksums after download to ensure data integrity.

### RSS Feed

Subscribe to RSS feed for update notifications:
`https://webgate.ec.europa.eu/fsd/fsf/rss`

### Crawler/Robot Access

The platform supports automated access but requires:
1. Proper User-Agent header
2. Respect for rate limits
3. Tokenized URLs (may be required for some endpoints)

## Integration Approach

### Recommended: Runtime Download

Due to unclear redistribution terms, it's recommended to:
1. Download files at runtime rather than committing to repository
2. Cache with appropriate expiration (e.g., 24 hours)
3. Store with provenance metadata

### Example Download Script

```python
import hashlib
import requests
from pathlib import Path

EU_FSF_XML_URL = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=..."
EU_FSF_CHECKSUM_URL = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/checksum?token=..."

def download_eu_fsf():
    # Download file
    response = requests.get(EU_FSF_XML_URL, timeout=60)
    response.raise_for_status()
    content = response.content
    
    # Download checksum
    checksum_response = requests.get(EU_FSF_CHECKSUM_URL, timeout=30)
    checksum_response.raise_for_status()
    expected_checksum = checksum_response.text.strip()
    
    # Verify
    actual_checksum = hashlib.sha256(content).hexdigest()
    if actual_checksum != expected_checksum:
        raise ValueError(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
    
    # Save
    output_path = Path("data/eu_fsf_consolidated.xml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(content)
    
    return output_path, actual_checksum
```

## Important Notes

### Licensing and Redistribution

- EU data redistribution terms are not as clear as US/UK sources
- Consult legal counsel before redistributing raw list files
- Consider redistributing **connectors/parsers** instead of data files
- Document source and retrieval method in your compliance procedures

### Update Frequency

The EU consolidated list is updated "whenever necessary" according to official guidance. This means:
- Updates are event-driven, not on a fixed schedule
- Monitor RSS feed for notifications
- Poll at least daily for production systems

### Data Scope

The consolidated list is "limited to the freezing of assets" per FSF documentation. This means:
- Primarily financial sanctions
- May not include all types of restrictive measures
- Cross-reference with Official Journal (OJ) for complete legal text

## Manual Access

For manual downloads and exploration:
1. Visit `https://webgate.ec.europa.eu/fsd/fsf`
2. Navigate to "Consolidated list of persons, groups and entities"
3. Select desired format (XML recommended)
4. Download file and checksum
5. Verify checksum before use

## Automation Considerations

### User-Agent

Use a descriptive User-Agent header:
```python
headers = {
    'User-Agent': 'YourCompany-SanctionsScreening/1.0 (contact@yourcompany.com)'
}
```

### Rate Limiting

- Respect platform rate limits
- Implement exponential backoff for retries
- Cache aggressively to minimize requests

### Error Handling

```python
import time

def download_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
```

## Compliance Documentation

When using EU FSF data, document:
1. Source URL and access method
2. Download timestamp (UTC)
3. File checksum (SHA-256)
4. Version/update information from file metadata
5. Legal review of redistribution terms (if applicable)

## Further Information

- FSF User Manual: Available on the FSF platform
- EU Sanctions Map: `https://www.sanctionsmap.eu/`
- Official Journal: `https://eur-lex.europa.eu/`

## Contact

For technical issues with the FSF platform, contact the European Commission's support channels (details available on the FSF website).
