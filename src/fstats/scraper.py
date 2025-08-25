# data_retriever.py
"""
This module handles scraping data from FSTATS API.
"""

import os
from typing import Dict, List, Optional, Any

import requests
from loguru import logger
from dotenv import load_dotenv
import pandas as pd

from src import config

load_dotenv()



class Scraper:
    """Handles data retrieval from FSTATS API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.token = None
    
    def _get_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """Get FSTATS credentials from environment variables."""
        user = os.getenv("FSTATS_MAIL")
        password = os.getenv("FSTATS_PASSWORD")
        
        if not user or not password:
            logger.error("FSTATS credentials not found in .env file.")
            return None, None
        
        return user, password
    
    def _login(self) -> bool:
        """Login to FSTATS and get access token."""
        user, password = self._get_credentials()
        if not user or not password:
            return False
        
        logger.debug("Logging into FSTATS...")
        login_payload = {"username": user, "password": password}
        headers = {"content-type": "application/json"}
        
        try:
            response = self.session.post(
                config.FSTATS_LOGIN_URL, 
                json=login_payload, 
                headers=headers
            )
            response.raise_for_status()
            self.token = response.json()["access_token"]
            logger.debug("Login successful.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"FSTATS login failed: {e}")
            return False
    
    def _scrape_player(self) -> Optional[List[Dict[str, Any]]]:
        """Scrape player data from FSTATS API."""
        if not self.token:
            logger.error("Not logged in to FSTATS. Please login first.")
            return None
        
        logger.debug("Scraping player data from FSTATS API...")
        auth_headers = {"authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(
                config.FSTATS_PLAYERS_URL, 
                headers=auth_headers
            )
            response.raise_for_status()
            players_data = response.json()["results"]
            logger.debug("FSTATS data scraped successfully.")
            return players_data
        except requests.exceptions.RequestException as e:
            logger.error(f"FSTATS data scrape failed: {e}")
            return None

    def scrape(self) -> None:
        """
        Logs into FSTATS, fetches player data from the API,
        and saves it to a CSV file.
        """
        if os.path.exists(config.PLAYERS_CSV):
            logger.debug(f"{config.PLAYERS_CSV} already exists. Skipping scraping.")
            return
        
        if not self._login():
            return
        
        players_data = self._scrape_player()
        
        if players_data:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(config.PLAYERS_CSV), exist_ok=True)
            
            df = pd.DataFrame(players_data)
            df.to_csv(config.PLAYERS_CSV, index=False, sep=";")
            logger.debug(f"FSTATS data saved to CSV: {len(players_data)} players")
        else:
            logger.warning("No player data was scraped from FSTATS.")
    


if __name__ == "__main__":
    # Example usage
    scraper = Scraper()
    scraper.scrape()