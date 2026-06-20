# Phase 7: Performance & On-Demand Simulation

## Objective
Optimize the application's responsiveness by decoupling the computationally intensive Monte Carlo simulation engine from the general Streamlit render loop. This ensures the UI remains lightning-fast during rapid drafting or scoring adjustments.

## Key Components

### 1. User Interface Additions (`src/app.py`)
*   **Simulation Control:** Add a new numeric input in the sidebar for `Number of Simulations` allowing users to balance speed versus statistical confidence (Default: 1000).
*   **Manual Trigger:** Implement an on-demand "Run Probability Simulation" button directly above the Player Pool table.

### 2. State Management (`src/app.py`)
*   **Decoupled Execution:** The `run_monte_carlo_simulations` function will *only* fire when the new trigger button is clicked.
*   **Caching Results:** The output of the simulation will be stored in `st.session_state.sim_results`.
*   **Dynamic Views:**
    *   *Base View:* If no simulation has been run (or results were cleared), display the standard Player Pool sorted by VORP without probability metrics.
    *   *Simulation View:* If `sim_results` exists in the session state, display the advanced table featuring the color-coded `% Avail Next Pick` column.
*   **Invalidation Logic:** Any action that alters the mathematical foundation of the draft (logging a pick, resetting the draft, changing scoring rules, or altering starting lineup slots) must automatically clear `st.session_state.sim_results` to prevent stale data from being displayed.

## Success Criteria for Phase 7
*   The application UI (sliders, dropdowns, Draft Board rendering) responds instantly without triggering background simulations.
*   The user can dictate exactly how many simulation loops the engine should execute.
*   Clicking the simulation button runs the engine and displays the probabilities correctly.
*   Registering a new pick immediately clears the probability data, requiring a fresh simulation run to see updated odds.