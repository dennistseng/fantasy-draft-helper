# Phase 5: Universal Flex Support (The SFB Overhaul)

## Objective
Refactor the application to handle both traditional roster requirements and highly flexible formats like the Scott Fish Bowl (SFB) seamlessly. This involves overhauling how VORP is calculated and how the simulation engine perceives positional need.

## Key Components

### 1. UI Updates (`src/app.py`)
*   Change the sidebar configuration from floating-point "Roster Baselines" to strict integer "Starting Lineup Slots".
*   Add dedicated inputs for `FLEX` (RB/WR/TE) and `SUPERFLEX` (QB/RB/WR/TE).

### 2. Tiered Allocation Algorithm for VORP (`src/data_loader.py`)
Rewrite `calculate_vorp` to dynamically determine replacement baselines across combined player pools. The algorithm must execute in this specific order:
*   **Step 1 (Mandatory Slots):** Lock the top players required to fill any specific positional inputs (e.g., if QB=1, lock the top 12 QBs).
*   **Step 2 (FLEX Slots):** From the remaining available RBs, WRs, and TEs, lock the top players required to fill all Flex spots. The final locked player establishes the Flex Replacement Baseline.
*   **Step 3 (SUPERFLEX Slots):** From the remaining available players across all positions (including QBs), lock the top players required to fill all Superflex spots. The final locked player establishes the Superflex Replacement Baseline.
*   **Step 4 (Positional Baselines):** For any specific position (e.g., TE) that isn't naturally filling the flex pools, determine the highest projected points among the remaining players of that position.
*   **Step 5 (Final Calculation):** Calculate VORP for every player based on the final replacement baseline established for their specific position in Step 4.

### 3. Slot-Based Positional Penalty (`src/engine.py`)
Rewrite `get_positional_penalty` to move away from evaluating "expected starters" and instead evaluate "available starting slots".
*   **Logic Flow:**
    1.  *Desperation Check:* If a team has 0 QBs and there are Superflex slots available, apply a reach penalty (-5.0 picks) to incentivize drafting a QB.
    2.  *Slot Availability Check:* Does the drafted player fit into an open, legal starting slot (Specific, Flex, or Superflex)? If yes, apply no penalty (0.0).
    3.  *Bench Depth Penalty:* If all legal starting slots for this player are full, they are relegated to the bench. Apply a standard bench penalty (+12.0 picks).

## Success Criteria for Phase 5
*   The tool successfully calculates VORP for extreme SFB cases (e.g., 0 positional minimums, 8 Flex, 2 Superflex).
*   The simulation engine dynamically handles teams filling flex spots rather than adhering to rigid positional caps.