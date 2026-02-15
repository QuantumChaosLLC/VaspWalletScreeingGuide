# Authoritative Sources Deep Dive

This document provides detailed context on each authoritative sanctions source, including operational considerations, data formats, and integration patterns.

## OFAC (Office of Foreign Assets Control)

### Why OFAC is primary for crypto sanctions

OFAC is the only major sanctions authority that consistently publishes **explicit blockchain addresses** in structured fields within its SDN (Specially Designated Nationals) list. The field format is:

```
Digital Currency Address - {TICKER}
```

Where `{TICKER}` is typically:
- `XBT` for Bitcoin
- `ETH` for Ethereum
- `XMR` for Monero
- `LTC` for Litecoin
- `ZEC` for Zcash
- `DASH` for Dash
- `BSV` for Bitcoin SV
- `BCH` for Bitcoin Cash
- `BTG` for Bitcoin Gold
- `ETC` for Ethereum Classic
- `XVG` for Verge
- `USDT` for Tether (on various chains)

### OFAC data formats

OFAC provides multiple download formats:

1. **CSV (delimited)** - Simple, but may have parsing edge cases with special characters
2. **XML (standard)** - Structured but less detailed
3. **XML (advanced)** - Most comprehensive; includes all ID fields with proper typing
4. **PDF** - Human-readable only; not for automated parsing

**Recommendation:** Use `sdn_advanced.xml` for production systems.

### OFAC update frequency

OFAC updates are **event-driven** and can be:
- Multiple times per day during active enforcement periods
- Weeks between updates during quiet periods

**Operational guidance:**
- Poll at least daily
- Consider hourly polling for high-risk operations
- Subscribe to OFAC email alerts for immediate notification
- Store every version with timestamp and hash

### OFAC's explicit limitation

From OFAC's own guidance:

> "The digital currency addresses listed on the SDN List are not likely to be exhaustive. Parties who identify a digital currency address that they believe is associated with an SDN should block the address and report it to OFAC."

**Implication:** Address-list screening is necessary but not sufficient. You must also:
- Monitor for new addresses controlled by known SDNs
- Use clustering/attribution intelligence
- Implement ongoing monitoring, not just point-in-time checks

### OFAC search behavior

OFAC's Sanctions List Search tool uses **exact matching** for digital currency addresses (the "ID #" field). This means:
- No fuzzy matching
- No partial matching
- Case sensitivity depends on the blockchain (handle in your canonicalization)

### Integration pattern

```python
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import hashlib

OFAC_SDN_ADVANCED_URL = "https://www.treasury.gov/ofac/downloads/sdn_advanced.xml"

def download_ofac_sdn():
    response = requests.get(OFAC_SDN_ADVANCED_URL, timeout=30)
    response.raise_for_status()
    
    content = response.content
    sha256 = hashlib.sha256(content).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    
    # Store immutably
    filename = f"ofac_sdn_advanced_{timestamp}_{sha256[:8]}.xml"
    with open(filename, 'wb') as f:
        f.write(content)
    
    return filename, sha256, timestamp

def parse_digital_currency_addresses(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    addresses = []
    
    for entry in root.findall('.//sdnEntry'):
        uid = entry.find('uid').text if entry.find('uid') is not None else None
        
        for id_elem in entry.findall('.//id'):
            id_type = id_elem.find('idType').text if id_elem.find('idType') is not None else ""
            id_number = id_elem.find('idNumber').text if id_elem.find('idNumber') is not None else ""
            
            if id_type and id_type.startswith("Digital Currency Address"):
                # Extract ticker from "Digital Currency Address - XBT"
                parts = id_type.split(" - ")
                ticker = parts[1] if len(parts) > 1 else "UNKNOWN"
                
                addresses.append({
                    'uid': uid,
                    'ticker': ticker,
                    'address': id_number.strip()
                })
    
    return addresses
```

## United Nations Security Council Consolidated List

### Purpose and scope

