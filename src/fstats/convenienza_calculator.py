# convenienza_calculator.py
import pandas as pd
from loguru import logger


def calcola_convenienza(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola due indici di convenienza per i dati di FSTATS:
    1. 'Convenienza': basata sulle performance stagionali (presenze, fantamedia).
    2. 'Convenienza Potenziale': basata sul valore intrinseco (fantacalcioFantaindex) e potenziale
       statistico (xG, xA), utile soprattutto a inizio campionato.
    """
    if df.empty:
        logger.warning("DataFrame FSTATS è vuoto. Calcolo saltato.")
        return df

    df_calc = df.copy()
    numeric_cols = [
        "goals",
        "assists",
        "yellowCards",
        "redCards",
        "xgFromOpenPlays",
        "xA",
        "presences",
        "fanta_avg",
        "fantacalcioFantaindex",
    ]
    for col in numeric_cols:
        df_calc[col] = pd.to_numeric(df_calc[col], errors="coerce").fillna(0)

    # --- Calcolo Convenienza (basata su presenze) ---
    df_con_presenze = df_calc[df_calc["presences"] > 0].reset_index(drop=True)
    if not df_con_presenze.empty:
        bonus_score = (df_con_presenze["goals"] * 3) + (df_con_presenze["assists"] * 1)
        malus_score = (df_con_presenze["yellowCards"] * 0.5) + (
            df_con_presenze["redCards"] * 1
        )
        bonus_per_presence = bonus_score / df_con_presenze["presences"]
        malus_per_presence = malus_score / df_con_presenze["presences"]
        potential_score = (
            df_con_presenze["xgFromOpenPlays"] + df_con_presenze["xA"]
        ) / df_con_presenze["presences"]

        convenienza = (
            df_con_presenze["fanta_avg"] * 0.6
            + bonus_per_presence * 0.25
            + potential_score * 0.15
            - malus_per_presence * 0.2
        )
        df_con_presenze["Convenienza"] = (
            (convenienza / convenienza.max()) * 100 if not convenienza.empty else 0
        )
        df = df.merge(df_con_presenze[["Nome", "Convenienza"]], on="Nome", how="left")
        logger.debug("Indice 'Convenienza' calcolato per FSTATS.")
    else:
        df["Convenienza"] = 0
        logger.warning(
            "Nessun giocatore con presenze in FSTATS. 'Convenienza' impostata a 0."
        )

    # --- Calcolo Convenienza Potenziale (indipendente da presenze) ---
    potential_stats = (
        df_calc["xgFromOpenPlays"] + df_calc["xA"]
    ) * 2  # Pondera il potenziale xG/xA
    potenziale = df_calc["fantacalcioFantaindex"] + potential_stats

    df_calc["Convenienza Potenziale"] = (
        (potenziale / potenziale.max()) * 100 if not potenziale.empty else 0
    )
    df = df.merge(df_calc[["Nome", "Convenienza Potenziale"]], on="Nome", how="left")
    logger.debug("Indice 'Convenienza Potenziale' calcolato per FSTATS.")

    df.fillna({"Convenienza": 0, "Convenienza Potenziale": 0}, inplace=True)
    return df
