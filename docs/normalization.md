# Address Normalization and Canonicalization

Proper address normalization is critical to avoid false negatives (missing sanctioned addresses due to formatting differences) and false positives (flagging legitimate addresses due to comparison errors).

## Core principle

**Never compare addresses across different blockchains.** Always include chain context in your data model.

## Data model

```python
from dataclasses import dataclass
from enum import Enum

class Chain(Enum):
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    ARBITRUM = "ARB"
    OPTIMISM = "OP"
    POLYGON = "MATIC"
    BSC = "BSC"
    TRON = "TRX"
    LITECOIN = "LTC"
    MONERO = "XMR"
    ZCASH = "ZEC"

@dataclass(frozen=True)
class Address:
    chain: Chain
    address: str
    
    def __post_init__(self):
        # Validate and canonicalize on construction
        object.__setattr__(self, 'address', canonicalize(self.chain, self.address))
```

## Bitcoin address normalization

### Bitcoin address types

1. **Legacy (P2PKH)** - Starts with `1`, base58-encoded
2. **Script (P2SH)** - Starts with `3`, base58-encoded
3. **SegWit (bech32)** - Starts with `bc1`, bech32-encoded
4. **Testnet** - Starts with `m`, `n`, `2`, or `tb1`

### Case sensitivity

- **Base58 (legacy/script):** Case-sensitive by design. Do NOT convert case.
- **Bech32 (SegWit):** Case-insensitive. Normalize to lowercase.

### Canonicalization rules

```python
import re

BTC_BECH32_RE = re.compile(r"^(bc1|tb1|bcrt1)[a-z0-9]{20,90}$", re.IGNORECASE)
BTC_BASE58_RE = re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$")

def canonicalize_bitcoin(address: str) -> str:
    addr = address.strip()
    
    # Bech32: normalize to lowercase
    if BTC_BECH32_RE.match(addr):
        return addr.lower()
    
    # Base58: preserve case
    if BTC_BASE58_RE.match(addr):
        return addr
    
    raise ValueError(f"Invalid Bitcoin address: {address}")
```

### Validation

For production systems, use a proper Bitcoin address validation library:

```python
from bitcoin import b58check_to_hex, bech32_decode

def validate_bitcoin_address(address: str) -> bool:
    try:
        if address.lower().startswith('bc1'):
            # Bech32
            hrp, data = bech32_decode(address)
            return hrp == 'bc' and data is not None
        else:
            # Base58
            b58check_to_hex(address)
            return True
    except:
        return False
```

## Ethereum and EVM chain normalization

### EVM address format

All EVM-compatible chains (Ethereum, Arbitrum, Optimism, Polygon, BSC, etc.) use the same address format:
- 20 bytes (40 hex characters)
- Prefixed with `0x`
- Hexadecimal encoding

### Case sensitivity and EIP-55

EVM addresses are **case-insensitive** for comparison purposes, but EIP-55 defines a **checksum encoding** using mixed case.

Example:
- `0x5aAeb6053f3E94C9b9A09f33669435E7Ef1BeAed` (checksummed)
- `0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed` (lowercase)
- `0x5AAEB6053F3E94C9B9A09F33669435E7EF1BEAED` (uppercase)

All three represent the same address.

### Canonicalization rules

**Recommendation:** Normalize to lowercase for storage and comparison.

```python
import re

EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

def canonicalize_evm(address: str) -> str:
    addr = address.strip()
    
    if not EVM_RE.match(addr):
        raise ValueError(f"Invalid EVM address: {address}")
    
    return addr.lower()
```

### EIP-55 checksum validation (optional)

If you want to validate checksummed addresses:

```python
from eth_utils import is_checksum_address, to_checksum_address

def validate_evm_checksum(address: str) -> bool:
    """
    Returns True if address is valid and properly checksummed.
    """
    if not EVM_RE.match(address):
        return False
    
    # If all lowercase or all uppercase, it's not checksummed
    if address == address.lower() or address == address.upper():
        return True  # Valid but not checksummed
    
    # Check if checksum is correct
    return is_checksum_address(address)
```

### Chain-specific considerations

Even though addresses have the same format across EVM chains, **the same address on different chains represents different accounts**:

- `0xABC...` on Ethereum mainnet
- `0xABC...` on Arbitrum
- `0xABC...` on Polygon

These are **different accounts** and must be tracked separately.

```python
# WRONG: Comparing addresses without chain context
if address in sanctioned_addresses:
    block()

# CORRECT: Chain-aware comparison
if (chain, address) in sanctioned_addresses:
    block()
```

## Tron address normalization

### Tron address format

Tron uses base58check encoding similar to Bitcoin, but with different prefixes:
- Mainnet addresses start with `T`
- Testnet addresses start with `t` (lowercase)

### Case sensitivity

Tron addresses are case-sensitive. Do NOT convert case.

### Canonicalization rules

```python
TRON_RE = re.compile(r"^T[a-km-zA-HJ-NP-Z1-9]{33}$")

def canonicalize_tron(address: str) -> str:
    addr = address.strip()
    
    if not TRON_RE.match(addr):
        raise ValueError(f"Invalid Tron address: {address}")
    
    return addr  # Preserve case
```

