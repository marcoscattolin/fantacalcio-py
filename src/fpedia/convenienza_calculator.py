# convenienza_calculator.py
import pandas as pd
import ast
from loguru import logger
from src import config

# --- Funzioni per FPEDIA ---

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


def calcola_convenienza(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola due indici di convenienza per i dati di FPEDIA:
    1. 'Convenienza': basata sulle performance stagionali (presenze, fantamedia).
    2. 'Convenienza Potenziale': basata sul valore intrinseco del giocatore (Punteggio, Skills),
       utile soprattutto a inizio campionato o con poche presenze.
    """
    if df.empty:
        logger.warning("DataFrame FPEDIA è vuoto. Calcolo saltato.")
        return df

    # --- Calcolo Convenienza (basata su presenze) ---
    res_convenienza = []
    df_calc = df.copy()

    numeric_cols = [
        f"Fantamedia anno {config.ANNO_CORRENTE-2}-{config.ANNO_CORRENTE-1}",
        "Partite giocate",
        f"Fantamedia anno {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}",
        "Presenze campionato corrente",
        "Punteggio",
        "Buon investimento",
        "Resistenza infortuni",
    ]
    for col in numeric_cols:
        df_calc[col] = pd.to_numeric(df_calc[col], errors="coerce").fillna(0)

    giocatemax = df_calc["Presenze campionato corrente"].max()
    if giocatemax == 0:
        giocatemax = 1

    for _, row in df_calc.iterrows():
        appetibilita = 0
        fantamedia_prec = row.get(
            f"Fantamedia anno {config.ANNO_CORRENTE-2}-{config.ANNO_CORRENTE-1}", 0
        )
        partite_prec = row.get("Partite giocate", 0)
        fantamedia_corr = row.get(
            f"Fantamedia anno {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}", 0
        )
        partite_corr = row.get("Presenze campionato corrente", 0)
        punteggio = row.get("Punteggio", 1)

        if partite_prec > 0:
            appetibilita += fantamedia_prec * (partite_prec / 38) * 0.20
        if partite_corr > 5:
            appetibilita += fantamedia_corr * (partite_corr / giocatemax) * 0.80
        elif partite_prec > 0:
            appetibilita = fantamedia_prec * (partite_prec / 38)

        appetibilita = appetibilita * punteggio * 0.30
        pt = punteggio if punteggio != 0 else 1
        appetibilita = (appetibilita / pt) * 100 / 40

        try:
            skills_list = ast.literal_eval(row.get("Skills", "[]"))
            plus = sum(SKILLS_MAPPING.get(skill, 0) for skill in skills_list)
            appetibilita += plus
        except (ValueError, SyntaxError):
            pass

        if row.get("Nuovo acquisto", False):
            appetibilita -= 2
        if row.get("Buon investimento", 0) == 60:
            appetibilita += 3
        if row.get("Consigliato prossima giornata", False):
            appetibilita += 1
        if row.get("Trend", "") == "UP":
            appetibilita += 2
        if row.get("Infortunato", False):
            appetibilita -= 1
        if row.get("Resistenza infortuni", 0) > 60:
            appetibilita += 4
        elif row.get("Resistenza infortuni", 0) == 60:
            appetibilita += 2

        res_convenienza.append(appetibilita)

    df["Convenienza"] = res_convenienza
    logger.debug("Indice 'Convenienza' calcolato per FPEDIA.")

    # --- Calcolo Convenienza Potenziale (indipendente da presenze) ---
    res_potenziale = []
    for _, row in df_calc.iterrows():
        potenziale = row.get("Punteggio", 0)
        try:
            skills_list = ast.literal_eval(row.get("Skills", "[]"))
            plus = sum(SKILLS_MAPPING.get(skill, 0) for skill in skills_list)
            potenziale += plus * 2  # Diamo più peso alle skill nel potenziale
        except (ValueError, SyntaxError):
            pass
        res_potenziale.append(potenziale)

    df["Convenienza Potenziale"] = res_potenziale
    logger.debug("Indice 'Convenienza Potenziale' calcolato per FPEDIA.")

    return df

