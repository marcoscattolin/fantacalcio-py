from src.fstats.scraper import Scraper
from src.fstats.data_proc import FstatsDataProcessor as DataProcessor
from src.fstats.convenienza_calculator import calcola_convenienza
from src import config
import os
from loguru import logger


def main():
    """
    Main script to run the entire Fantacalcio analysis pipeline.
    It now runs two separate pipelines for FPEDIA and FSTATS,
    generating both performance-based and potential-based convenience indexes.
    """

    logger.info("+++++++++++++ Starting FSTATS analysis +++++++++++++")
    
    scraper = Scraper()
    scraper.scrape()
    
    data_processor = DataProcessor()
    raw_df = data_processor.load_dataframe()
    df_processed = data_processor.process_data(raw_df)
    
    df = calcola_convenienza(df_processed)
    df = df.sort_values(by="Convenienza Potenziale", ascending=False)

    # Define a comprehensive and ordered list of columns for the final output
    output_columns = [
        # Key Info
        "Nome",
        "Ruolo",
        "Squadra",
        # Calculated Indexes
        "Convenienza Potenziale",
        "Convenienza",
        "fantacalcioFantaindex",
        # Key Performance Indicators
        "fanta_avg",
        "avg",
        "presences",
        # Core Stats
        "goals",
        "assists",
        # Potential Stats
        "xgFromOpenPlays",
        "xA",
        # Disciplinary
        "yellowCards",
        "redCards",
        # Legacy
        "injured",
        "banned",
        "mantra_position",
        "fantacalcio_position",
        "birth_date",
        "foot_name",
        "fantacalcioPlayerId",
        "fantacalcioTeamName",
        "appearances",
        "matchesInStart",
        "mins_played",
        "pagella",
        "fantacalcioRanking",
        "fantacalcioFantaindex",
        "fantacalcioPosition",
        "assists",
        "goals",
        "goals90min",
        "goalsFromOpenPlays",
        "xgFromOpenPlays",
        "xgFromOpenPlays/90min",
        "xA",
        "xA90min",
        "redCards",
        "yellowCards",
        "successfulPenalties",
        "penalties",
        "gkPenaltiesSaved",
        "gkCleanSheets",
        "gkConcededGoals",
        "openPlaysGoalsConceded",
        "openPlaysXgConceded",
        "fantamediaPred",
        "fantamediaPredRoundId",
        "matchConvocation",
        "matchesWithGrade",
        "perc_matchesStarted",
        "perc_matchesWithGrade",
        "percMinsPlayed",
        "expectedFantamediaMean",
        "External_breakout_Index",
        "Shot_on_goal_Index",
        "Offensive_actions_Index",
        "Pass_forward_accuracy_Index",
        "Air_challenge_offensive_Index",
        "Cross_accuracy_Index",
        "Converge_in_the_center_Index",
        "Accompany_the_offensive_action_Index",
        "Offensive_verticalization_Index",
        "Received_pass_Index",
        "Attacking_area_Index",
        "Offensive_field_presence_Index",
        "Pass_accuracy_Index",
        "Pass_leading_chances_Index",
        "Deep_runs_Index",
        "Defense_solidity_Index",
        "Set_piece_attack_Index",
        "Shot_on_target_Index",
        "Dribbles_successful_Index",
    ]
    final_columns = [col for col in output_columns if col in df.columns]

    output_path = os.path.join(config.OUTPUT_DIR, "fstats_analysis.xlsx")
    df[final_columns].to_excel(output_path, index=False)

    logger.info(f"Results saved to {output_path}, shape: {df.shape}")
    
    logger.info("------------- FSTATS analysis complete -------------")

if __name__ == "__main__":
    main()
