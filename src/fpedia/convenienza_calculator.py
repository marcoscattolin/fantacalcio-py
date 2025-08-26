# convenienza_calculator.py
"""
Convenienza Calculator for FPEDIA data analysis.
Calculates convenience indices for football players.
"""

import ast
import pandas as pd
from loguru import logger
from src.fpedia import config


class ConvenienzaCalculator:
    """Calculator for player convenience indices."""
    
    # Skills values
    SKILLS_VALUES = {
        "Fuoriclasse": 1, "Titolare": 3, "Buona Media": 2, "Goleador": 4,
        "Assistman": 2, "Piazzati": 2, "Rigorista": 5, "Giovane talento": 2,
        "Panchinaro": -4, "Falloso": -2, "Outsider": 2,
    }
    SEASON_MATCHES = 38
    
    def __init__(self):
        self.current_year = config.ANNO_CORRENTE
        self.prev_year = self.current_year - 1
        self.prev_prev_year = self.current_year - 2

    def _get_skills_bonus(self, skills_str: str) -> int:
        """Calculate bonus from player skills."""
        try:
            skills = ast.literal_eval(skills_str)
            return sum(self.SKILLS_VALUES.get(skill, 0) for skill in skills) if isinstance(skills, list) else 0
        except:
            return 0

    def _calculate_base_score(self, row: pd.Series, max_appearances: int) -> float:
        """Calculate base convenience score."""
        # Get data
        prev_avg = row.get(f"Fantamedia anno {self.prev_prev_year}-{self.prev_year}", 0)
        prev_matches = row.get("Partite giocate", 0)
        curr_avg = row.get(f"Fantamedia anno {self.prev_year}-{self.current_year}", 0)
        curr_appearances = row.get("Presenze campionato corrente", 0)
        score = row.get("Punteggio", 1)
        
        # Calculate base value
        base = 0.0
        
        # Previous season (20% weight)
        if prev_matches > 0:
            base += prev_avg * (prev_matches / self.SEASON_MATCHES) * 0.2
        
        # Current season (80% weight if enough data)
        if curr_appearances > 5:
            base += curr_avg * (curr_appearances / max_appearances) * 0.8
        elif prev_matches > 0:
            base = prev_avg * (prev_matches / self.SEASON_MATCHES)
        
        # Apply score multiplier and normalize
        base = base * score * 0.3
        base = (base / (score or 1)) * 100 / 40
        
        return base

    def _apply_modifiers(self, row: pd.Series, base_score: float) -> float:
        """Apply additional modifiers to base score."""
        final_score = base_score
        
        # Skills bonus
        final_score += self._get_skills_bonus(row.get("Skills", "[]"))
        
        # Status modifiers
        if row.get("Nuovo acquisto", False):
            final_score -= 2
        if row.get("Buon investimento", 0) == 60:
            final_score += 3
        if row.get("Consigliato prossima giornata", False):
            final_score += 1
        if row.get("Trend", "") == "UP":
            final_score += 2
        if row.get("Infortunato", False):
            final_score -= 1
        
        # Injury resistance
        resistance = row.get("Resistenza infortuni", 0)
        if resistance > 60:
            final_score += 4
        elif resistance == 60:
            final_score += 2
        
        return final_score

    def calculate_convenienza(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate both convenience indices."""
        if df.empty:
            logger.warning("DataFrame is empty, calculation skipped.")
            return df
        
        df_calc = df.copy()
        
        # Get max appearances for normalization
        max_appearances = df_calc["Presenze campionato corrente"].max() or 1
        
        # Calculate Convenienza
        convenienza = []
        for _, row in df_calc.iterrows():
            base = self._calculate_base_score(row, max_appearances)
            final = self._apply_modifiers(row, base)
            convenienza.append(final)
        
        df["Convenienza"] = convenienza
        
        # Calculate Convenienza Potenziale
        potenziale = []
        for _, row in df_calc.iterrows():
            score = row.get("Punteggio", 0)
            skills_bonus = self._get_skills_bonus(row.get("Skills", "[]")) * 2
            potenziale.append(score + skills_bonus)
        
        df["Convenienza Potenziale"] = potenziale
        
        logger.debug("Convenience indices calculated.")
        return df

    def save_excel(self, df: pd.DataFrame, sort_by: str = "Convenienza Potenziale"):
        """Save results to Excel with selected columns."""
        # Sort by potential convenience
        df_sorted = df.sort_values(by=sort_by, ascending=False)
        
        # Define output columns (no duplicates)
        output_columns = [
            "Nome", "Ruolo", "Squadra",
            "Convenienza Potenziale", "Convenienza", "Punteggio",
            f"Fantamedia anno {self.prev_year}-{self.current_year}",
            "Presenze campionato corrente",
            f"Fantamedia anno {self.prev_prev_year}-{self.prev_year}",
            "Partite giocate",
            "Trend", "Skills", "Consigliato prossima giornata",
            "Buon investimento", "Resistenza infortuni", "Infortunato",
            f"FM su tot gare {self.prev_year}-{self.current_year}",
            "Presenze previste", "Gol previsti", "Assist previsti",
            "Nuovo acquisto"
        ]
        
        # Filter to existing columns only
        available_columns = [col for col in output_columns if col in df_sorted.columns]
        
        # Save to Excel
        df_sorted[available_columns].to_excel(config.FPEDIA_EXCEL, index=False)
        logger.info(f"Results saved to {config.FPEDIA_EXCEL}, shape: {df_sorted.shape}")

