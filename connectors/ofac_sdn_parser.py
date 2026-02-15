#!/usr/bin/env python3
"""
OFAC SDN Advanced XML Parser

Extracts digital currency addresses from OFAC SDN Advanced XML.
"""

import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DigitalCurrencyAddress:
    uid: str
    ticker: str
    address: str
    entity_name: Optional[str] = None


OFAC_TICKER_TO_CHAIN = {
    'XBT': 'BTC',
    'BTC': 'BTC',
    'ETH': 'ETH',
    'TRX': 'TRX',
    'LTC': 'LTC',
    'XMR': 'XMR',
    'ZEC': 'ZEC',
    'DASH': 'DASH',
    'BSV': 'BSV',
    'BCH': 'BCH',
    'BTG': 'BTG',
    'ETC': 'ETC',
    'XVG': 'XVG',
    'USDT': 'USDT',
}


def parse_ofac_sdn_xml(xml_path: Path) -> List[DigitalCurrencyAddress]:
    """
    Parse OFAC SDN Advanced XML and extract digital currency addresses.
    
    Args:
        xml_path: Path to the XML file
    
    Returns:
        List of DigitalCurrencyAddress objects
    """
    print(f"Parsing {xml_path}...")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    addresses = []
    
    for entry in root.findall('.//sdnEntry'):
        uid = entry.find('uid')
        uid_text = uid.text if uid is not None else None
        
        # Try to get entity name
        first_name = entry.find('.//firstName')
        last_name = entry.find('.//lastName')
        entity_name_elem = entry.find('.//name')
        
        entity_name = None
        if first_name is not None and last_name is not None:
            entity_name = f"{first_name.text} {last_name.text}"
        elif entity_name_elem is not None:
            entity_name = entity_name_elem.text
        
        # Extract digital currency addresses
        for id_elem in entry.findall('.//id'):
            id_type = id_elem.find('idType')
            id_number = id_elem.find('idNumber')
            
            if id_type is None or id_number is None:
                continue
            
            id_type_text = id_type.text
            id_number_text = id_number.text
            
            if not id_type_text or not id_number_text:
                continue
            
            if id_type_text.startswith("Digital Currency Address"):
                # Extract ticker from "Digital Currency Address - XBT"
                parts = id_type_text.split(" - ")
                ticker = parts[1].strip() if len(parts) > 1 else "UNKNOWN"
                
                addresses.append(DigitalCurrencyAddress(
                    uid=uid_text or "UNKNOWN",
                    ticker=ticker,
                    address=id_number_text.strip(),
                    entity_name=entity_name
                ))
    
    print(f"Found {len(addresses)} digital currency addresses")
    
    return addresses


def export_by_chain(addresses: List[DigitalCurrencyAddress], output_dir: Path):
    """
    Export addresses grouped by chain.
    
    Args:
        addresses: List of addresses
        output_dir: Directory to save output files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Group by chain
    by_chain: Dict[str, List[str]] = {}
    
    for addr in addresses:
        chain = OFAC_TICKER_TO_CHAIN.get(addr.ticker, addr.ticker)
        if chain not in by_chain:
            by_chain[chain] = []
        by_chain[chain].append(addr.address)
    
    # Export each chain
    for chain, addrs in by_chain.items():
        # Remove duplicates
        unique_addrs = sorted(set(addrs))
        
        # JSON format
        json_path = output_dir / f"ofac_{chain.lower()}_addresses.json"
        with open(json_path, 'w') as f:
            json.dump(unique_addrs, f, indent=2)
        print(f"Exported {len(unique_addrs)} {chain} addresses to {json_path}")
        
        # TXT format (one per line)
        txt_path = output_dir / f"ofac_{chain.lower()}_addresses.txt"
        with open(txt_path, 'w') as f:
            f.write('\n'.join(unique_addrs))
        print(f"Exported {len(unique_addrs)} {chain} addresses to {txt_path}")
    
    # Export full details
    full_path = output_dir / "ofac_all_addresses_detailed.json"
    with open(full_path, 'w') as f:
        json.dump([
            {
                'uid': addr.uid,
                'ticker': addr.ticker,
                'chain': OFAC_TICKER_TO_CHAIN.get(addr.ticker, addr.ticker),
                'address': addr.address,
                'entity_name': addr.entity_name
            }
            for addr in addresses
        ], f, indent=2)
    print(f"Exported full details to {full_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ofac_sdn_parser.py <path_to_sdn_advanced.xml>")
        sys.exit(1)
    
    xml_path = Path(sys.argv[1])
    if not xml_path.exists():
        print(f"Error: File not found: {xml_path}", file=sys.stderr)
        sys.exit(1)
    
    addresses = parse_ofac_sdn_xml(xml_path)
    export_by_chain(addresses, Path("output"))
