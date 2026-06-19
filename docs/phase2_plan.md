# Phase 2: The UI Skeleton (`app.py`)

## Objective
Build the basic Streamlit frontend to display the data generated in Phase 1 and provide interactive controls for the user to configure league settings and scoring rules. 

## Key Components

### 1. `src/app.py`
The main entry point for the Streamlit application.

*   **Configuration & Sidebar:**
    *   Set up a wide layout using `st.set_page_config`.
    *   Created a sidebar with sections for:
        *   **League Settings:** Inputs for Number of Teams, Total Rounds, and Draft Position.
        *   **Roster Baselines:** Expected number of starters for QB, RB, WR, and TE. These inputs dynamically feed into the `calculate_vorp` function from Phase 1.
        *   **Scoring Rules:** Number inputs for Pass Yds, Pass TD, INT, Rush Yds, Rush TD, Rec (PPR), TE Premium, Rec Yds, and Rec TD. These feed into `calculate_projected_points`.
*   **Data Processing Pipeline:**
    *   Utilized `@st.cache_data` to efficiently run the Phase 1 functions (`load_and_merge_data`, `calculate_projected_points`, `calculate_vorp`) whenever the user modifies a sidebar setting.
*   **Draft Board Placeholder:**
    *   Created an empty Pandas DataFrame with columns representing Teams (Team 1 to Team N) and rows representing Rounds (Round 1 to Round M).
    *   Displayed this grid using `st.dataframe` to visually hold the structure for the upcoming interactive draft board in Phase 3.
*   **Available Player Pool:**
    *   Displayed the merged and scored player data in a sortable, interactive `st.dataframe`.
    *   Included columns for Player, Position, Team, ADP, StdDev, Projected Points, and VORP.
    *   Sorted the data by VORP descending by default and applied a background gradient to the VORP column to highlight valuable players visually.

## Success Criteria for Phase 2
*   Streamlit app runs without errors using `streamlit run src/app.py`.
*   Sidebar controls successfully update the player pool data (e.g., changing Pass TD from 4 to 6 immediately updates QB Projected Points and VORP).
*   The empty Draft Board grid renders correctly based on the number of teams and rounds selected in the sidebar.
*   The Player Pool table displays the correctly calculated data and formatting.