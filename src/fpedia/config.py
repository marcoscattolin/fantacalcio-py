from src.commons import config
import os



# FPEDIA
BASEURL_FPEDIA = config.decode("aHR0cHM6Ly93d3cuZmFudGFjYWxjaW9wZWRpYS5jb20=")
FPEDIA_URL = f"{BASEURL_FPEDIA}/lista-calciatori-serie-a/"
MAX_WORKERS = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
RUOLI = ["Portieri", "Difensori", "Centrocampisti", "Attaccanti"]

ANNO_CORRENTE = 2025

# output of scraper
GIOCATORI_CSV = os.path.join(config.TEMP_DIR, "fpedia", "giocatori.csv")
GIOCATORI_URLS = os.path.join(config.TEMP_DIR, "fpedia", "giocatori_urls.txt")

# output of data_proc
PROCESSED_GIOCATORI_PARQUET = os.path.join(config.TEMP_DIR, "fpedia", "giocatori_processed.parquet")

# output of pipeline
FPEDIA_EXCEL = os.path.join(config.OUTPUT_DIR, "fpedia.xlsx")
