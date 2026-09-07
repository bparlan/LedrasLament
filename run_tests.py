#!/usr/bin/env python3
"""Run the fal_generate.py tests from the project root."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tests.test_fal_generate import *
except ImportError:
    # Fallback: run tests file directly if tests/ is not a package
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))
    from test_fal_generate import *

print("✅ All tests imported successfully!")
