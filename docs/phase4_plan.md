# Phase 4: Refinement (The "Deep End")

## Objective
Enhance the core Monte Carlo simulation engine to evaluate players based on Positional Need and Roster Scarcity, moving beyond simple ADP variance. This creates a highly realistic draft simulation where teams adapt to their roster requirements.

## Key Components

### 1. Positional Need Penalty (`src/engine.py`)
Implemented `get_positional_penalty`, which calculates a modifier for a player's perceived value based on a team's current roster.
*   **Mechanics:** Evaluates a team's current positional count against the league's `roster_settings` (expected starters).
*   **Desperation (-5.0 picks):** If a team has 0 players at a core position, their perceived ADP for players at that position is artificially lowered (making them appear more valuable, simulating a "reach").
*   **Standard Evaluation (0.0 picks):** If a team is still filling their baseline starters, they evaluate ADP normally.
*   **Bench Depth Penalty (+12.0 to +24.0 picks):** Once a team fills their starters, they deprioritize that position. The simulation adds 12 to 24 picks to the player's perceived ADP, meaning the team will only draft them if they are an absolute steal (falling a full 1-2 rounds past their ADP).
*   **Max Limit (+999.0 picks):** If a team hits their positional limit, they will physically not draft another player at that position.

### 2. Enhanced Monte Carlo Loop (`src/engine.py`)
Upgraded `run_monte_carlo_simulations` to incorporate the new positional logic.
*   **State Tracking:** Inside the 1000x simulation loop, the engine now generates a temporary copy of every simulated team's roster counts.
*   **The Decision Logic:**
    1.  *Roll the Dice:* Uses `scipy.stats` to pull a simulated draft position based on the player's ADP and StdDev.
    2.  *Apply the Penalty:* Evaluates the simulated team's current roster count for each position and calculates the penalty.
    3.  *Adjust:* `Adjusted_Draft_Position = Simulated_Draft_Position + Positional_Need_Penalty`.
    4.  *Select:* The team drafts the player with the *lowest* `Adjusted_Draft_Position`.
*   **Roster Updates:** The drafted player is added to the temporary simulated roster count, ensuring that if a team drafts a QB in the simulation, their need for a QB drops in the very next pick.

### 3. Application Integration (`src/app.py`)
*   Updated the `run_monte_carlo_simulations` call in the Streamlit UI to dynamically pass the `roster_settings` dictionary from the sidebar configuration. This links the user's SFB-style starting limits directly to the logic of the simulated opponents.

## Success Criteria for Phase 4
*   Simulated teams behave realistically: they will not blindly draft 4 QBs in a row even if those QBs have the best raw ADP.
*   The `% Avail Next Pick` calculations dynamically shift as the draft progresses. If 10 QBs are taken in Round 1, the probability of a QB falling to you in Round 2 drops sharply because the engine recognizes the positional run and increased scarcity among the remaining teams.