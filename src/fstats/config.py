# config.py
import os
import base64

from src.commons import config

def decode(stringa):
    return base64.b64decode(stringa).decode("utf-8")


# FSTATS
PLAYERS_CSV = os.path.join(config.TEMP_DIR, "fstats", "players.csv")
PROCESSED_PLAYERS_PARQUET = os.path.join(config.TEMP_DIR, "fstats", "players_processed.parquet")

# constants
ANNO_CORRENTE = 2025
FSTATS_ANNO = 2024
BASEURL_FSTATS = decode("aHR0cHM6Ly9hcGkuYXBwLmZhbnRhZ29hdC5pdC9hcGk=")
FSTATS_LOGIN_URL = f"{BASEURL_FSTATS}/account/login/"
FSTATS_PLAYERS_URL = f"{BASEURL_FSTATS}/v1/zona/player/?page_size=1000&page=1&season={str(FSTATS_ANNO)}%2F{str(FSTATS_ANNO+1)[-2:]}&ordering="

# output of pipeline
FSTATS_EXCEL = os.path.join(config.OUTPUT_DIR, "fstats.xlsx")