## Monero address normalization

### Monero address format

Monero uses base58 encoding with:
- Standard addresses: 95 characters, start with `4`
- Integrated addresses: 106 characters, start with `4`
- Subaddresses: 95 characters, start with `8`

### Case sensitivity

Monero addresses are case-sensitive. Do NOT convert case.

### Canonicalization rules

```python
MONERO_STANDARD_RE = re.compile(r"^4[0-9A-Za-z]{94}$")
MONERO_SUBADDRESS_RE = re.compile(r"^8[0-9A-Za-z]{94}$")

def canonicalize_monero(address: str) -> str:
    addr = address.strip()
    
    if not (MONERO_STANDARD_RE.match(addr) or MONERO_SUBADDRESS_RE.match(addr)):
        raise ValueError(f"Invalid Monero address: {address}")
    
    return addr  # Preserve case
```

## Litecoin address normalization

### Litecoin address format

Similar to Bitcoin:
- Legacy: Starts with `L`, base58-encoded
- Script: Starts with `M` or `3`, base58-encoded
- SegWit: Starts with `ltc1`, bech32-encoded

### Canonicalization rules

```python
LTC_BECH32_RE = re.compile(r"^ltc1[a-z0-9]{20,90}$", re.IGNORECASE)
LTC_BASE58_RE = re.compile(r"^[LM3][a-km-zA-HJ-NP-Z1-9]{25,34}$")

def canonicalize_litecoin(address: str) -> str:
    addr = address.strip()
    
    # Bech32: normalize to lowercase
    if LTC_BECH32_RE.match(addr):
        return addr.lower()
    
    # Base58: preserve case
    if LTC_BASE58_RE.match(addr):
        return addr
    
    raise ValueError(f"Invalid Litecoin address: {address}")
```

## Unified canonicalization function

```python
from typing import Union

def canonicalize(chain: Union[Chain, str], address: str) -> str:
    """
    Canonicalize an address according to chain-specific rules.
    
    Args:
        chain: Chain enum or string identifier
        address: Raw address string
    
    Returns:
        Canonicalized address string
    
    Raises:
        ValueError: If address is invalid for the specified chain
    """
    if isinstance(chain, str):
        chain = Chain(chain.upper())
    
    address = address.strip()
    
    if chain in {Chain.BITCOIN}:
        return canonicalize_bitcoin(address)
    
    elif chain in {Chain.ETHEREUM, Chain.ARBITRUM, Chain.OPTIMISM, 
                   Chain.POLYGON, Chain.BSC}:
        return canonicalize_evm(address)
    
    elif chain == Chain.TRON:
        return canonicalize_tron(address)
    
    elif chain == Chain.MONERO:
        return canonicalize_monero(address)
    
    elif chain == Chain.LITECOIN:
        return canonicalize_litecoin(address)
    
    else:
        # For unknown chains, preserve as-is but trim whitespace
        return address
```

## Handling OFAC ticker mappings

OFAC uses specific ticker symbols in its "Digital Currency Address - {TICKER}" fields. Map these to your internal chain identifiers:

```python
OFAC_TICKER_TO_CHAIN = {
    'XBT': Chain.BITCOIN,
    'BTC': Chain.BITCOIN,
    'ETH': Chain.ETHEREUM,
    'TRX': Chain.TRON,
    'LTC': Chain.LITECOIN,
    'XMR': Chain.MONERO,
    'ZEC': Chain.ZCASH,
    'DASH': Chain.DASH,
    'BSV': Chain.BITCOIN_SV,
    'BCH': Chain.BITCOIN_CASH,
    'BTG': Chain.BITCOIN_GOLD,
    'ETC': Chain.ETHEREUM_CLASSIC,
    'XVG': Chain.VERGE,
    'USDT': Chain.ETHEREUM,  # Tether can be on multiple chains; context needed
}

def parse_ofac_address(id_type: str, id_number: str):
    """
    Parse OFAC "Digital Currency Address - {TICKER}" field.
    
    Example:
        id_type = "Digital Currency Address - XBT"
        id_number = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    """
    if not id_type.startswith("Digital Currency Address"):
        return None
    
    parts = id_type.split(" - ")
    if len(parts) < 2:
        return None
    
    ticker = parts[1].strip()
    chain = OFAC_TICKER_TO_CHAIN.get(ticker)
    
    if chain is None:
        # Unknown ticker; log for manual review
        return None
    
    try:
        canonical_address = canonicalize(chain, id_number)
        return Address(chain=chain, address=canonical_address)
    except ValueError:
        # Invalid address; log for manual review
        return None
```

## Handling multi-chain tokens (e.g., USDT)

Some tokens exist on multiple chains. OFAC's ticker alone may not specify which chain.

**Problem:**
```
Digital Currency Address - USDT
0x1234...
```

Is this USDT on Ethereum, Tron, or another chain?

**Solution:**
1. Check address format to infer chain:
   - `0x...` (40 hex chars) → Ethereum or EVM chain
   - `T...` (base58) → Tron

