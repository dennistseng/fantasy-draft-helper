# Fantasy Draft Helper

This project contains a Python-based Fantasy Football Draft helper that uses a Monte Carlo simulation engine to predict draft probability availability. 

## Project Architecture

* **Framework:** Streamlit (UI), Pandas (Data handling), SciPy/NumPy (Math & Simulations)
* **`src/app.py`**: The Streamlit frontend. Displays the draft board, user settings, and probability tables.
* **`src/engine.py`**: The Monte Carlo simulator. Handles running 1000s of simulated drafts to determine player availability based on positional need and VORP.
* **`src/data_loader.py`**: Ingests raw ADP and Projection CSVs, applies user-defined dynamic scoring rules, and calculates baseline metrics like Total Projected Points and VORP.

## Environment Setup

The project uses standard Python `venv` and `pip` for dependency management.

**Creating & Activating the Virtual Environment:**
* Windows: `python -m venv venv` then `.\venv\Scripts\Activate.ps1`
* Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`

**Installing Dependencies:**
* `pip install -r requirements.txt`

## Running the Application

To run the Streamlit dashboard locally:
```bash
streamlit run src/app.py
```

## Data Files
* Place ADP data in `data/adp_data.csv`
* Place Season Projections in `data/projections.csv`

## Development Phases

### Phase 1: Foundation (Data & Scoring)
* Ingest mock/real CSVs for ADP and raw Projections.
* Calculate dynamic baseline scores based on customizable user scoring inputs.
* Calculate VORP (Value Over Replacement Player) based on league positional requirements.

### Phase 2: The UI Skeleton (`app.py`)
* Build Streamlit sidebar for league settings (league size, position limits, custom scoring).
* Create an interactive draft board grid (Rounds vs Teams).
* Display the available player pool data table.

### Phase 3: The Engine & Interactivity (`engine.py`)
* Implement state management (`DraftState`) to track drafted players, rosters, and the available pool.
* Build the core Monte Carlo simulation loop to run 1,000+ simulated remaining drafts based on ADP, Variance (StdDev), and VORP.

### Phase 4: Refinement (The "Deep End")
* Integrate simulation probabilities back into the UI table (`% Avail Next Pick`).
* Implement complex Positional Need multipliers to handle flexible starting spots (e.g., Scott Fish Bowl's 0-2 QBs rules).

### Phase 5: Universal Flex Support (The SFB Overhaul)
* Update Streamlit UI sidebar to accept discrete starting slot inputs, including Flex and Superflex.
* Rewrite `calculate_vorp` to use a "Tiered Allocation Algorithm" that accurately calculates replacement baselines regardless of whether the league uses strict positional slots or pure flex slots.
* Update the simulation's `get_positional_penalty` logic to evaluate "Available Starting Slots" rather than strict expected positional limits.
