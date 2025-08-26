# convenienza_calculator.py
"""
Convenienza Calculator for FPEDIA data analysis.

This module calculates convenience indices for football players based on their
performance data, skills, and various other factors.
"""

import ast
from typing import List, Dict, Any, Optional
import pandas as pd
from loguru import logger
from src.fpedia import config


class ConvenienzaCalculator:
    """
    Calculator for player convenience indices based on FPEDIA data.
    
    This class provides methods to calculate two main convenience indices:
    1. Convenienza: Based on seasonal performance (appearances, fantasy average)
    2. Convenienza Potenziale: Based on intrinsic player value (Score, Skills)
    """
    
    # Skills mapping with their corresponding values
    SKILLS_MAPPING = {
        "Fuoriclasse": 1,
        "Titolare": 3,
        "Buona Media": 2,
        "Goleador": 4,
        "Assistman": 2,
        "Piazzati": 2,
        "Rigorista": 5,
        "Giovane talento": 2,
        "Panchinaro": -4,
        "Falloso": -2,
        "Outsider": 2,
    }
    
    # Configuration constants
    SEASON_MATCHES = 38
    MIN_CURRENT_APPEARANCES = 5
    WEIGHTS = {
        "previous_performance": 0.20,
        "current_performance": 0.80,
        "score_multiplier": 0.30,
        "score_normalization": 40,
        "skills_potential_multiplier": 2,
    }
    
    # Bonus/penalty values
    BONUS_PENALTIES = {
        "new_purchase": -2,
        "good_investment": 3,
        "recommended_next_match": 1,
        "trend_up": 2,
        "injured": -1,
        "injury_resistance_high": 4,
        "injury_resistance_medium": 2,
    }
    
    # Column names for better maintainability
    COLUMNS = {
        "previous_fantasy_avg": "Fantamedia anno {}-{}",
        "previous_matches": "Partite giocate",
        "current_fantasy_avg": "Fantamedia anno {}-{}",
        "current_appearances": "Presenze campionato corrente",
        "score": "Punteggio",
        "good_investment": "Buon investimento",
        "injury_resistance": "Resistenza infortuni",
        "skills": "Skills",
        "new_purchase": "Nuovo acquisto",
        "recommended_next_match": "Consigliato prossima giornata",
        "trend": "Trend",
        "injured": "Infortunato",
    }

    def __init__(self):
        """Initialize the calculator with current year configuration."""
        self.current_year = config.ANNO_CORRENTE
        self.previous_year = self.current_year - 1
        self.two_years_ago = self.current_year - 2

    def _calculate_skills_bonus(self, skills_str: str) -> int:
        """Calculate bonus points based on player skills."""
        try:
            skills_list = ast.literal_eval(skills_str)
            if isinstance(skills_list, list):
                return sum(self.SKILLS_MAPPING.get(skill, 0) for skill in skills_list)
        except (ValueError, SyntaxError) as e:
            logger.debug(f"Errore nel parsing delle skills: {e}")
        return 0

    def _calculate_base_appetibilita(self, row: pd.Series, max_appearances: int) -> float:
        """Calculate base appetibility based on performance data."""
        previous_fantasy_avg = row.get(
            f"Fantamedia anno {self.two_years_ago}-{self.previous_year}", 0
        )
        previous_matches = row.get(self.COLUMNS["previous_matches"], 0)
        current_fantasy_avg = row.get(
            f"Fantamedia anno {self.previous_year}-{self.current_year}", 0
        )
        current_appearances = row.get(self.COLUMNS["current_appearances"], 0)
        score = row.get(self.COLUMNS["score"], 1)

        appetibilita = 0.0

        # Previous season contribution
        if previous_matches > 0:
            previous_weight = (previous_matches / self.SEASON_MATCHES) * self.WEIGHTS["previous_performance"]
            appetibilita += previous_fantasy_avg * previous_weight

        # Current season contribution
        if current_appearances > self.MIN_CURRENT_APPEARANCES:
            current_weight = (current_appearances / max_appearances) * self.WEIGHTS["current_performance"]
            appetibilita += current_fantasy_avg * current_weight
        elif previous_matches > 0:
            # Fallback to previous season if current season has insufficient data
            appetibilita = previous_fantasy_avg * (previous_matches / self.SEASON_MATCHES)

        # Apply score multiplier and normalization
        appetibilita *= score * self.WEIGHTS["score_multiplier"]
        score_normalizer = score if score != 0 else 1
        appetibilita = (appetibilita / score_normalizer) * 100 / self.WEIGHTS["score_normalization"]

        return appetibilita

    def _apply_additional_modifiers(self, row: pd.Series, appetibilita: float) -> float:
        """Apply additional modifiers based on player status and attributes."""
        modified_appetibilita = appetibilita

        # Skills bonus
        skills_bonus = self._calculate_skills_bonus(row.get(self.COLUMNS["skills"], "[]"))
        modified_appetibilita += skills_bonus

        # Status-based modifiers
        if row.get(self.COLUMNS["new_purchase"], False):
            modified_appetibilita += self.BONUS_PENALTIES["new_purchase"]
        
        if row.get(self.COLUMNS["good_investment"], 0) == 60:
            modified_appetibilita += self.BONUS_PENALTIES["good_investment"]
        
        if row.get(self.COLUMNS["recommended_next_match"], False):
            modified_appetibilita += self.BONUS_PENALTIES["recommended_next_match"]
        
        if row.get(self.COLUMNS["trend"], "") == "UP":
            modified_appetibilita += self.BONUS_PENALTIES["trend_up"]
        
        if row.get(self.COLUMNS["injured"], False):
            modified_appetibilita += self.BONUS_PENALTIES["injured"]
        
        # Injury resistance bonus
        injury_resistance = row.get(self.COLUMNS["injury_resistance"], 0)
        if injury_resistance > 60:
            modified_appetibilita += self.BONUS_PENALTIES["injury_resistance_high"]
        elif injury_resistance == 60:
            modified_appetibilita += self.BONUS_PENALTIES["injury_resistance_medium"]

        return modified_appetibilita

    def _calculate_potential_convenienza(self, row: pd.Series) -> float:
        """Calculate potential convenience based on intrinsic player value."""
        potential = row.get(self.COLUMNS["score"], 0)
        
        # Skills contribution (weighted more heavily for potential)
        skills_bonus = self._calculate_skills_bonus(row.get(self.COLUMNS["skills"], "[]"))
        potential += skills_bonus * self.WEIGHTS["skills_potential_multiplier"]
        
        return potential

    def calculate_convenienza(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate convenience indices for FPEDIA data.
        
        Args:
            df: DataFrame containing player data from FPEDIA
            
        Returns:
            DataFrame with added 'Convenienza' and 'Convenienza Potenziale' columns
            
        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        df_calc = df.copy()

        # Calculate max appearances for normalization
        max_appearances = df_calc[self.COLUMNS["current_appearances"]].max()
        if max_appearances == 0:
            max_appearances = 1

        # Calculate Convenienza (based on appearances)
        convenienza_results = []
        for _, row in df_calc.iterrows():
            base_appetibilita = self._calculate_base_appetibilita(row, max_appearances)
            final_appetibilita = self._apply_additional_modifiers(row, base_appetibilita)
            convenienza_results.append(final_appetibilita)

        df["Convenienza"] = convenienza_results
        logger.debug("Indice 'Convenienza' calcolato per FPEDIA.")

        # Calculate Convenienza Potenziale (independent of appearances)
        potenziale_results = []
        for _, row in df_calc.iterrows():
            potential = self._calculate_potential_convenienza(row)
            potenziale_results.append(potential)

        df["Convenienza Potenziale"] = potenziale_results
        logger.debug("Indice 'Convenienza Potenziale' calcolato per FPEDIA.")

        return df

    
    def save_excel(self, df: pd.DataFrame):

        df = df.sort_values(by="Convenienza Potenziale", ascending=False)

        output_columns = [
            # Key Info
            "Nome",
            "Ruolo",
            "Squadra",
            # Calculated Indexes
            "Convenienza Potenziale",
            "Convenienza",
            "Punteggio",
            # Current Season Stats
            f"Fantamedia anno {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}",
            f"Presenze campionato corrente",
            # Previous Season Stats
            f"Fantamedia anno {config.ANNO_CORRENTE-2}-{config.ANNO_CORRENTE-1}",
            "Partite giocate",
            # Qualitative Info
            "Trend",
            "Skills",
            "Consigliato prossima giornata",
            "Buon investimento",
            "Resistenza infortuni",
            "Infortunato",
            # Legacy
            f"FM su tot gare {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}",
            "Presenze previste",
            "Gol previsti",
            "Assist previsti",
            "Ruolo",
            "Skills",
            "Buon investimento",
            "Resistenza infortuni",
            "Consigliato prossima giornata",
            "Nuovo acquisto",
            "Infortunato",
            "Squadra",
            "Trend",
            "Presenze campionato corrente",
        ]

        selected_columns = [col for col in output_columns if col in df.columns]
        df[selected_columns].to_excel(config.FPEDIA_EXCEL, index=False)
        logger.info(f"Results saved to {config.FPEDIA_EXCEL}, shape: {df.shape}")

