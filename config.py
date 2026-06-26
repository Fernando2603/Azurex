from pathlib import Path

ROOT = Path(__file__).parent
LINK = "https://raw.githubusercontent.com/Fernando2603/AzurLane/main"
VERSION = "5.1.7"
"""
MAJOR: json key deleted
MINOR: json key added without deletion (backward compatible)
PATCH: bug fix, misc, etc.
"""

# Linker
LINKER_SOURCE = ROOT / "AzurAssets"
LINKER_TARGET = ROOT / "AzurLane"
LINKER_EXTRACT = ROOT / "ClientExtract"

# parser
PARSER_ROOT = ROOT / "AzurLane"

# debug
DEBUG_RUNTIME = True
DEBUG_VERBOSE = False