The UN Consolidated List combines:
- Al-Qaida Sanctions List
- ISIL (Da'esh) & Al-Qaida Sanctions List
- Taliban Sanctions List
- Other UNSC sanctions regimes

### Data format

Available in:
- **XML** - Structured, machine-readable (recommended)
- **HTML** - Web display
- **PDF** - Human-readable

### Key fields

- Name (with aliases)
- Date of birth
- Place of birth
- Nationality
- Passport numbers
- National identification numbers
- Address
- **Note:** Generally does NOT include blockchain addresses

### Integration approach

Use UN list for:
1. Entity name screening
2. Cross-referencing with OFAC/EU/UK lists
3. Building a comprehensive sanctions entity database

Then map entities to blockchain addresses using:
- Commercial intelligence (Chainalysis, TRM, Elliptic)
- Internal investigations
- Vetted OSINT

### Update mechanism

- UN publishes an "Updates" page with press releases
- Check daily for new designations
- Store historical versions for audit trails

## European Union Financial Sanctions

### EU sanctions architecture

EU sanctions are implemented through:
1. **Council Regulations** - Directly applicable in all member states
2. **Council Decisions** - Binding on member states
3. **Consolidated List** - Administrative compilation (not legal instrument itself)

### Financial Sanctions Files (FSF) platform

The EU provides a dedicated platform at `webgate.ec.europa.eu` with:
- Downloadable consolidated list files
- XML, CSV, PDF formats
- **Checksums** for integrity verification (important!)
- RSS feed for updates
- Crawler/robot access guidelines

### Integration considerations

**Licensing concern:** EU data redistribution terms are less clear than US/UK. Recommended approach:
- Download at runtime rather than committing to repo
- Cache with expiration
- Document source and retrieval method
- Consult legal counsel for redistribution

### Checksum verification

```python
import hashlib
import requests

def verify_eu_fsf_download(url, expected_checksum):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    content = response.content
    actual_checksum = hashlib.sha256(content).hexdigest()
    
    if actual_checksum != expected_checksum:
        raise ValueError(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
    
    return content
```

## United Kingdom Sanctions List

### UK sanctions post-Brexit

The UK now maintains its own sanctions regime, independent of the EU. The UK Sanctions List (UKSL) is the authoritative source.

### Licensing advantage

UK Government content is generally available under the **Open Government Licence v3.0**, which permits:
- Copying
- Publishing
- Distributing
- Transmitting
- Adapting

**Conditions:**
- Acknowledge the source
- Provide a link to the license
- State if you've modified the data

This makes UK data particularly suitable for open-source redistribution.

### Format options

Seven formats available:
- ODT (OpenDocument Text)
- ODS (OpenDocument Spreadsheet)
- XML (machine-readable, recommended)
- HTML (web display)
- TXT (plain text)
- CSV (comma-separated)
- PDF (human-readable)

### Integration pattern

```python
UK_SANCTIONS_XML_URL = "https://www.gov.uk/government/publications/the-uk-sanctions-list"

def download_uk_sanctions():
    # Note: Actual download URL is on the publications page
    # This is a simplified example
    response = requests.get(UK_SANCTIONS_XML_URL, timeout=30)
    response.raise_for_status()
    return response.content
```

## Canada Consolidated Autonomous Sanctions List

### Important limitation

Canada explicitly warns:

> "The Consolidated Canadian Autonomous Sanctions List is not a regulation. It is an administrative document that consolidates information from regulations... The consolidated list may not be up to date because the regulations are updated frequently."

**Implication:** Use for screening, but maintain a process to reconcile against underlying regulations for high-risk cases.

### Format and access

- HTML (web display)
- PDF (download)
- XML (machine-readable)

### Integration approach

- Use as a screening aid
- Flag matches for enhanced review
- For confirmed matches, verify against official regulations
- Document the reconciliation process

## FATF Guidance

### Not a sanctions list

FATF (Financial Action Task Force) does not publish sanctions lists. Instead, it provides:
- Standards for AML/CFT (Anti-Money Laundering / Countering the Financing of Terrorism)
- Guidance for risk-based approaches
- Expectations for VASPs (Virtual Asset Service Providers)

### Key FATF requirements for VASPs

From the October 2021 Updated Guidance:

1. **Travel Rule** - VASPs must obtain, hold, and transmit required originator and beneficiary information
2. **Risk-based approach** - Screening must be proportionate to risk
3. **Ongoing monitoring** - Not just point-in-time checks
4. **Suspicious activity reporting** - Report to FIUs (Financial Intelligence Units)

### How to use FATF guidance

- Design your screening controls to meet FATF expectations
- Document your risk-based approach
- Use FATF guidance to justify threshold decisions
- Reference in compliance policies and procedures

## US Consolidated Screening List (CSL)

### What CSL consolidates

The CSL combines multiple US restricted party lists:
- OFAC SDN List
- Bureau of Industry and Security (BIS) Denied Persons List
- BIS Entity List
- BIS Unverified List
- State Department Nonproliferation Sanctions
- And others

### API vs. bulk download

**API:**
- Real-time search
- Fuzzy matching available
- Rate limited
- Good for name/entity screening

**Bulk download:**
- CSV, TSV, JSON formats
- Updated daily (5:00 AM EST/EDT)
- Good for building local indexes
- No rate limits

### Integration pattern

```python
CSL_API_URL = "https://api.trade.gov/consolidated_screening_list/search"

def search_csl(name, fuzzy=True):
    params = {
        'name': name,
        'fuzzy_name': 'true' if fuzzy else 'false'
    }
    response = requests.get(CSL_API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Licensing

CSL data is published as **public domain (us-pd)** in US government data catalogs. This means:
- No copyright restrictions in the US
- Free to use, modify, redistribute
- No attribution required (but recommended)

## Cross-list reconciliation

### Why reconcile across lists

Sanctioned parties often appear on multiple lists with:
- Slight name variations
- Different aliases
- Additional identifying information on some lists

### Reconciliation strategy

1. **Use unique identifiers where available:**
   - Passport numbers
   - National ID numbers
   - Date of birth + place of birth
   - Known blockchain addresses

2. **Fuzzy name matching with high thresholds:**
   - Levenshtein distance
   - Soundex/Metaphone for phonetic matching
   - Token-based matching

3. **Manual review for ambiguous cases**

4. **Document reconciliation decisions**

### Example reconciliation logic

```python
from fuzzywuzzy import fuzz

def reconcile_entities(ofac_entity, un_entity, threshold=90):
    """
    Determine if two entities from different lists are the same person/org.
    """
    name_score = fuzz.token_sort_ratio(
        ofac_entity['name'].lower(),
        un_entity['name'].lower()
    )
    
    if name_score >= threshold:
        # Check additional fields
        if ofac_entity.get('dob') == un_entity.get('dob'):
            return True, "High confidence: name + DOB match"
        elif ofac_entity.get('passport') == un_entity.get('passport'):
            return True, "High confidence: name + passport match"
        else:
            return True, f"Moderate confidence: name match ({name_score})"
    
    return False, "No match"
```

## Operational best practices

### Version control for sanctions lists

Every downloaded list should be stored with:
```json
{
  "source": "OFAC_SDN",
  "format": "XML_ADVANCED",
  "url": "https://www.treasury.gov/ofac/downloads/sdn_advanced.xml",
  "retrieved_at_utc": "2026-02-15T05:46:03Z",
  "sha256": "abc123...",
  "parser_version": "1.2.3",
  "record_count": 12543
}
```

### Audit trail requirements

For every screening decision, log:
- Subject identifier (wallet address, entity name, etc.)
- Screening timestamp
- List versions used (with hashes)
- Match results (hit/no-hit)
- Risk score
- Action taken (allow/block/escalate)
- Reviewer (if manual review)
- Case ID (if created)

### Continuous monitoring

Sanctions screening is not one-time:
1. **Onboarding** - Screen new customers/wallets
2. **Pre-transaction** - Screen before processing
3. **Post-transaction** - Monitor for retroactive designations
4. **Periodic re-screening** - Re-check existing relationships

### Handling retroactive designations

When an address becomes sanctioned after you've already transacted:
1. Identify all affected transactions
2. Calculate exposure (amounts, dates)
3. File required reports (SAR, blocking report, etc.)
4. Freeze any remaining assets
5. Document remediation steps

## Performance considerations

### Indexing strategies

For large-scale screening:

**Option 1: In-memory hash set**
```python
sanctioned_addresses = set(load_addresses())  # O(1) lookup
```

**Option 2: Database with indexes**
```sql
CREATE INDEX idx_sanctioned_addresses ON sanctioned_addresses(chain, address);
```

**Option 3: Bloom filter for pre-filtering**
```python
from pybloom_live import BloomFilter

bf = BloomFilter(capacity=100000, error_rate=0.001)
for addr in sanctioned_addresses:
    bf.add(addr)

# Fast negative check
if address not in bf:
    return False  # Definitely not sanctioned
else:
    return address in sanctioned_addresses  # Confirm with exact check
```

### Caching vendor API responses

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=10000)
def cached_vendor_screen(address, chain, cache_time):
    # cache_time is rounded to nearest hour for cache key
    return vendor_api.screen(address, chain)

def screen_with_cache(address, chain, cache_duration_hours=1):
    cache_time = datetime.utcnow().replace(
        minute=0, second=0, microsecond=0
    )
    return cached_vendor_screen(address, chain, cache_time)
```

## Testing and validation

### Test cases for screening logic

1. **Known sanctioned addresses** (from OFAC test data)
2. **Case variations** (uppercase, lowercase, mixed)
3. **Invalid addresses** (malformed, wrong chain)
4. **Edge cases** (empty strings, null values, special characters)
5. **Performance tests** (large batch screening)

### Validation against official sources

Periodically validate your parsed data against official sources:
```python
def validate_ofac_parse():
    # Download fresh OFAC data
    official_data = download_ofac_sdn()
    
    # Parse with your parser
    parsed_addresses = parse_digital_currency_addresses(official_data)
    
    # Manually verify a sample
    sample = random.sample(parsed_addresses, min(10, len(parsed_addresses)))
    
    for addr in sample:
        # Check against OFAC search tool
        official_result = query_ofac_search_tool(addr['address'])
        assert official_result['found'], f"Address {addr} not found in official search"
```

## Compliance documentation

### What to document

1. **Source selection rationale** - Why you chose specific sources
2. **Update procedures** - How often, who's responsible, escalation
3. **Matching logic** - Exact match, fuzzy match, thresholds
4. **Risk scoring methodology** - How scores are calculated
5. **Action thresholds** - What score triggers what action
6. **Exception handling** - How false positives are resolved
7. **Audit procedures** - How decisions are reviewed
8. **Training records** - Who's trained on the system

### Sample policy excerpt

```
Sanctions Screening Policy - Section 3.2: Address Screening

3.2.1 Primary Source
The Company uses OFAC SDN "Digital Currency Address" fields as the 
primary authoritative source for sanctioned blockchain addresses.

3.2.2 Update Frequency
OFAC SDN data is downloaded and parsed every 6 hours. Each download
is verified via SHA-256 hash and stored immutably in the compliance
data warehouse.

3.2.3 Matching Logic
Address matching uses exact-match logic after chain-aware canonicalization:
- EVM addresses: converted to lowercase
- Bitcoin bech32: converted to lowercase
- Bitcoin base58: case-preserved

3.2.4 Action Thresholds
- Exact match to OFAC address: BLOCK + immediate compliance case
- Vendor risk score ≥80: HOLD + manual review within 4 hours
- Vendor risk score 50-79: ALLOW + enhanced monitoring
- Vendor risk score <50: ALLOW + standard monitoring

3.2.5 Audit Trail
All screening decisions are logged with:
- Timestamp (UTC)
- Subject address and chain
- List version hash
- Match result and risk score
- Action taken
- Reviewer (if applicable)

Logs are retained for 7 years and are immutable.
```

## Further reading

- [OFAC Sanctions List Search](https://sanctionslist.ofac.treas.gov/)
- [OFAC Compliance Resources](https://ofac.treasury.gov/compliance)
- [FATF Virtual Assets Guidance](https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Guidance-rba-virtual-assets-2021.html)
- [UK Sanctions Guidance](https://www.gov.uk/government/collections/uk-sanctions-guidance)
- [EU Sanctions Map](https://www.sanctionsmap.eu/)
