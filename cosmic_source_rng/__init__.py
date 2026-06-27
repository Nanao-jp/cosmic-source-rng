"""
Cosmic-Source-RNG: True random number generator using NASA solar activity data and local CPU jitter.
"""
from .cosmic import get_cosmic_value, get_cosmic_value_with_details
from .local import get_local_jitter
from .engine import generate_cosmic_random

__version__ = "0.1.0"

# Convenience alias
generate_random = generate_cosmic_random

__all__ = [
    'get_cosmic_value',
    'get_cosmic_value_with_details',
    'get_local_jitter',
    'generate_cosmic_random',
    'generate_random',
    '__version__',
]

