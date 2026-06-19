import pandas as pd
import numpy as np
import scipy.stats as stats
import copy

class DraftState:
    def __init__(self, num_teams, total_rounds, initial_player_pool: pd.DataFrame):
        self.num_teams = num_teams
        self.total_rounds = total_rounds
        self.current_pick = 1
        
        # Keep track of available players
        self.available_players = initial_player_pool.copy()
        
        # Initialize rosters: dictionary of DataFrames or Lists per team
        self.rosters = {i: [] for i in range(1, num_teams + 1)}
        
        # Track the actual draft board: (Round, Pick In Round) -> (Team, Player)
        self.draft_log = []

    def get_team_for_pick(self, pick_num):
        """Calculates which team is picking based on snake draft logic."""
        round_num = ((pick_num - 1) // self.num_teams) + 1
        pick_in_round = ((pick_num - 1) % self.num_teams) + 1
        
        if round_num % 2 == 0:
            # Even rounds snake backward
            return self.num_teams - pick_in_round + 1
        else:
            return pick_in_round

    def make_pick(self, player_name: str, force_pick_num=None):
        """Logs a pick, removes player from pool, and advances state."""
        if player_name not in self.available_players['Player'].values:
            raise ValueError(f"Player {player_name} not found in available pool.")
            
        pick_to_use = force_pick_num if force_pick_num else self.current_pick
        team = self.get_team_for_pick(pick_to_use)
        
        # Get player data
        player_row = self.available_players[self.available_players['Player'] == player_name].iloc[0]
        
        # Update Roster
        self.rosters[team].append(player_row.to_dict())
        
        # Update Draft Log
        round_num = ((pick_to_use - 1) // self.num_teams) + 1
        self.draft_log.append({
            'Pick': pick_to_use,
            'Round': round_num,
            'Team': team,
            'Player': player_name,
            'Position': player_row['Position']
        })
        
        # Remove from pool
        self.available_players = self.available_players[self.available_players['Player'] != player_name]
        
        if not force_pick_num:
            self.current_pick += 1

    def get_draft_board_df(self):
        """Returns a formatted DataFrame for the Streamlit UI."""
        teams_cols = [f"Team {i}" for i in range(1, self.num_teams + 1)]
        rounds_index = [f"Round {i}" for i in range(1, self.total_rounds + 1)]
        
        board = pd.DataFrame(index=rounds_index, columns=teams_cols).fillna("")
        
        for entry in self.draft_log:
            round_idx = f"Round {entry['Round']}"
            team_col = f"Team {entry['Team']}"
            # Format: Player (Pos)
            board.at[round_idx, team_col] = f"{entry['Player']} ({entry['Position']})"
            
        return board


def get_positional_penalty(pos: str, current_roster: dict, roster_settings: dict) -> float:
    """
    Calculates a 'penalty' in draft picks based on a team's positional need.
    Evaluates available slots (Specific, Flex, Superflex).
    """
    if pos in ['K', 'DST']: 
        if current_roster.get(pos, 0) > 0: return 999
        return 0

    # 1. Desperation Check
    # If the team has 0 QBs and Superflex spots are available, reach for one.
    if pos == 'QB' and current_roster.get('QB', 0) == 0 and roster_settings.get('SUPERFLEX', 0) > 0:
        return -5.0 

    # Calculate overflow (players at a position exceeding mandatory specific slots)
    overflow = {}
    for p in ['QB', 'RB', 'WR', 'TE']:
        overflow[p] = max(0, current_roster.get(p, 0) - roster_settings.get(p, 0))
        
    # How much of the FLEX pool is used by RB/WR/TE overflow?
    flex_used = overflow['RB'] + overflow['WR'] + overflow['TE']
    flex_remaining = max(0, roster_settings.get('FLEX', 0) - flex_used)
    
    # If Flex is over capacity, that spills into Superflex
    flex_spillover = max(0, flex_used - roster_settings.get('FLEX', 0))
    
    # How much of the SUPERFLEX pool is used by QB overflow + Flex spillover?
    sflex_used = overflow['QB'] + flex_spillover
    sflex_remaining = max(0, roster_settings.get('SUPERFLEX', 0) - sflex_used)

    # 2. Slot Availability Check for the NEW player
    current_pos_count = current_roster.get(pos, 0)
    
    # Does it fit in a specific mandatory slot?
    if current_pos_count < roster_settings.get(pos, 0):
        return 0.0
        
    # Does it fit in a FLEX slot?
    if pos in ['RB', 'WR', 'TE'] and flex_remaining > 0:
        return 0.0
        
    # Does it fit in a SUPERFLEX slot?
    if pos in ['QB', 'RB', 'WR', 'TE'] and sflex_remaining > 0:
        return 0.0

    # 3. Bench Depth Penalty
    # If no starting slots are available, they are relegated to the bench.
    # We could scale this by total overflow, but a standard +12 picks works well.
    return 12.0


def run_monte_carlo_simulations(current_state: DraftState, my_team_id: int, roster_settings: dict, num_simulations=1000):
    """
    Simulates the remainder of the draft N times to calculate availability probabilities.
    Now incorporates Positional Need based on existing rosters and roster_settings.
    """
    total_picks_in_draft = current_state.num_teams * current_state.total_rounds
    my_next_pick = None
    
    # Find my next pick
    for p in range(current_state.current_pick, total_picks_in_draft + 1):
        if current_state.get_team_for_pick(p) == my_team_id:
            my_next_pick = p
            break
            
    if not my_next_pick:
        return pd.DataFrame()
        
    picks_until_me = my_next_pick - current_state.current_pick
    
    if picks_until_me == 0:
        results = current_state.available_players.copy()
        results['Sim_Avail_Next_Pick'] = 1.0
        return results
        
    survival_counts = {player: 0 for player in current_state.available_players['Player']}
    base_pool = current_state.available_players.copy()
    
    # Pre-calculate current roster counts for all teams to pass into simulations
    initial_roster_counts = {i: {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0} for i in range(1, current_state.num_teams + 1)}
    for team_id, roster in current_state.rosters.items():
        for player in roster:
            pos = player['Position']
            if pos in initial_roster_counts[team_id]:
                initial_roster_counts[team_id][pos] += 1
    
    for _ in range(num_simulations):
        sim_pool = base_pool.copy()
        # Deep copy the counts for this specific simulation iteration
        sim_counts = copy.deepcopy(initial_roster_counts)
        
        for step in range(picks_until_me):
             current_pick_num = current_state.current_pick + step
             team_picking = current_state.get_team_for_pick(current_pick_num)
             
             # 1. Roll the dice on perceived ADP (The Monte Carlo variance)
             sim_draft_positions = stats.norm.rvs(
                 loc=sim_pool['ADP'], 
                 scale=sim_pool['ADP_StdDev']
             )
             
             # 2. Adjust perceived ADP based on team's positional need
             # We use map/apply to calculate the penalty for each player's position
             team_needs = sim_counts[team_picking]
             penalties = sim_pool['Position'].apply(
                 lambda p: get_positional_penalty(p, team_needs, roster_settings)
             )
             
             adjusted_draft_positions = sim_draft_positions + penalties
             
             # 3. Draft the player with the lowest adjusted ADP
             best_idx = np.argmin(adjusted_draft_positions)
             player_drafted = sim_pool.iloc[best_idx]
             
             # Update Simulation State
             drafted_pos = player_drafted['Position']
             if drafted_pos in sim_counts[team_picking]:
                 sim_counts[team_picking][drafted_pos] += 1
                 
             sim_pool = sim_pool[sim_pool['Player'] != player_drafted['Player']]
             
        # Record who survived this simulation
        for player in sim_pool['Player']:
            survival_counts[player] += 1
            
    # Calculate Probabilities
    results = base_pool.copy()
    results['Sim_Avail_Next_Pick'] = results['Player'].map(survival_counts) / num_simulations
    
    return results
