# Define all scrapers and their configurations
SCRAPERS = {
    # Daily scrapers update existing items
    "belfield_daily": {
        "file_name": "Belfield.xlsx", 
        "script_name": "Belfield_Daily_Modified.py",
        "description": "Belfield Music Store (Daily)",
        "type": "daily"
    },
    "better_monthly": {
    "file_name": "Better.xlsx",
    "script_name": "Better_Monthly_Modified.py", 
    "description": "Better Music Store (Monthly)",
    "type": "monthly"
},
    "better_daily": {
    "file_name": "Better.xlsx",
    "script_name": "Better_Daily_Modified.py", 
    "description": "Better Music Store (Daily)",
    "type": "daily"
},
    "sky_music_daily": {
        "file_name": "Sky_Music.xlsx",
        "script_name": "Sky_Music_Daily_Modified.py", 
        "description": "Sky Music Store (Daily)",
        "type": "daily"
    },
    # Add other daily scrapers here

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
    # Add other monthly scrapers here
}

# Convenience dictionaries to get scrapers by type
DAILY_SCRAPERS = {k: v for k, v in SCRAPERS.items() if v["type"] == "daily"}
MONTHLY_SCRAPERS = {k: v for k, v in SCRAPERS.items() if v["type"] == "monthly"}
