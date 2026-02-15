# VASP Sanctions Screening

## Credit
This guide was developed in collaboration with the team at [ttexchange.io](https://ttexchange.io). TT Exchange is a crypto / USDT on ramp service built for Trinidad and Tobago. They are VASP regulated in T&T ensuring safe compliant access to crypto markets.

A comprehensive guide and toolkit for Virtual Asset Service Providers (VASPs) to implement cryptocurrency wallet sanctions screening.

## Quick Links

- [Main README](README.md) - Overview and quick start
- [Sources Documentation](docs/sources.md) - Detailed source information
- [Normalization Guide](docs/normalization.md) - Address canonicalization rules
- [Governance Framework](docs/governance.md) - Controls and case workflow

## Repository Structure

```
.
├── README.md                    # Main documentation
├── LICENSE                      # MIT License
├── docs/
│   ├── sources.md              # Deep dive on authoritative sources
│   ├── normalization.md        # Chain-specific canonicalization
│   └── governance.md           # Controls, audits, case workflow
├── connectors/
│   ├── ofac_sdn_downloader.py  # Download OFAC SDN XML
│   ├── ofac_sdn_parser.py      # Parse digital currency addresses
│   ├── uk_sanctions_downloader.py
│   ├── un_consolidated_downloader.py
│   └── eu_fsf_notes.md         # EU FSF access guidance
├── examples/
│   ├── screen_address.py       # Working Python example
│   └── screen_transaction_pseudocode.txt
└── .github/
    └── workflows/
        └── update_lists.yml    # Automated list updates
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/vasp-sanctions-screening.git
cd vasp-sanctions-screening
```

### 2. Install dependencies

```bash
pip install requests
```

### 3. Download sanctions lists

```bash
# Download OFAC SDN
python connectors/ofac_sdn_downloader.py

# Parse digital currency addresses
python connectors/ofac_sdn_parser.py data/ofac_sdn_advanced_*.xml

# Download other lists
python connectors/un_consolidated_downloader.py
python connectors/uk_sanctions_downloader.py
```

### 4. Run screening example

```bash
python examples/screen_address.py
```

## Key Features

- **Authoritative sources** - Direct integration with OFAC, UN, EU, UK, Canada
- **Chain-aware** - Proper handling of Bitcoin, Ethereum, and other blockchains
- **Production-ready** - Includes versioning, integrity checks, audit trails
- **Compliance-focused** - Governance framework and case management
- **Open source** - MIT licensed, community contributions welcome

## Use Cases

- **Onboarding screening** - Check new customer addresses
- **Transaction screening** - Pre-transaction risk assessment
- **Continuous monitoring** - Detect retroactive designations
- **Compliance reporting** - Generate regulatory reports

## Important Disclaimers

⚠️ **Not legal advice** - Consult qualified legal counsel for your jurisdiction

⚠️ **Not exhaustive** - OFAC explicitly states published addresses are not exhaustive

⚠️ **Requires governance** - Technical tools alone are insufficient for compliance

## Contributing

Contributions are welcome! Please:
- Ensure sources are verifiable and authoritative
- Include provenance information
- Follow existing documentation structure
- Test code examples before submitting

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/vasp-sanctions-screening/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/vasp-sanctions-screening/discussions)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

This project was created to help VASPs implement effective sanctions screening programs. It is based on extensive research of authoritative sources and industry best practices.

---

**Maintained by the community** | **Not affiliated with any government agency**
