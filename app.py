import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Mundial 2026 Predictor", page_icon="⚽", layout="wide")

# CSS Branding
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #f59e0b !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #1e3a8a; color: white; border-radius: 8px; border: 1px solid #f59e0b; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #3b82f6; color: white; }
    .chat-box { background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b; max-height: 250px; overflow-y: auto; }
    .odds-badge { background-color: #047857; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .group-container { background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
    .login-container { max-width: 450px; margin: 100px auto; padding: 30px; background-color: #1e293b; border-radius: 10px; border: 2px solid #f59e0b; }
    </style>
""", unsafe_allow_html=True)

PASSWORDS = {"1453": "BOIKOS", "1821": "MAVROMICHALIS", "1940": "CHOUSIADAS"}

if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = [{"user": "System", "msg": "Το chat ενεργοποιήθηκε!"}]
if 'temp_matches' not in st.session_state: st.session_state.temp_matches = {}
if 'temp_groups' not in st.session_state: st.session_state.temp_groups = {}

MATCH_TIMES = {
    4: datetime(2026, 6, 11, 22, 0, 0),  # MEXICO - SOUTH AFRICA (Σειρά 4 / Δείκτης 3)
    5: datetime(2026, 6, 12, 18, 0, 0),  # SOUTH KOREA - CZECHIA
    6: datetime(2026, 6, 12, 21, 0, 0),  # CANADA - BOSNIA & HERZ.
    7: datetime(2026, 6, 13, 0, 0, 0),   # SPAIN - ECUADOR
}
STOIXIMAN_ODDS = {
    4: {"1": "1.85", "X": "3.40", "2": "4.50"},
    5: {"1": "2.10", "X": "3.20", "2": "3.60"},
    6: {"1": "1.55", "X": "3.90", "2": "6.00"},
    7: {"1": "1.70", "X": "3.60", "2": "5.20"},
}

# 🔗 Σύνδεση με το Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df_sheet = conn.read(ttl="0m") # ttl="0m" για να διαβάζει ΠΑΝΤΑ live δεδομένα

# --- LOGIN PANEL ---
if st.session_state.logged_in_user is None:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.write("## 🔒 Είσοδος στο Mundial Predictor")
    input_pass = st.text_input("Εισάγετε τον Προσωπικό σας Κωδικό:", type="password")
    if st.button("Είσοδος 🚀"):
        if input_pass in PASSWORDS:
            st.session_state.logged_in_user = PASSWORDS[input_pass]
            
            # 🔄 ΑΥΤΟΜΑΤΗ ΕΝΗΜΕΡΩΣΗ ΣΤΟ ΑΡΧΙΚΟ ΑΝΟΙΓΜΑ (Τραβάει τις ήδη καταχωρημένες προβλέψεις)
            USER_OFFSETS = {"BOIKOS": (13, 15), "MAVROMICHALIS": (20, 22), "CHOUSIADAS": (27, 29)}
            h_col, a_col = USER_OFFSETS[st.session_state.logged_in_user]
            for r in range(4, 8):
                try:
                    val_h = df_sheet.iloc[r-1, h_col]
                    val_a = df_sheet.iloc[r-1, a_col]
                    st.session_state.temp_matches[r] = {
                        "h": int(float(val_h)) if pd.notna(val_h) and str(val_h).strip() != "" else 0,
                        "a": int(float(val_a)) if pd.notna(val_a) and str(val_a).strip() != "" else 0
                    }
                except:
                    st.session_state.temp_matches[r] = {"h": 0, "a": 0}
            st.session_state.temp_groups = {} # Reset ομίλων για να τραβήξει τους καταχωρημένους live
            st.rerun()
        else: st.error("❌ Λάθος Κωδικός!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.title("🏆 MUNDIAL 2026 – CLOUD PREDICTOR")
st.subheader(f"👤 Παίκτης: {st.session_state.logged_in_user}")

# Κουμπί Έξοδος & Αποθήκευση
if st.button("🚪 ΕΞΟΔΟΣ & ΑΥΤΟΜΑΤΗ ΑΠΟΘΗΚΕΥΣΗ ΣΤΟ CLOUD"):
    with st.spinner("Γίνεται αποθήκευση στο Google Sheet..."):
        # 1. Ενημέρωση Αγώνων
        USER_OFFSETS = {"BOIKOS": (13, 15), "MAVROMICHALIS": (20, 22), "CHOUSIADAS": (27, 29)}
        h_col, a_col = USER_OFFSETS[st.session_state.logged_in_user]
        for r_idx, scores in st.session_state.temp_matches.items():
            df_sheet.iloc[r_idx-1, h_col] = int(scores["h"])
            df_sheet.iloc[r_idx-1, a_col] = int(scores["a"])
            
        # 2. Ενημέρωση Ομίλων
        PLAYER_OFFSETS = {"BOIKOS": 10, "MAVROMICHALIS": 16, "CHOUSIADAS": 22}
        start_row = PLAYER_OFFSETS[st.session_state.logged_in_user]
        for col_idx, positions in st.session_state.temp_groups.items():
            df_sheet.iloc[start_row, col_idx] = positions[0]
            df_sheet.iloc[start_row+1, col_idx] = positions[1]
            df_sheet.iloc[start_row+2, col_idx] = positions[2]
            df_sheet.iloc[start_row+3, col_idx] = positions[3]
            
        # 🚀 LIVE ΕΓΓΡΑΦΗ ΣΤΟ GOOGLE SHEET
        conn.update(data=df_sheet)
        
        st.session_state.temp_matches = {}
        st.session_state.temp_groups = {}
        st.session_state.logged_in_user = None
        st.success("Οι αλλαγές αποθηκεύτηκαν!")
        st.rerun()

st.write("---")
tab1, tab2 = st.tabs(["⚽ Αγώνες & Σκορ", "📊 Κατάταξη Ομίλων"])

# --- TAB 1: ΑΓΩΝΕΣ ---
with tab1:
    st.header("Προβλέψεις Σκορ Αγώνων")
    for r in range(4, 8):
        h_team = df_sheet.iloc[r-1, 4] # Στήλη E
        a_team = df_sheet.iloc[r-1, 6] # Στήλη G
        if pd.isna(h_team): continue
        m_time = MATCH_TIMES.get(r, datetime(2026, 6, 15, 12, 0, 0))
        time_to_start = m_time - datetime.now()
        is_locked = time_to_start.total_seconds() <= 60
        
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 4, 3])
            with c1:
                st.markdown(f"**{h_team} vs {a_team}**")
                odds = STOIXIMAN_ODDS.get(r, {"1":"-","X":"-","2":"-"})
                st.markdown(f"<span class='odds-badge'>Stoiximan</span> 1:{odds['1']} X:{odds['X']} 2:{odds['2']}", unsafe_allow_html=True)
            with c2:
                st.write(f"📅 Σέντρα: {m_time.strftime('%d/%m %H:%M')}")
                if is_locked: st.error("🔒 Κλειδωμένο")
                else: st.info(f"⏳ Σε: {time_to_start.days}ημ. {time_to_start.seconds // 3600}ώρ.")
            with c3:
                cc1, cc2 = st.columns(2)
                with cc1: new_h = st.number_input(f"Σκορ {h_team}", 0, 10, int(st.session_state.temp_matches[r]["h"]), key=f"h_{r}", disabled=is_locked)
                with cc2: new_a = st.number_input(f"Σκορ {a_team}", 0, 10, int(st.session_state.temp_matches[r]["a"]), key=f"a_{r}", disabled=is_locked)
                st.session_state.temp_matches[r] = {"h": new_h, "a": new_a}
            with c4:
                st.write("👀 Αποκάλυψη:")
                if is_locked:
                    st.write(f"BOIKOS: {df_sheet.iloc[r-1, 13] or 0}-{df_sheet.iloc[r-1, 15] or 0}")
                    st.write(f"MAVRO: {df_sheet.iloc[r-1, 20] or 0}-{df_sheet.iloc[r-1, 22] or 0}")
                    st.write(f"CHOUS: {df_sheet.iloc[r-1, 27] or 0}-{df_sheet.iloc[r-1, 29] or 0}")
                else: st.warning("🔒 Κρυφό μέχρι το 1'")
        st.markdown("---")

# --- TAB 2: ΟΜΙΛΟΙ ---
with tab2:
    st.header("📊 Προβλέψεις Τελικής Κατάταξης Ομίλων")
    GROUPS_MAP = {
        "GROUP A": 37, "GROUP B": 42, "GROUP C": 47, "GROUP D": 52,
        "GROUP E": 57, "GROUP F": 62, "GROUP G": 67, "GROUP H": 72,
        "GROUP I": 77, "GROUP J": 82, "GROUP K": 87, "GROUP L": 92
    }
    selected_group = st.selectbox("🗂️ Επιλέξτε Όμιλο:", list(GROUPS_MAP.keys()))
    col_idx = GROUPS_MAP[selected_group]
    PLAYER_OFFSETS = {"BOIKOS": 10, "MAVROMICHALIS": 16, "CHOUSIADAS": 22}
    start_row = PLAYER_OFFSETS[st.session_state.logged_in_user]
    
    group_teams = []
    for r in range(4, 8):
        val = df_sheet.iloc[r-1, col_idx]
        if pd.notna(val): group_teams.append(str(val).strip())
        
    if len(group_teams) == 4:
        if col_idx not in st.session_state.temp_groups:
            st.session_state.temp_groups[col_idx] = [
                str(df_sheet.iloc[start_row, col_idx]).strip() if pd.notna(df_sheet.iloc[start_row, col_idx]) else group_teams[0],
                str(df_sheet.iloc[start_row+1, col_idx]).strip() if pd.notna(df_sheet.iloc[start_row+1, col_idx]) else group_teams[1],
                str(df_sheet.iloc[start_row+2, col_idx]).strip() if pd.notna(df_sheet.iloc[start_row+2, col_idx]) else group_teams[2],
                str(df_sheet.iloc[start_row+3, col_idx]).strip() if pd.notna(df_sheet.iloc[start_row+3, col_idx]) else group_teams[3]
            ]
        g_preds = st.session_state.temp_groups[col_idx]
        
        p1 = st.selectbox("1η Θέση:", group_teams, index=group_teams.index(g_preds[0]) if g_preds[0] in group_teams else 0, key=f"g1_{selected_group}")
        p2 = st.selectbox("2η Θέση:", group_teams, index=group_teams.index(g_preds[1]) if g_preds[1] in group_teams else 1, key=f"g2_{selected_group}")
        p3 = st.selectbox("3η Θέση:", group_teams, index=group_teams.index(g_preds[2]) if g_preds[2] in group_teams else 2, key=f"g3_{selected_group}")
        p4 = st.selectbox("4η Θέση:", group_teams, index=group_teams.index(g_preds[3]) if g_preds[3] in group_teams else 3, key=f"g4_{selected_group}")
        st.session_state.temp_groups[col_idx] = [p1, p2, p3, p4]
    else: st.error(f"❌ Δεν βρέθηκαν 4 ομάδες στη στήλη του ομίλου.")

# --- 📊 LIVE LEADERBOARD ---
st.write("---")
st.header("📊 Live Βαθμολογία (Από τις φόρμουλες του Excel)")
score_boikos, score_mavro, score_chous = 0.0, 0.0, 0.0
for r in range(4, 8):
    h_val = df_sheet.iloc[r-1, 8] # Στήλη I
    if pd.notna(h_val) and str(h_val).strip() != "-":
        score_boikos += float(df_sheet.iloc[r-1, 18] or 0) # Στήλη S
        score_mavro += float(df_sheet.iloc[r-1, 25] or 0)  # Στήλη Z
        score_chous += float(df_sheet.iloc[r-1, 32] or 0)  # Στήλη AG
st.table(pd.DataFrame({"Παίκτης": ["BOIKOS", "MAVROMICHALIS", "CHOUSIADAS"], "Συνολικοί Πόντοι": [score_boikos, score_mavro, score_chous]}).sort_values(by="Συνολικοί Πόντοι", ascending=False))

# --- CHAT ROOM ---
st.write("---")
st.header("💬 Live Chat")
chat_html = "<div class='chat-box'>"
for chat in st.session_state.chat_history: chat_html += f"<p><b>[{chat['user']}]:</b> {chat['msg']}</p>"
st.markdown(chat_html + "</div>", unsafe_allow_html=True)
with st.form(key="ch_form", clear_on_submit=True):
    msg = st.text_input("Γράψε την ατάκα σου:")
    if st.form_submit_button("Αποστολή 🚀") and msg:
        st.session_state.chat_history.append({"user": st.session_state.logged_in_user, "msg": msg})
        st.rerun()
