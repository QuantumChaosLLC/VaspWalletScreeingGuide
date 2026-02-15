#!/usr/bin/env python3
"""
Address Screening Example

Demonstrates exact-match screening with chain-aware canonicalization.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Set, Tuple


class Chain(Enum):
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    ARBITRUM = "ARB"
    OPTIMISM = "OP"
    POLYGON = "MATIC"
    BSC = "BSC"
    TRON = "TRX"


@dataclass(frozen=True)
class ListVersion:
    source: str
    retrieved_at_utc: datetime
    sha256: str
    uri: str


@dataclass(frozen=True)
class ScreenResult:
    address: str
    chain: str
    match: bool
    risk_score: int
    reason: str
    list_version: Optional[ListVersion] = None


# Regex patterns
EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
BTC_BECH32_RE = re.compile(r"^(bc1|tb1|bcrt1)[a-z0-9]{20,90}$", re.IGNORECASE)
BTC_BASE58_RE = re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$")


def canonicalize(chain: str, address: str) -> str:
    """
    Canonicalize address by chain to reduce false positives.
    """
    a = address.strip()
    c = chain.upper().strip()

    if c in {"ETH", "EVM", "ARB", "BSC", "OP", "MATIC"}:
        # EVM addresses are case-insensitive; store lower-case
        return a.lower()

    if c in {"XBT", "BTC"}:
        # bech32 is case-insensitive; normalize to lower-case
        if a.lower().startswith(("bc1", "tb1", "bcrt1")):
            return a.lower()
        # base58 is case-sensitive by design; keep as-is
        return a

    # Default: conservative, no transformation beyond trimming
    return a


def syntactic_validate(chain: str, address: str) -> bool:
    """
    Validate address syntax for known chains.
    """
    c = chain.upper().strip()
    a = address.strip()

    if c in {"ETH", "EVM", "ARB", "BSC", "OP", "MATIC"}:
        return bool(EVM_RE.match(a))
    if c in {"XBT", "BTC"}:
        return bool(BTC_BECH32_RE.match(a.lower()) or BTC_BASE58_RE.match(a))
    return True  # unknown chains -> don't falsely reject


def screen_exact_match(
    chain: str,
    address: str,
    sanctioned_set: Set[Tuple[str, str]],
    list_version: ListVersion
) -> ScreenResult:
    """
    Deterministic screening: exact-match only.
    
    Args:
        chain: Blockchain identifier
        address: Address to screen
        sanctioned_set: Set of (chain, address) tuples
        list_version: Version metadata for the list
    
    Returns:
        ScreenResult with match status and risk score
    """
    if not syntactic_validate(chain, address):
        return ScreenResult(
            address=address,
            chain=chain,
            match=False,
            risk_score=0,
            reason="invalid_address_syntax",
            list_version=list_version,
        )

    addr_norm = canonicalize(chain, address)
    hit = (chain.upper(), addr_norm) in sanctioned_set

    if hit:
        # For authoritative address lists, treat as mandatory stop + case
        return ScreenResult(
            address=address,
            chain=chain,
            match=True,
            risk_score=100,
            reason="exact_match_authoritative_sanctions_address",
            list_version=list_version,
        )

    return ScreenResult(
        address=address,
        chain=chain,
        match=False,
        risk_score=0,
        reason="no_exact_match",
        list_version=list_version,
    )


def load_sanctioned_addresses(json_path: Path) -> Tuple[Set[Tuple[str, str]], ListVersion]:
    """
    Load sanctioned addresses from JSON file.
    
    Expected format:
    {
        "metadata": {
            "source": "OFAC_SDN",
            "retrieved_at_utc": "2026-02-15T00:00:00",
            "sha256": "abc123...",
            "uri": "https://..."
        },
        "addresses": [
            {"chain": "ETH", "address": "0x..."},
            {"chain": "BTC", "address": "bc1..."}
        ]
    }
    """
    with open(json_path) as f:
        data = json.load(f)
    
    metadata = data.get("metadata", {})
    list_version = ListVersion(
        source=metadata.get("source", "UNKNOWN"),
        retrieved_at_utc=datetime.fromisoformat(metadata.get("retrieved_at_utc", "2000-01-01T00:00:00")),
        sha256=metadata.get("sha256", ""),
        uri=metadata.get("uri", "")
    )
    
    sanctioned_set = set()
    for item in data.get("addresses", []):
        chain = item["chain"]
        address = item["address"]
        canonical = canonicalize(chain, address)
        sanctioned_set.add((chain.upper(), canonical))
    
    return sanctioned_set, list_version


def main():
    """
    Example usage.
    """
    # Example: Load from a JSON file
    # sanctioned_set, list_version = load_sanctioned_addresses(Path("sanctioned_addresses.json"))
    
    # For demo purposes, create a small test set
    list_version = ListVersion(
        source="DEMO",
        retrieved_at_utc=datetime.utcnow(),
        sha256="demo",
        uri="demo"
    )
    
    # Known sanctioned addresses (examples only - not real)
    sanctioned_set = {
        ("ETH", "0x7f367cc41522ce07553e823bf3be79a889debe1b"),  # Tornado Cash (real)
        ("BTC", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),  # Example
    }
    
    # Test cases
    test_cases = [
        ("ETH", "0x7f367cc41522ce07553e823bf3be79a889debe1b"),  # Should hit
        ("ETH", "0x7F367CC41522CE07553E823BF3BE79A889DEBE1B"),  # Should hit (case variation)
        ("ETH", "0x0000000000000000000000000000000000000000"),  # Should not hit
        ("BTC", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),  # Should hit
        ("BTC", "BC1QXY2KGDYGJRSQTZQ2N0YRF2493P83KKFJHX0WLH"),  # Should hit (case variation)
        ("ETH", "invalid"),  # Invalid syntax
    ]
    
    print("Screening Test Results")
    print("=" * 80)
    
    for chain, address in test_cases:
        result = screen_exact_match(chain, address, sanctioned_set, list_version)
        
        status = "🚫 BLOCKED" if result.match else "✅ ALLOWED"
        print(f"\n{status}")
        print(f"  Chain: {result.chain}")
        print(f"  Address: {result.address}")
        print(f"  Risk Score: {result.risk_score}")
        print(f"  Reason: {result.reason}")


if __name__ == "__main__":
    main()
