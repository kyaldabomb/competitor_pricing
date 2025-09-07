# Define all scrapers and their configurations
SCRAPERS = {
    # Daily scrapers update existing items
    "belfield_daily": {
        "file_name": "Belfield.xlsx", 
        "script_name": "Belfield_Daily_Modified.py",
        "description": "Belfield Music Store (Daily)",
        "type": "daily"
    },
    "better_daily": {
        "file_name": "Better.xlsx",
        "script_name": "Better_Daily_Modified.py", 
        "description": "Better Music Store (Daily)",
        "type": "daily"
    },
    "apw_daily": {
        "file_name": "APW.xlsx",
        "script_name": "APW_Daily_Modified.py", 
        "description": "Australian Piano Warehouse (Daily)",
        "type": "daily"
    },
    "sky_music_daily": {
        "file_name": "Sky_Music.xlsx",
        "script_name": "Sky_Music_Daily_Modified.py", 
        "description": "Sky Music Store (Daily)",
        "type": "daily"
    },
    "mannys_daily": {
        "file_name": "Mannys.xlsx",
        "script_name": "Mannys_Daily_Modified.py", 
        "description": "Mannys Music Store (Daily)",
        "type": "daily"
    },
    
    # Monthly scrapers find new items
    "belfield_monthly": {
        "file_name": "Belfield.xlsx", 
        "script_name": "Belfield_Monthly_Modified.py",
        "description": "Belfield Music Store (Monthly)",
        "type": "monthly"
    },
    "better_monthly": {
        "file_name": "Better.xlsx",
        "script_name": "Better_Monthly_Modified.py", 
        "description": "Better Music Store (Monthly)",
        "type": "monthly"
    },
    "apw_monthly": {
        "file_name": "APW.xlsx",
        "script_name": "APW_Monthly_Modified.py",
        "description": "Australian Piano Warehouse (Monthly)",
        "type": "monthly"
    },
    "sky_music_monthly": {
        "file_name": "Sky_Music.xlsx",
        "script_name": "Sky_Music_Monthly_Modified.py", 
        "description": "Sky Music Store (Monthly)",
        "type": "monthly"
    },
    "mannys_monthly": {
        "file_name": "Mannys.xlsx",
        "script_name": "Mannys_Monthly_Modified.py", 
        "description": "Mannys Music Store (Monthly)",
        "type": "monthly"
    },
}

# Convenience dictionaries to get scrapers by type
DAILY_SCRAPERS = {k: v for k, v in SCRAPERS.items() if v["type"] == "daily"}
MONTHLY_SCRAPERS = {k: v for k, v in SCRAPERS.items() if v["type"] == "monthly"}

# Chunked scrapers configuration (for scrapers that take too long)
# These scrapers will be split into chunks when run with --chunk flag
CHUNKED_SCRAPERS = {
    "belfield_monthly": {
        "pages_per_chunk": 500,    # How many pages per chunk
        "max_pages_total": 1000,   # Maximum total pages to scrape
        "chunk_only": False        # If True, only run in chunk mode; if False, can run normally too
    },
    # Uncomment and configure these if they also need chunking:
    # "mannys_monthly": {
    #     "pages_per_chunk": 500,
    #     "max_pages_total": 1000,
    #     "chunk_only": False
    # },
    # "sky_music_monthly": {
    #     "pages_per_chunk": 300,
    #     "max_pages_total": 600,
    #     "chunk_only": False
    # },
    # "apw_monthly": {
    #     "pages_per_chunk": 400,
    #     "max_pages_total": 800,
    #     "chunk_only": False
    # },
    # "better_monthly": {
    #     "pages_per_chunk": 500,
    #     "max_pages_total": 1000,
    #     "chunk_only": False
    # },
}
