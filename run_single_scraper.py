#!/usr/bin/env python
import sys
import subprocess
from scrapers_config import SCRAPERS

if len(sys.argv) < 2:
    print("Usage: run_single_scraper.py <scraper_name>")
    sys.exit(1)

scraper_name = sys.argv[1]

if scraper_name not in SCRAPERS:
    print(f"Error: Scraper '{scraper_name}' not found in config")
    print(f"Available scrapers: {', '.join(SCRAPERS.keys())}")
    sys.exit(1)

# Get the script name from config
script_file = SCRAPERS[scraper_name]["script_name"]
description = SCRAPERS[scraper_name]["description"]

print(f"Running {description} ({script_file})")

# Run the scraper script with the scraper name as argument
result = subprocess.run([sys.executable, script_file, scraper_name])
sys.exit(result.returncode)
