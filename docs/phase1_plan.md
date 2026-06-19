# Phase 1: Foundation (Data & Scoring)

## Objective
Establish the foundational data pipeline for the Fantasy Draft Helper. This involves ingesting raw player data (ADP and Projections), applying dynamic scoring rules defined by the user, and calculating baseline values like Total Projected Points and Value Over Replacement Player (VORP).

## Key Components

### 1. Data Structures (Mock Data)
To test the pipeline before integrating real data, we will create two mock CSV files in the `data/` directory:
*   `data/adp_data.csv`: Contains Player Name, Position, Team, ADP, and ADP Standard Deviation.
*   `data/projections.csv`: Contains Player Name, Position, Team, and raw projected stats (Pass Yds, Pass TDs, Ints, Rush Yds, Rush TDs, Receptions, Rec Yds, Rec TDs).

### 2. `src/data_loader.py` Module
This module will handle all data ingestion and baseline calculations.

#### Functions to Implement:

*   **`load_and_merge_data(adp_path, proj_path)`**
    *   **Input:** File paths to the ADP and Projections CSVs.
    *   **Logic:** Reads both CSVs using Pandas. Merges them into a single DataFrame based on Player Name (and potentially Position/Team to handle edge cases like players with the same name).
    *   **Output:** A unified Pandas DataFrame containing both ADP data and raw statistical projections.

*   **`calculate_projected_points(df, scoring_rules)`**
    *   **Input:** The merged DataFrame and a dictionary of `scoring_rules` (e.g., `{'pass_td': 6, 'ppr': 0.5, 'te_premium': 1.0}`).
    *   **Logic:** Iterates through the DataFrame, applying the scoring rules to the raw projections to calculate a new column: `Projected_Points`. 
    *   **Note:** This function will be designed to be extensible, allowing for the easy addition of future rules (like First Downs or milestone bonuses) without breaking existing logic.
    *   **Output:** The DataFrame with the appended `Projected_Points` column.

*   **`calculate_vorp(df, roster_settings, league_size)`**
    *   **Input:** The DataFrame (now with projected points), roster requirements (e.g., `{'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'FLEX': 1}`), and the number of teams (e.g., 12).
    *   **Logic:**
        1.  Determine the total number of starters required across the league for each position (e.g., 12 teams * 1 QB = 12 starting QBs).
        2.  Identify the "replacement level" player for each position. This is typically the projected points of the player ranked just below the last starter (e.g., the 13th ranked QB).
        3.  For every player, calculate their VORP: `Player Projected Points - Replacement Level Points for their position`.
    *   **Output:** The DataFrame with the appended `VORP` column.

## Success Criteria for Phase 1
*   Mock CSVs are created and correctly formatted.
*   `data_loader.py` successfully reads and merges the mock data.
*   `calculate_projected_points` accurately computes totals based on variable input dictionaries.
*   `calculate_vorp` establishes reasonable replacement baselines and assigns a VORP value to all relevant players.
*   The output is a single, clean Pandas DataFrame ready to be consumed by the Streamlit UI and the Simulation Engine.