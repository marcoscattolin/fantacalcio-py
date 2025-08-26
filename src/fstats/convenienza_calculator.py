# convenienza_calculator.py
"""
Convenienza Calculator for FSTATS data analysis.
Calculates convenience indices for football players.
"""

import pandas as pd
from loguru import logger
from src.fstats import config


class ConvenienzaCalculator:
    """Calculator for player convenience indices."""
    
    # Scoring weights
    GOAL_WEIGHT = 3
    ASSIST_WEIGHT = 1
    YELLOW_CARD_WEIGHT = 0.5
    RED_CARD_WEIGHT = 1
    XG_XA_WEIGHT = 2
    
    # Convenience calculation weights
    FANTA_AVG_WEIGHT = 0.6
    BONUS_WEIGHT = 0.25
    POTENTIAL_WEIGHT = 0.15
    MALUS_WEIGHT = 0.2
    
    def __init__(self):
        self.current_year = config.ANNO_CORRENTE
        self.fstats_year = config.FSTATS_ANNO

    def _calculate_bonus_score(self, goals: pd.Series, assists: pd.Series) -> pd.Series:
        """Calculate bonus score from goals and assists."""
        return (goals * self.GOAL_WEIGHT) + (assists * self.ASSIST_WEIGHT)

    def _calculate_malus_score(self, yellow_cards: pd.Series, red_cards: pd.Series) -> pd.Series:
        """Calculate malus score from cards."""
        return (yellow_cards * self.YELLOW_CARD_WEIGHT) + (red_cards * self.RED_CARD_WEIGHT)

    def _calculate_potential_score(self, xg: pd.Series, xa: pd.Series, presences: pd.Series) -> pd.Series:
        """Calculate potential score from xG and xA per presence."""
        return (xg + xa) / presences

    def _calculate_convenienza(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Convenienza index based on presences and performance."""
        df_result = df.copy()
        
        # Filter players with presences
        df_con_presenze = df[df["presences"] > 0].reset_index(drop=True)
        
        if df_con_presenze.empty:
            df_result["Convenienza"] = 0
            logger.warning("Nessun giocatore con presenze in FSTATS. 'Convenienza' impostata a 0.")
            return df_result
        
        # Calculate scores
        bonus_score = self._calculate_bonus_score(
            df_con_presenze["goals"], 
            df_con_presenze["assists"]
        )
        malus_score = self._calculate_malus_score(
            df_con_presenze["yellowCards"], 
            df_con_presenze["redCards"]
        )
        
        # Calculate per-presence scores
        bonus_per_presence = bonus_score / df_con_presenze["presences"]
        malus_per_presence = malus_score / df_con_presenze["presences"]
        potential_score = self._calculate_potential_score(
            df_con_presenze["xgFromOpenPlays"],
            df_con_presenze["xA"],
            df_con_presenze["presences"]
        )
        
        # Calculate final convenience score
        convenienza = (
            df_con_presenze["fanta_avg"] * self.FANTA_AVG_WEIGHT +
            bonus_per_presence * self.BONUS_WEIGHT +
            potential_score * self.POTENTIAL_WEIGHT -
            malus_per_presence * self.MALUS_WEIGHT
        )
        
        # Normalize to 0-100 scale
        if not convenienza.empty:
            df_con_presenze["Convenienza"] = (convenienza / convenienza.max()) * 100
        else:
            df_con_presenze["Convenienza"] = 0
        
        # Merge back to original dataframe
        df_result = df_result.merge(
            df_con_presenze[["Nome", "Convenienza"]], 
            on="Nome", 
            how="left"
        )
        
        logger.debug("Indice 'Convenienza' calcolato per FSTATS.")
        return df_result

    def _calculate_convenienza_potenziale(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Convenienza Potenziale index independent of presences."""
        df_result = df.copy()
        
        # Calculate potential stats (weighted xG + xA)
        potential_stats = (
            df_result["xgFromOpenPlays"] + df_result["xA"]
        ) * self.XG_XA_WEIGHT
        
        # Calculate potential convenience
        potenziale = df_result["fantacalcioFantaindex"] + potential_stats
        
        # Normalize to 0-100 scale
        if not potenziale.empty:
            df_result["Convenienza Potenziale"] = (potenziale / potenziale.max()) * 100
        else:
            df_result["Convenienza Potenziale"] = 0
        
        logger.debug("Indice 'Convenienza Potenziale' calcolato per FSTATS.")
        return df_result

    def calculate_convenienza(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate both convenience indices."""
        if df.empty:
            logger.warning("DataFrame FSTATS è vuoto. Calcolo saltato.")
            return df
        
        df_calc = df.copy()

        # Calculate Convenienza (presence-based)
        df_result = self._calculate_convenienza(df_calc)
        
        # Calculate Convenienza Potenziale (potential-based)
        df_result = self._calculate_convenienza_potenziale(df_result)
        
        # Fill missing values
        df_result.fillna({"Convenienza": 0, "Convenienza Potenziale": 0}, inplace=True)
        
        return df_result

    def save_excel(self, df: pd.DataFrame, sort_by: str = "Convenienza Potenziale"):
        
        """Save results to Excel with selected columns."""
        
        # Sort by potential convenience
        df_sorted = df.sort_values(by=sort_by, ascending=False)
        
        # Define output columns in logical groups
        output_columns = [
            # Essential Info
            "Nome", "Ruolo", "Squadra",
            # Calculated Indices
            "Convenienza Potenziale", "Convenienza", "fantacalcioFantaindex",
            # Performance Metrics
            "fanta_avg", "avg", "presences", "appearances", "matchesInStart", "mins_played",
            # Core Statistics
            "goals", "assists", "goals90min", "goalsFromOpenPlays", "xA", "xA90min",
            # Expected Goals
            "xgFromOpenPlays", "xgFromOpenPlays/90min",
            # Disciplinary & Status
            "yellowCards", "redCards", "injured", "banned", "successfulPenalties", "penalties",
            # Goalkeeper Stats
            "gkPenaltiesSaved", "gkCleanSheets", "gkConcededGoals", "openPlaysGoalsConceded", "openPlaysXgConceded",
            # Advanced Metrics
            "fantamediaPred", "expectedFantamediaMean", "perc_matchesStarted", "percMinsPlayed",
            # Position & Identity
            "mantra_position", "fantacalcio_position", "birth_date", "foot_name", "fantacalcioPlayerId", "fantacalcioTeamName",
            # Performance Indices
            "External_breakout_Index", "Shot_on_goal_Index", "Offensive_actions_Index", "Pass_forward_accuracy_Index",
            "Air_challenge_offensive_Index", "Cross_accuracy_Index", "Converge_in_the_center_Index",
            "Accompany_the_offensive_action_Index", "Offensive_verticalization_Index", "Received_pass_Index",
            "Attacking_area_Index", "Offensive_field_presence_Index", "Pass_accuracy_Index", "Pass_leading_chances_Index",
            "Deep_runs_Index", "Defense_solidity_Index", "Set_piece_attack_Index", "Shot_on_target_Index", "Dribbles_successful_Index"
        ]
        
        # Filter to existing columns only
        selected_columns = [col for col in output_columns if col in df_sorted.columns]
        
        # Save to Excel
        df_sorted[selected_columns].to_excel(config.FSTATS_EXCEL, index=False)
        logger.info(f"Results saved to {config.FSTATS_EXCEL}, shape: {df_sorted.shape}")
