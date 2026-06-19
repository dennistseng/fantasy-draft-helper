import streamlit as st
import pandas as pd
import os
from data_loader import load_and_merge_data, calculate_projected_points, calculate_vorp
from engine import DraftState, run_monte_carlo_simulations

# --- CONFIGURATION ---
st.set_page_config(page_title="Fantasy Draft Helper", layout="wide")

# Ensure paths work when running from project root
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
adp_file = os.path.join(base_dir, "data", "adp_data.csv")
proj_file = os.path.join(base_dir, "data", "projections.csv")

# --- SIDEBAR: LEAGUE & SCORING SETTINGS ---
st.sidebar.header("League Settings")
league_size = st.sidebar.number_input("Number of Teams", min_value=8, max_value=32, value=12, step=1)
total_rounds = st.sidebar.number_input("Total Rounds", min_value=5, max_value=40, value=15, step=1)
draft_position = st.sidebar.number_input("Your Draft Position", min_value=1, max_value=league_size, value=1, step=1)

st.sidebar.markdown("---")
st.sidebar.header("Starting Lineup Slots")
st.sidebar.caption("Exact number of starting slots per team.")
start_qb = st.sidebar.number_input("QB", min_value=0, value=0, step=1)
start_rb = st.sidebar.number_input("RB", min_value=0, value=0, step=1)
start_wr = st.sidebar.number_input("WR", min_value=0, value=0, step=1)
start_te = st.sidebar.number_input("TE", min_value=0, value=0, step=1)
start_flex = st.sidebar.number_input("FLEX (RB/WR/TE)", min_value=0, value=8, step=1)
start_sflex = st.sidebar.number_input("SUPERFLEX (QB/RB/WR/TE)", min_value=0, value=2, step=1)

roster_settings = {
    'QB': start_qb,
    'RB': start_rb,
    'WR': start_wr,
    'TE': start_te,
    'FLEX': start_flex,
    'SUPERFLEX': start_sflex
}

st.sidebar.markdown("---")
st.sidebar.header("Scoring Rules")
pass_yd = st.sidebar.number_input("Pass Yards (pts per yard)", value=0.04, step=0.01)
pass_td = st.sidebar.number_input("Pass TD", value=6.0, step=1.0)
int_pts = st.sidebar.number_input("Interception", value=-2.0, step=1.0)
rush_yd = st.sidebar.number_input("Rush Yards (pts per yard)", value=0.1, step=0.01)
rush_td = st.sidebar.number_input("Rush TD", value=6.0, step=1.0)
rec = st.sidebar.number_input("Reception (PPR)", value=0.5, step=0.1)
te_rec_bonus = st.sidebar.number_input("TE Premium (Extra pts/rec)", value=1.0, step=0.1)
rec_yd = st.sidebar.number_input("Rec Yards (pts per yard)", value=0.1, step=0.01)
rec_td = st.sidebar.number_input("Rec TD", value=6.0, step=1.0)

scoring_rules = {
    'pass_yd': pass_yd,
    'pass_td': pass_td,
    'int': int_pts,
    'rush_yd': rush_yd,
    'rush_td': rush_td,
    'rec': rec,
    'te_rec_bonus': te_rec_bonus,
    'rec_yd': rec_yd,
    'rec_td': rec_td,
}

# --- DATA PROCESSING ---
@st.cache_data
def get_data(adp_path, proj_path, scoring, roster_baselines, teams):
    df = load_and_merge_data(adp_path, proj_path)
    if not df.empty:
        df = calculate_projected_points(df, scoring)
        df = calculate_vorp(df, roster_baselines, league_size=teams)
    return df

# Load the data and apply settings
player_data = get_data(adp_file, proj_file, scoring_rules, roster_settings, league_size)

# --- SESSION STATE INITIALIZATION ---
if 'draft_state' not in st.session_state or st.sidebar.button("Reset Draft"):
    if not player_data.empty:
        st.session_state.draft_state = DraftState(league_size, total_rounds, player_data)
    else:
        st.session_state.draft_state = None

draft_state = st.session_state.draft_state

# --- MAIN UI: DRAFT BOARD ---
st.title("🏈 Fantasy Draft Helper")

# Interactive Pick Selection
if draft_state:
    st.markdown("### Log a Pick")
    col1, col2 = st.columns([3, 1])
    with col1:
        # Get list of available player names, sorted by ADP for the dropdown
        available_names = draft_state.available_players.sort_values('ADP')['Player'].tolist()
        selected_player = st.selectbox(
            f"Select Player for Pick {draft_state.current_pick} (Team {draft_state.get_team_for_pick(draft_state.current_pick)})", 
            options=available_names
        )
    with col2:
        st.write("") # spacing
        st.write("")
        if st.button("Draft Player"):
            draft_state.make_pick(selected_player)
            st.rerun()

st.header("Draft Board")

if draft_state:
    draft_board_df = draft_state.get_draft_board_df()
    st.dataframe(draft_board_df, use_container_width=True)
else:
    st.warning("Please configure data and initialize draft.")

# --- MAIN UI: PLAYER POOL ---
st.markdown("---")
st.header("Available Player Pool")

if not draft_state or draft_state.available_players.empty:
    st.warning("No available players. Draft may be complete or data is missing.")
else:
    st.info(f"Running Monte Carlo Simulations (N=1000) for Team {draft_position}...")
    # Run the engine with roster settings for positional need
    sim_results = run_monte_carlo_simulations(draft_state, draft_position, roster_settings, num_simulations=1000)
    
    # Format dataframe for display
    display_cols = ['Player', 'Position', 'Team', 'ADP', 'Projected_Points', 'VORP', 'Sim_Avail_Next_Pick']
    
    # Sort by VORP descending by default
    display_df = sim_results[display_cols].sort_values(by='VORP', ascending=False).reset_index(drop=True)
    
    # Style the dataframe
    st.dataframe(
        display_df.style.format({
            'ADP': '{:.1f}',
            'Projected_Points': '{:.1f}',
            'VORP': '{:.1f}',
            'Sim_Avail_Next_Pick': '{:.1%}'
        }).background_gradient(subset=['VORP'], cmap='Greens')
          .background_gradient(subset=['Sim_Avail_Next_Pick'], cmap='RdYlGn', vmin=0, vmax=1),
        use_container_width=True,
        height=500
    )

