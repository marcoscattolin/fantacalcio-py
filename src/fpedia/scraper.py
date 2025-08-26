# data_retriever.py
"""
This module handles scraping data from FPEDIA website.
"""

import os
import time
from random import randint
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from loguru import logger
from dotenv import load_dotenv
import pandas as pd
import concurrent.futures

from src.fpedia import config

load_dotenv()


@dataclass
class PlayerAttributes:
    """Data class for player attributes."""
    nome: str
    punteggio: str
    ruolo: str
    squadra: str
    fantamedia_anni: Dict[str, str]
    stats_ultimo_anno: Dict[str, str]
    stats_previste: Dict[str, str]
    skills: List[str]
    buon_investimento: str
    resistenza_infortuni: str
    consigliato_prossima_giornata: bool
    nuovo_acquisto: bool
    infortunato: bool
    trend: str
    presenze_campionato_corrente: str


class Scraper:
    """Handles scraping operations from FPEDIA website."""
    
    def __init__(self, max_workers: int = config.MAX_WORKERS):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.session.verify = False
     
    def _extract_fantamedia(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract fantamedia data for different years."""
        selettore = "div.col_one_fourth:nth-of-type(n+2) div"
        elements = soup.select(selettore)
        
        fantamedia_data = {}
        for element in elements:
            try:
                media = element.find("span").text.strip()
                anno = element.find("strong").text.split(" ")[-1].strip()
                fantamedia_data[f"Fantamedia anno {anno}"] = media
            except (AttributeError, IndexError):
                continue
        
        return fantamedia_data
    
    def _extract_stats(self, soup: BeautifulSoup, selettore: str) -> Dict[str, str]:
        """Extract statistics data from a specific selector."""
        stats_element = soup.select_one(selettore)
        if not stats_element:
            return {}
        
        parametri = [
            el.text.strip().replace(":", "") 
            for el in stats_element.find_all("strong")
        ]
        valori = [
            el.text.strip() 
            for el in stats_element.find_all("span")
        ]
        
        return dict(zip(parametri, valori))
    
    def _extract_boolean(self, soup: BeautifulSoup, selettore: str, 
                                 title_contains: str, default: bool = False) -> bool:
        """Extract boolean attribute based on title content."""
        try:
            element = soup.select_one(selettore)
            if element and element.get("title"):
                return title_contains in element.get("title")
        except (AttributeError, IndexError):
            pass
        return default
    
    def _extract_trend(self, soup: BeautifulSoup) -> str:
        """Extract trend information."""
        selettore = "div.col_one_fourth:nth-of-type(n+2) div"
        try:
            trend_element = soup.select(selettore)[0].find("i")
            if trend_element and trend_element.get("class"):
                trend_class = trend_element.get("class")[1]
                if trend_class == "icon-arrow-up":
                    return "UP"
                elif trend_class == "icon-arrow-down":
                    return "DOWN"
        except (AttributeError, IndexError):
            pass
        return "STABLE"
    
    def _get_role_urls(self, ruolo: str) -> List[str]:
        """Get player URLs for a specific role."""
        url = f"{config.FPEDIA_URL}{ruolo.lower()}/"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            urls = []
            for giocatore in soup.find_all("article"):
                calciatore_url = giocatore.find("a")
                if calciatore_url and calciatore_url.get("href"):
                    urls.append(calciatore_url.get("href"))
            
            return urls
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve URLs for role '{ruolo}': {e}")
            return []
   
    def _get_player_urls(self) -> List[str]:
        """Scrape all player URLs from FPEDIA."""
        if os.path.exists(config.GIOCATORI_URLS):
            logger.debug("Reading player URLs from cache.")
            with open(config.GIOCATORI_URLS, "r", encoding="utf-8") as fp:
                return [url.strip() for url in fp.readlines()]
        
        logger.debug("Scraping player URLs from FPEDIA...")
        all_urls = []
        
        for ruolo in tqdm(config.RUOLI, desc="Scraping roles"):
            urls = self._get_role_urls(ruolo)
            all_urls.extend(urls)
        
        if not all_urls:
            logger.warning(
                "No player URLs were scraped from FPEDIA. "
                "The website structure may have changed, or the request was blocked."
            )
            return []
        
        # Save URLs to cache
        os.makedirs(os.path.dirname(config.GIOCATORI_URLS), exist_ok=True)
        with open(config.GIOCATORI_URLS, "w", encoding="utf-8") as fp:
            for url in all_urls:
                fp.write(f"{url}\n")
        
        logger.debug(f"{len(all_urls)} player URLs saved.")
        return all_urls

    def _scrape_attributes(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape attributes for a single player."""
        logger.debug(f"Scraping attributes for player from URL: {url}")
        
        # Random delay to be respectful to the server
        time.sleep(randint(1000, 8000) / 1000)
        
        try:
            response = self.session.get(url.strip())
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract basic information
            nome = soup.select_one("h1")
            if not nome:
                logger.warning(f"Could not find player name for URL: {url}")
                return None
            
            nome = nome.get_text().strip()
            
            # Extract score
            punteggio_element = soup.select_one("div.col_one_fourth:nth-of-type(1) span.stickdan")
            punteggio = punteggio_element.text.strip().replace("/100", "") if punteggio_element else "0"
            
            # Extract fantamedia
            fantamedia_anni = self._extract_fantamedia(soup)
            
            # Extract last year stats
            stats_ultimo_anno = self._extract_stats(
                soup, "div.col_one_third:nth-of-type(2) div"
            )
            
            # Extract predicted stats
            stats_previste = self._extract_stats(
                soup, ".col_one_third.col_last div"
            )
            
            # Extract role
            ruolo_element = soup.select_one(".label12 span.label")
            ruolo = ruolo_element.get_text().strip() if ruolo_element else "Unknown"
            
            # Extract skills
            skills_elements = soup.select("span.stickdanpic")
            skills = [el.text for el in skills_elements if el.text]
            
            # Extract investment percentages
            progress_elements = soup.select("div.progress-percent")
            buon_investimento = "0"
            resistenza_infortuni = "0"
            
            if len(progress_elements) >= 4:
                buon_investimento = progress_elements[2].text.replace("%", "")
                resistenza_infortuni = progress_elements[3].text.replace("%", "")
            
            # Extract boolean attributes
            consigliato = self._extract_boolean(
                soup, "img.inf_calc", "Consigliato per la giornata"
            )
            
            nuovo_acquisto = bool(soup.select_one("span.new_calc"))
            
            infortunato = self._extract_boolean(
                soup, "img.inf_calc", "Infortunato"
            )
            
            # Extract team
            squadra_element = soup.select_one(
                "#content > div > div.section.nobg.nomargin > div > div > div:nth-child(2) > div.col_three_fifth > div.promo.promo-border.promo-light.row > div:nth-child(3) > div:nth-child(1) > div > img"
            )
            squadra = "Unknown"
            if squadra_element and squadra_element.get("title"):
                squadra = squadra_element.get("title").split(":")[1].strip()
            
            # Extract trend
            trend = self._extract_trend(soup)
            
            # Extract current season appearances
            presenze_element = soup.select_one("div.col_one_fourth:nth-of-type(2) span.rouge")
            presenze_campionato_corrente = presenze_element.text if presenze_element else "0"
            
            # Build attributes dictionary
            attributi = {
                "Nome": nome,
                "Punteggio": punteggio,
                "Ruolo": ruolo,
                "Squadra": squadra,
                "Presenze campionato corrente": presenze_campionato_corrente,
                "Buon investimento": buon_investimento,
                "Resistenza infortuni": resistenza_infortuni,
                "Consigliato prossima giornata": consigliato,
                "Nuovo acquisto": nuovo_acquisto,
                "Infortunato": infortunato,
                "Trend": trend,
                "Skills": skills,
                "URL": url,
            }
            
            # Add fantamedia data
            attributi.update(fantamedia_anni)
            
            # Add stats data
            attributi.update(stats_ultimo_anno)
            attributi.update(stats_previste)
            
            return attributi
            
        except Exception as e:
            logger.error(f"Error scraping player attributes from {url}: {e}")
            return None
    
    def _scrape_players(self) -> List[Dict[str, Any]]:
        """Scrape attributes for all players."""
        urls = self._get_player_urls()
        if not urls:
            return []
        
        giocatori = []
        logger.debug("Scraping individual player data from website...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._scrape_attributes, url): url 
                for url in urls
            }
            
            for future in tqdm(
                concurrent.futures.as_completed(future_to_url), 
                total=len(urls),
                desc="Scraping players"
            ):
                url = future_to_url[future]
                try:
                    attributi = future.result()
                    if attributi:
                        giocatori.append(attributi)
                except Exception as exc:
                    logger.error(f"{url} generated an exception: {exc}")
        
        return giocatori


    def scrape(self) -> None:
            """
            Fetches all player URLs and then scrapes each player's page for their attributes.
            Saves the data to a CSV file.
            """
            if os.path.exists(config.GIOCATORI_CSV):
                logger.debug(f"{config.GIOCATORI_CSV} already exists. Skipping scraping.")
                return
            
            giocatori = self._scrape_players()
            
            if giocatori:
                # Ensure output directory exists
                os.makedirs(os.path.dirname(config.GIOCATORI_CSV), exist_ok=True)
                
                df = pd.DataFrame(giocatori)
                df.to_csv(config.GIOCATORI_CSV, index=False)
                logger.debug(f"FPEDIA data saved to CSV: {len(giocatori)} players")
            else:
                logger.warning("No player data was scraped from FPEDIA.")
    
    

if __name__ == "__main__":
    # Example usage
    scraper = Scraper()
    scraper.scrape()