# Phase 8: True Next Pick Probability Logic

## Goal
Redefine the "Next Pick" logic in the Monte Carlo simulation to properly calculate probabilities for the *next* time the user is on the clock, especially correctly handling the scenarios where the user is currently on the clock (including back-to-back picks).

## Problem Statement
Previously, if the user was currently on the clock, the simulation would identify `picks_until_me = 0` and bypass the Monte Carlo simulation, returning 100% availability for all players. This is unhelpful because the user wants to know the probability of a player making it back to them for their *subsequent* turn (e.g., if they are picking at 12 and 13, they want to know who will be there at pick 36).

## Proposed Solution
Update `run_monte_carlo_simulations` in `src/engine.py`:
1. **Skip the Current Turn:** Start scanning from the `current_pick`. If that pick belongs to the user, advance forward until finding a pick that belongs to *another* team. This skips consecutive picks (like 12 and 13).
2. **Find the True Next Turn:** Continue scanning forward to find the *next* pick that belongs to the user (e.g., pick 36).
3. **Simulate the Gap:** Set the `my_next_pick` to this newly found pick. The engine will simulate all picks between the current pick and that future pick (including having the AI organically simulate the user's current pending picks based on ADP and team needs).

## Implementation Details
- Remove the `picks_until_me == 0` check as it is no longer reachable or desired.
- Iterate over picks to cleanly separate the "skip current block" phase and the "find next turn" phase.
