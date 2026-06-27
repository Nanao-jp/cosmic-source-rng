# Cosmic-Source-RNG

[![PyPI version](https://badge.fury.io/py/cosmic-source-rng.svg)](https://badge.fury.io/py/cosmic-source-rng)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**True random number generator using NASA solar activity data and local CPU jitter.**

Unlike traditional pseudo-random number generators (PRNGs), Cosmic-Source-RNG generates truly unpredictable random numbers based on verifiable physical phenomena from space weather events.

## Features

- **Cosmic Entropy**: Real-time solar activity data from NASA's DONKI API (CMEs, solar flares, geomagnetic storms)
- **Local Jitter**: Nanosecond-level CPU timing measurements
- **Verifiable Physics**: Based on measurable physical facts, not black-box algorithms
- **Collision-Free Design**: Nanosecond timestamps ensure near-zero collision probability
- **Transparent Process**: Full calculation details available for audit

## Installation

```bash
pip install cosmic-source-rng
```

## Quick Start

### As a Library

```python
from cosmic_source_rng import generate_random

# Generate a random hash
result = generate_random()
print(result['hash'])  # SHA256 hash string
print(result['cosmic_val'])  # Cosmic entropy value
print(result['jitter'])  # CPU jitter in nanoseconds
```

### As an API Server

```bash
# Install with server dependencies
pip install cosmic-source-rng[server]

# Set NASA API key (optional, DEMO_KEY works with rate limits)
export NASA_API_KEY=your_api_key

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then access:
- API docs: http://localhost:8000/docs
- Generate random: http://localhost:8000/generate

## How It Works

### Algorithm Overview

1. **Cosmic Data Acquisition**: Fetches solar activity data from NASA DONKI API
2. **Constant Selection**: Uses π (Pi) if cosmic value is even, e (Euler's number) if odd
3. **Local Jitter Measurement**: Measures CPU execution time jitter at nanosecond precision
4. **Nanosecond Timestamp**: Incorporates `time.time_ns()` for uniqueness
5. **Hash Generation**: Combines all entropy sources into SHA256 hash

### Entropy Sources

| Source | Description |
|--------|-------------|
| Cosmic | NASA solar activity data (CME IDs, timestamps, locations) |
| Quantum | CPU execution time jitter (nanosecond fluctuations) |
| Temporal | Nanosecond-precision UNIX timestamps |
| System | Memory usage percentage |

## API Response

```json
{
  "hash": "a1b2c3d4e5f6...",
  "constant_used": "Pi",
  "cosmic_val": 12345678901234567890,
  "jitter": 1234567,
  "memory_percent": 45.2,
  "process_details": {
    "timestamp_ns": 1704067200000000000,
    "nasa_data_summary": [
      "/CME:activityID:2024-01-15T12:00:00-CME-001",
      "CME:startTime:2024-01-15T12:00:00"
    ]
  }
}
```

## Use Cases

- **Cryptography**: Key generation, token generation, salt creation
- **Gaming**: Gacha systems, procedural generation, matchmaking
- **Web3/NFT**: Provably fair minting, on-chain randomness
- **Research**: Monte Carlo simulations, statistical sampling

## Commercial API

A hosted version is available on RapidAPI:
https://rapidapi.com/Nanaojp/api/cosmic-source-rng

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NASA_API_KEY` | NASA API key for DONKI API | `DEMO_KEY` |

Get your NASA API key at: https://api.nasa.gov/

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<details>
<summary>日本語 / Japanese</summary>

## 概要

Cosmic-Source-RNGは、NASAの太陽活動データとローカル環境のCPUジッターを組み合わせて、予測不可能な真の乱数を生成するライブラリです。

## インストール

```bash
pip install cosmic-source-rng
```

## 使い方

```python
from cosmic_source_rng import generate_random

result = generate_random()
print(result['hash'])
```

詳細は英語版READMEを参照してください。

</details>
