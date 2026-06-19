import pandas as pd
import numpy as np

def load_and_merge_data(adp_path: str, proj_path: str) -> pd.DataFrame:
    """
    Loads ADP and Projection CSVs and merges them on Player, Position, and Team.
    """
    try:
        adp_df = pd.read_csv(adp_path)
        proj_df = pd.read_csv(proj_path)
        
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
        'rush_rec_2pt': 2
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

    return df


def calculate_vorp(df: pd.DataFrame, roster_settings: dict, league_size: int = 12) -> pd.DataFrame:
    """
    Calculates Value Over Replacement Player (VORP).
    """
    df = df.copy()
    df['VORP'] = 0.0
    
    # Calculate how many of each position are expected to be drafted as "starters"
    # Note: SFB has flexible starting spots (0-2 QB, etc.). For VORP baselining, 
    # we need to make an assumption about the "meta" or average drafted starters.
    
    # Using typical SFB "expected" starters as baselines for calculation
    # If the rule is 0-2 QB, typically ~20 QBs will start across 12 teams.
    # If 10 starters total, maybe 20 QB, 30 RB, 40 WR, 15 TE.
    # We will use the provided roster_settings dictionary to define these baselines.
    
    for pos, expected_starters_per_team in roster_settings.items():
        if pos == 'FLEX' or pos == 'SUPERFLEX':
            continue # Flex complicates VORP, we'll establish positional baselines first
            
        total_starters = expected_starters_per_team * league_size
        
        # Filter for the specific position and sort by projected points
        pos_df = df[df['Position'] == pos].sort_values(by='Projected_Points', ascending=False)
        
        # If we have fewer players in the DB than expected starters, replacement is 0
        if len(pos_df) <= total_starters:
             replacement_value = 0
        else:
             # The replacement player is the one drafted right after the last starter
             # e.g., if 24 QBs start, the 25th QB is replacement level
             replacement_index = int(total_starters)
             replacement_value = pos_df.iloc[replacement_index]['Projected_Points']
             
        # Calculate VORP for this position
        mask = df['Position'] == pos
        df.loc[mask, 'VORP'] = df.loc[mask, 'Projected_Points'] - replacement_value

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
        # Assuming a baseline of 1.5 QBs, 2.5 RBs, 3.5 WRs, 1.25 TEs per team for SFB baseline
        sfb_baselines = {'QB': 1.5, 'RB': 2.5, 'WR': 3.5, 'TE': 1.25}
        vorp_data = calculate_vorp(scored_data, sfb_baselines, league_size=12)
        
        # Sort by VORP to see top overall value
        top_vorp = vorp_data.sort_values(by='VORP', ascending=False)
        print(top_vorp[['Player', 'Position', 'Projected_Points', 'VORP']].head(10))
