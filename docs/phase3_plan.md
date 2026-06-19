# Phase 3: The Engine & Interactivity

## Objective
Transform the static UI into a fully interactive application by implementing state management for the draft and building the core Monte Carlo simulation engine to predict player availability.

## Key Components

### 1. Draft State Management (`src/engine.py`)
Created a `DraftState` class to manage the live environment of the draft.
*   **Properties:**
    *   Tracks `current_pick`, `num_teams`, and `total_rounds`.
    *   Maintains the `available_players` DataFrame (updating as picks are made).
    *   Maintains team `rosters` (a dictionary tracking who each team has drafted).
    *   Maintains a `draft_log` (a historical list of every pick made).
*   **Core Logic (`get_team_for_pick`):** Implements the "snake draft" math to determine which team owns any given pick number (e.g., in a 12-team league, Team 12 picks at 12 and 13).
*   **Action (`make_pick`):** Takes a player name, logs the pick to the correct team, removes the player from the available pool, and advances the pick counter.
*   **UI Helper (`get_draft_board_df`):** Generates a formatted Pandas DataFrame of the draft history to be rendered directly by Streamlit.

### 2. The Monte Carlo Simulator (`src/engine.py`)
Implemented the `run_monte_carlo_simulations` function to provide the core predictive analytics.
*   **Logic Flow:**
    1.  Determines how many picks exist between the `current_pick` and the user's *next* pick based on their designated draft position.
    2.  If the gap is 0, everyone available has a 100% availability probability.
    3.  If there is a gap, it runs a loop $N$ times (currently 1000).
    4.  **The Simulation Step:** For every pick in the gap, it simulates an opponent's decision by pulling a random expected draft position for every available player along their ADP Bell Curve (using `scipy.stats.norm.rvs` with the player's ADP as the mean and ADP_StdDev as the standard deviation). The player with the lowest simulated number is drafted and removed from that specific simulation's pool.
    5.  **Aggregation:** After simulating the gap, it checks which players "survived" (remained undrafted). It repeats this 1000 times to calculate the final `Sim_Avail_Next_Pick` percentage.

### 3. Streamlit UI Integration (`src/app.py`)
Connected the `DraftState` and the simulation engine to the frontend.
*   **Session State:** Used `st.session_state` to persist the `DraftState` object across UI reruns, ensuring the draft doesn't reset when a user interacts with a widget.
*   **Interactive Drafting:** Added a dropdown (populated by currently available players) and a "Draft Player" button. Clicking this triggers `draft_state.make_pick()` and reruns the app to update the view.
*   **Dynamic UI Updates:**
    *   The Draft Board grid now populates with player names in real-time.
    *   The Player Pool table now calls the simulation engine on every rerun. It displays the new `Sim_Avail_Next_Pick` column, heavily styled with a Red-Yellow-Green gradient to instantly highlight which players are likely to make it back to the user's next turn.

## Success Criteria for Phase 3
*   Users can select a player from a dropdown and click "Draft" to log the pick.
*   The UI grid updates to show the selected player in the correct cell based on snake draft logic.
*   The drafted player is removed from the available pool table.
*   The `Sim_Avail_Next_Pick` column calculates and displays a percentage between 0 and 100% based on the Monte Carlo outputs, updating dynamically based on how many picks are between the current pick and the user's designated team slot.