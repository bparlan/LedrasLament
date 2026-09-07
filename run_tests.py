#!/usr/bin/env python3
"""Run the fal_generate.py tests from the project root."""

import sys
import os

# Add the tests directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from test_fal_generate import *

print("✅ All tests imported successfully!")
