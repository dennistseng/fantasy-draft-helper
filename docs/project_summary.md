# Fantasy Draft Helper: Project Summary

## Overview
The Fantasy Draft Helper is an advanced, interactive draft companion designed to give fantasy football managers a statistical edge, particularly in leagues with complex scoring and flexible roster requirements (such as the Scott Fish Bowl). 

Instead of relying on static, one-size-fits-all rankings, this tool uses predictive modeling to act as a "crystal ball." As the draft unfolds, it calculates the exact mathematical probability that any given player will still be available when it is your turn to pick again.

## How the Logic Works

The tool operates on three core logical pillars:

### 1. Dynamic Value Calculation (VORP) & Universal Flex
Every league is different. A player's value changes drastically depending on whether passing touchdowns are worth 4 or 6 points, or if tight ends get a premium bonus.
* **Custom Scoring:** The tool takes raw player stat projections (yards, touchdowns, catches) and applies the specific scoring rules of your league to determine their projected total points.
* **Tiered Allocation Algorithm:** Total points aren't enough. A quarterback will almost always outscore a tight end. To accurately calculate Value Over Replacement Player (VORP), the tool must identify the "baseline" (the worst starter) for every position. To support extreme flexibility like the Scott Fish Bowl (which uses pure Flex and Superflex slots instead of mandatory positional slots), the tool uses a "Tiered Allocation Algorithm." It mathematically fills mandatory slots first, then Flex slots, and finally Superflex slots. This dynamically discovers the true replacement value of a player across combined, cross-positional pools rather than rigid silos.

### 2. The Predictive Engine (Monte Carlo Simulations)
The defining feature of the tool is its predictive engine. Whenever a pick is made, the tool doesn't just guess what will happen next—it simulates the remainder of the draft **1,000 times** in the blink of an eye.
* By simulating a thousand parallel universes of the draft, it can confidently tell you: *"In 650 of our 1,000 simulations, Player X was still available at your next pick. You have a 65% chance of getting him if you wait."*

### 3. Modeling Human Behavior (Positional Scarcity)
If the simulation only assumed that opponents drafted the highest-ranked player available, it would be highly inaccurate. Humans draft based on roster needs and panic. The engine mimics realistic human behavior through two mechanisms:
* **Draft Variance:** Opponents don't follow Average Draft Position (ADP) rigidly. The tool introduces realistic randomness (a bell curve) based on how widely a player's draft position typically varies.
* **Positional Need & Slot Availability:** The engine actively tracks the simulated rosters of every opponent during its 1,000 test runs, evaluating their empty starting lineup slots. 
    * *Desperation:* If a simulated opponent has zero Quarterbacks and an open Superflex slot, the engine forces them to "reach" for one.
    * *Satisfaction:* If an opponent fills all their legal starting slots for a position, any subsequent player at that position would be relegated to their bench. The engine heavily penalizes bench picks, ensuring they draft a starter for an empty slot instead.

## The User Experience
All of this complex math is wrapped in a clean, user-friendly interface:
* **The Control Panel:** Users can adjust sliders and inputs for league size, draft position, starting lineup slots (including Flex/Superflex), and scoring rules on the fly.
* **The Draft Board:** A visual grid tracks the draft round-by-round, updating instantly as players are selected.
* **The Player Pool:** An interactive table displaying all remaining players, sorted by true value (VORP). Crucially, this table features a color-coded **"Probability Available at Next Pick"** column, turning dark green for safe bets and deep red for players likely to be drafted before your next turn.

## Current Status
The project has successfully bridged data ingestion, dynamic scoring, the Monte Carlo simulation engine, and the interactive user interface. It is a fully functional prototype capable of generating real-time predictive insights during a live fantasy football draft, with robust support for complex Universal Flex formats.