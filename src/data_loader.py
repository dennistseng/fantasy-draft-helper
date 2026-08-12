import pandas as pd
import numpy as np

def load_and_merge_data(adp_path: str, proj_path: str) -> pd.DataFrame:
    """
    Loads ADP and Projection CSVs and merges them on Player, Position, and Team.
    """
    try:
        adp_df = pd.read_csv(adp_path, thousands=',')
        proj_df = pd.read_csv(proj_path, thousands=',')
        
        # Strip whitespace from string columns to prevent merge issues
        for df in [adp_df, proj_df]:
            string_cols = df.select_dtypes(['object', 'string']).columns
            df[string_cols] = df[string_cols].apply(lambda x: x.str.strip() if hasattr(x.str, 'strip') else x)

        # Merge the dataframes. Using inner join to only keep players with both ADP and Projections.
        # Merging on Player, Position, and Team helps resolve same-name issues.
        merged_df = pd.merge(adp_df, proj_df, on=['Player', 'Position', 'Team'], how='inner')
        return merged_df

    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred during data merging: {e}")
        return pd.DataFrame()


def calculate_projected_points(df: pd.DataFrame, scoring_rules: dict) -> pd.DataFrame:
    """
    Calculates projected fantasy points based on provided scoring rules.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Default rules based roughly on SFB16 screenshot
    default_rules = {
        'pass_yd': 0.04,
        'pass_td': 6,
        'int': -2,  # Assuming standard -2 for INTs as it wasn't explicitly shown
        'rush_yd': 0.1,
        'rush_td': 6,
        'rec': 0.5, # Base PPR
        'te_rec_bonus': 1.0, # TE gets +1 on top of base PPR
        'rec_yd': 0.1,
        'rec_td': 6,
        'pass_2pt': 2,
        'rush_rec_2pt': 2,
        'bonus_pass_300': 10.0,
        'bonus_pass_400': 10.0,
        'bonus_comb_100': 10.0,
        'bonus_comb_200': 10.0,
        'bonus_pass_40p': 10.0,
        'bonus_rush_40p': 10.0,
        'bonus_rec_20p': 10.0
    }
    
    # Update defaults with any provided rules
    rules = {**default_rules, **scoring_rules}

    # Initialize points column
    df['Projected_Points'] = 0.0

    # Passing
    if 'Pass_Yds' in df.columns: df['Projected_Points'] += df['Pass_Yds'] * rules['pass_yd']
    if 'Pass_TD' in df.columns: df['Projected_Points'] += df['Pass_TD'] * rules['pass_td']
    if 'Int' in df.columns: df['Projected_Points'] += df['Int'] * rules['int']

    # Rushing
    if 'Rush_Yds' in df.columns: df['Projected_Points'] += df['Rush_Yds'] * rules['rush_yd']
    if 'Rush_TD' in df.columns: df['Projected_Points'] += df['Rush_TD'] * rules['rush_td']

    # Receiving (Base)
    if 'Rec' in df.columns: df['Projected_Points'] += df['Rec'] * rules['rec']
    if 'Rec_Yds' in df.columns: df['Projected_Points'] += df['Rec_Yds'] * rules['rec_yd']
    if 'Rec_TD' in df.columns: df['Projected_Points'] += df['Rec_TD'] * rules['rec_td']

    # TE Premium Bonus
    if 'Rec' in df.columns and 'te_rec_bonus' in rules:
        te_mask = df['Position'] == 'TE'
        df.loc[te_mask, 'Projected_Points'] += df.loc[te_mask, 'Rec'] * rules['te_rec_bonus']

    # SFB Bonuses (Milestones & Explosive Plays)
    if 'Games_Pass_300' in df.columns: df['Projected_Points'] += df['Games_Pass_300'] * rules['bonus_pass_300']
    if 'Games_Pass_400' in df.columns: df['Projected_Points'] += df['Games_Pass_400'] * rules['bonus_pass_400']
    if 'Games_Comb_100' in df.columns: df['Projected_Points'] += df['Games_Comb_100'] * rules['bonus_comb_100']
    if 'Games_Comb_200' in df.columns: df['Projected_Points'] += df['Games_Comb_200'] * rules['bonus_comb_200']
    if 'Pass_40p' in df.columns: df['Projected_Points'] += df['Pass_40p'] * rules['bonus_pass_40p']
    if 'Rush_40p' in df.columns: df['Projected_Points'] += df['Rush_40p'] * rules['bonus_rush_40p']
    if 'Rec_20p' in df.columns: df['Projected_Points'] += df['Rec_20p'] * rules['bonus_rec_20p']

    return df


def calculate_vorp(df: pd.DataFrame, roster_settings: dict, league_size: int = 12) -> pd.DataFrame:
    """
    Calculates Value Over Replacement Player (VORP) using the Tiered Allocation Algorithm.
    Supports specific slots, FLEX, and SUPERFLEX.
    """
    df = df.copy()
    df['VORP'] = 0.0
    
    # Sort entire dataframe by projected points to make greedy allocation easy
    df_sorted = df.sort_values(by='Projected_Points', ascending=False)
    
    locked_indices = set()
    
    # Step 1: Fill Mandatory Specific Positions
    for pos in ['QB', 'RB', 'WR', 'TE']:
        needed = roster_settings.get(pos, 0) * league_size
        if needed > 0:
            # Find the top 'needed' players at this position not already locked
            available = df_sorted[(df_sorted['Position'] == pos) & (~df_sorted.index.isin(locked_indices))]
            locked_indices.update(available.head(needed).index.tolist())
            
    # Step 2: Fill FLEX Slots (RB, WR, TE)
    flex_needed = roster_settings.get('FLEX', 0) * league_size
    if flex_needed > 0:
        available = df_sorted[
            (df_sorted['Position'].isin(['RB', 'WR', 'TE'])) & 
            (~df_sorted.index.isin(locked_indices))
        ]
        locked_indices.update(available.head(flex_needed).index.tolist())
        
    # Step 3: Fill SUPERFLEX Slots (QB, RB, WR, TE)
    sflex_needed = roster_settings.get('SUPERFLEX', 0) * league_size
    if sflex_needed > 0:
        available = df_sorted[~df_sorted.index.isin(locked_indices)]
        locked_indices.update(available.head(sflex_needed).index.tolist())
        
    # Step 4: Establish Positional Baselines
    # The baseline for a position is the projected points of the BEST remaining player
    # at that position who was NOT drafted as a starter in the steps above.
    pos_baselines = {}
    remaining_players = df_sorted[~df_sorted.index.isin(locked_indices)]
    
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_remaining = remaining_players[remaining_players['Position'] == pos]
        if not pos_remaining.empty:
            pos_baselines[pos] = pos_remaining.iloc[0]['Projected_Points']
        else:
            pos_baselines[pos] = 0.0
            
    # Step 5: Calculate VORP
    # VORP = Projected Points - Positional Baseline
    df['VORP'] = df.apply(
        lambda row: row['Projected_Points'] - pos_baselines.get(row['Position'], 0.0), 
        axis=1
    )

    return df

# Simple test block
if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    adp_file = os.path.join(base_dir, "data", "adp_data.csv")
    proj_file = os.path.join(base_dir, "data", "projections.csv")
    
    print("Loading and Merging Data...")
    merged_data = load_and_merge_data(adp_file, proj_file)
    print(f"Merged Data Shape: {merged_data.shape}")
    
    if not merged_data.empty:
        print("\nCalculating Projected Points (Default Rules)...")
        # Customizing rules just to show how it works
        custom_rules = {'pass_td': 6, 'te_rec_bonus': 1.5} 
        scored_data = calculate_projected_points(merged_data, custom_rules)
        print(scored_data[['Player', 'Position', 'Projected_Points']].head())
        
        print("\nCalculating VORP...")
        # Testing with SFB Pure Flex Layout, but small enough to leave players in the pool
        sfb_baselines = {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0, 'FLEX': 1, 'SUPERFLEX': 1}
        vorp_data = calculate_vorp(scored_data, sfb_baselines, league_size=4)
        
        # Sort by VORP to see top overall value
        top_vorp = vorp_data.sort_values(by='VORP', ascending=False)
        print(top_vorp[['Player', 'Position', 'Projected_Points', 'VORP']].head(10))