2. If ambiguous, create entries for all possible chains and flag for manual review.

```python
def parse_multi_chain_token(ticker: str, address: str):
    """
    Handle tokens that exist on multiple chains.
    """
    if ticker == 'USDT':
        # Try to infer chain from address format
        if EVM_RE.match(address):
            # Could be Ethereum, BSC, Polygon, etc.
            # Create entries for all EVM chains where USDT exists
            return [
                Address(chain=Chain.ETHEREUM, address=canonicalize_evm(address)),
                Address(chain=Chain.BSC, address=canonicalize_evm(address)),
                Address(chain=Chain.POLYGON, address=canonicalize_evm(address)),
            ]
        elif TRON_RE.match(address):
            return [Address(chain=Chain.TRON, address=canonicalize_tron(address))]
    
    return []
```

## Testing normalization logic

```python
import unittest

class TestNormalization(unittest.TestCase):
    
    def test_evm_lowercase(self):
        addr = "0x5aAeb6053f3E94C9b9A09f33669435E7Ef1BeAed"
        expected = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        self.assertEqual(canonicalize_evm(addr), expected)
    
    def test_evm_already_lowercase(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        self.assertEqual(canonicalize_evm(addr), addr)
    
    def test_bitcoin_bech32_lowercase(self):
        addr = "BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4"
        expected = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
        self.assertEqual(canonicalize_bitcoin(addr), expected)
    
    def test_bitcoin_base58_preserve_case(self):
        addr = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        self.assertEqual(canonicalize_bitcoin(addr), addr)
    
    def test_invalid_evm_address(self):
        with self.assertRaises(ValueError):
            canonicalize_evm("0xINVALID")
    
    def test_chain_aware_comparison(self):
        addr = "0x1234567890123456789012345678901234567890"
        eth_addr = Address(chain=Chain.ETHEREUM, address=addr)
        arb_addr = Address(chain=Chain.ARBITRUM, address=addr)
        
        # Same address string, different chains
        self.assertNotEqual(eth_addr, arb_addr)

if __name__ == '__main__':
    unittest.main()
```

## Common pitfalls

### Pitfall 1: Comparing addresses without chain context

```python
# WRONG
sanctioned = {'0xabc...', '0xdef...'}
if user_address in sanctioned:
    block()

# CORRECT
sanctioned = {
    (Chain.ETHEREUM, '0xabc...'),
    (Chain.ARBITRUM, '0xdef...'),
}
if (user_chain, user_address) in sanctioned:
    block()
```

### Pitfall 2: Inconsistent case handling

```python
# WRONG: Storing mixed case, comparing lowercase
sanctioned = {'0xABC...'}  # Mixed case
if user_address.lower() in sanctioned:  # Comparing lowercase
    block()  # Will never match!

# CORRECT: Canonicalize on storage
sanctioned = {canonicalize_evm('0xABC...')}  # Stored as lowercase
if canonicalize_evm(user_address) in sanctioned:
    block()
```

### Pitfall 3: Not trimming whitespace

```python
# WRONG
address = "  0xabc...  "
if address in sanctioned:  # Won't match due to whitespace
    block()

# CORRECT
address = address.strip()
if address in sanctioned:
    block()
```

### Pitfall 4: Assuming all addresses are lowercase

```python
# WRONG: Bitcoin base58 is case-sensitive
bitcoin_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
if bitcoin_address.lower() in sanctioned:  # Will never match!
    block()

# CORRECT: Use chain-aware canonicalization
if canonicalize_bitcoin(bitcoin_address) in sanctioned:
    block()
```

## Performance optimization

### Pre-compute canonical forms

```python
# When loading sanctioned addresses
sanctioned_addresses = set()
for raw_chain, raw_address in load_from_ofac():
    try:
        canonical = canonicalize(raw_chain, raw_address)
        sanctioned_addresses.add((raw_chain, canonical))
    except ValueError as e:
        log_error(f"Invalid address in OFAC data: {raw_address} ({e})")

# When screening
def screen(chain, address):
    try:
        canonical = canonicalize(chain, address)
        return (chain, canonical) in sanctioned_addresses
    except ValueError:
        return False  # Invalid address format
```

### Use hash-based lookups

Python's `set` and `dict` provide O(1) average-case lookup:

```python
# Fast: O(1) average case
if (chain, address) in sanctioned_set:
    block()

# Slow: O(n)
if (chain, address) in sanctioned_list:
    block()
```

## Summary

| Chain | Case handling | Validation |
|---|---|---|
| Bitcoin (bech32) | Lowercase | Regex + bech32 decode |
| Bitcoin (base58) | Preserve | Regex + base58check |
| Ethereum/EVM | Lowercase | Regex + optional EIP-55 |
| Tron | Preserve | Regex + base58check |
| Monero | Preserve | Regex |
| Litecoin (bech32) | Lowercase | Regex + bech32 decode |
| Litecoin (base58) | Preserve | Regex + base58check |

**Golden rule:** Always canonicalize addresses using chain-specific rules before storage and comparison.
