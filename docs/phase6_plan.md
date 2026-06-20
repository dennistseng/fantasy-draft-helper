# Phase 6: Custom Draft Order (Round Reversal)

## Objective
Implement a "Round Reversal" feature (most commonly the 3rd Round Reversal or 3RR) to support modern, high-stakes draft formats like the Scott Fish Bowl. This allows the snake draft parity to "flip" at a specified round, balancing the structural advantage of drafting early.

## Key Components

### 1. UI Configuration (`src/app.py`)
*   **Settings Toggle:** Add a checkbox to the "League Settings" sidebar section allowing users to enable or disable "Round Reversal".
*   **Round Selection:** Add a conditional number input that appears when the toggle is enabled, allowing the user to select the specific round where the reversal occurs (defaulting to Round 3).
*   **State Propagation:** Ensure the `reversal_round` parameter is passed into the `DraftState` object upon initialization.

### 2. Core Draft Logic Update (`src/engine.py`)
*   **State Initialization:** Update the `DraftState` class to accept and store the `reversal_round` parameter.
*   **Snake Math Overhaul:** Rewrite the `get_team_for_pick` function. 
    *   The standard logic relies on round parity (even rounds snake backward: 12 to 1).
    *   The updated logic will check if a `reversal_round` is active.
    *   If the current round is greater than or equal to the `reversal_round`, the parity of the round is mathematically inverted. For example, in a 3RR, Round 3 (an odd round) will calculate its draft order as if it were an even round (12 to 1), and Round 4 (an even round) will calculate as an odd round (1 to 12). 

## Success Criteria for Phase 6
*   The Streamlit sidebar displays a toggle for Round Reversal.
*   When enabled (e.g., at Round 3 in a 12-team league), the Draft Board accurately reflects the pick order:
    *   Round 1: Team 1 ... Team 12
    *   Round 2: Team 12 ... Team 1
    *   Round 3: Team 12 ... Team 1 (The Reversal)
    *   Round 4: Team 1 ... Team 12
*   The Monte Carlo simulation correctly anticipates the user's future picks based on the modified snake order, accurately calculating the "picks until next turn."