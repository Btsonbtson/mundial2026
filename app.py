import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import os

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Mundial 2026 Predictor App", page_icon="⚽", layout="wide")

# CSS Branding (FIFA Theme)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #f59e0b !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #1e3a8a; color: white; border-radius: 8px; border: 1px solid #f59e0b; width: 100%; }
    .stButton>button:hover { background-color: #3b82f6; color: white; }
    .chat-box { background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b; max-height: 250px; overflow-y: auto; }
    .odds-badge { background-color: #047857; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .group-container { background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# Εντοπισμός Αρχείου Excel
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(CURRENT_DIR, "Mundial 2026.xlsx")

if 'user' not in st.session_state:
    st.session_state.user = "BOIKOS"
if 'admin' not in st.session_state:
    st.session_state.admin = "BOIKOS"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [{"user": "System", "msg": "Το chat ενεργοποιήθηκε! Καλό τουρνουά!"}]

# 📅 ΠΡΑΓΜΑΤΙΚΕΣ ΗΜΕΡΟΜΗΝΙΕΣ ΕΝΑΡΞΗΣ MUNDIAL 2026 (ONLINE FEED)
# Οι αγώνες ξεκινούν κανονικά τον Ιούνιο του 2026
MATCH_TIMES = {
    5: datetime(2026, 6, 11, 22, 0, 0),  # MEXICO - SOUTH AFRICA (Έναρξη Μουντιάλ & Κλείδωμα Ομίλων)
    6: datetime(2026, 6, 12, 18, 0, 0),  # SOUTH KOREA - CZECHIA
    7: datetime(2026, 6, 12, 21, 0, 0),  # CANADA - BOSNIA & HERZ.
    8: datetime(2026, 6, 13, 0, 0, 0),   # SPAIN - ECUADOR
}

STOIXIMAN_ODDS = {
    5: {"1": "1.85", "X": "3.40", "2": "4.50"},
    6: {"1": "2.10", "X": "3.20", "2": "3.60"},
    7: {"1": "1.55", "X": "3.90", "2": "6.00"},
    8: {"1": "1.70", "X": "3.60", "2": "5.20"},
}

# Φόρτωση δεδομένων
wb_read = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
sheet_read = wb_read.active

# --- UI ΕΦΑΡΜΟΓΗΣ ---
st.title("🏆 MUNDIAL 2026 – AUTOMATED PREDICTOR")
st.subheader("BOIKOS / MAVROMICHALIS / CHOUSIADAS")

# Login Panels
col_u, col_a, col_t = st.columns(3)
with col_u:
    st.session_state.user = st.selectbox("👤 Είσαι ο παίκτης:", ["BOIKOS", "MAVROMICHALIS", "CHOUSIADAS"])
with col_a:
    st.write(f"👑 Admin: {st.session_state.admin}")
with col_t:
    st.metric("🕒 Ώρα Συστήματος", datetime.now().strftime("%d/%m/%Y %H:%M"))

# TABS
tab1, tab2 = st.tabs(["⚽ Αγώνες & Σκορ", "📊 Κατάταξη Ομίλων"])

# --- TAB 1: ΑΓΩΝΕΣ ---
with tab1:
    st.header("Προβλέψεις Σκορ Αγώνων")
    USER_COLS = {
        "BOIKOS": {"h": "N", "a": "P"},
        "MAVROMICHALIS": {"h": "U", "a": "W"},
        "CHOUSIADAS": {"h": "AB", "a": "AD"}
    }
    
    for r in range(5, 9):
        h_team = sheet_read[f"E{r}"].value
        a_team = sheet_read[f"G{r}"].value
        if not h_team: continue
        
        m_time = MATCH_TIMES.get(r, datetime(2026, 6, 15, 12, 0, 0))
        time_to_start = m_time - datetime.now()
        is_locked = time_to_start.total_seconds() <= 60
        
        wb_w = openpyxl.load_workbook(EXCEL_FILE)
        sh_w = wb_w.active
        curr_h = sh_w[f"{USER_COLS[st.session_state.user]['h']}{r}"].value or 0
        curr_a = sh_w[f"{USER_COLS[st.session_state.user]['a']}{r}"].value or 0
        
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 4, 3])
            with c1:
                st.markdown(f"**{h_team} vs {a_team}**")
                odds = STOIXIMAN_ODDS.get(r, {"1":"-","X":"-","2":"-"})
                st.markdown(f"<span class='odds-badge'>Stoiximan</span> 1:{odds['1']} X:{odds['X']} 2:{odds['2']}", unsafe_allow_html=True)
            with c2:
                st.write(f"📅 Σέντρα: {m_time.strftime('%d/%m %H:%M')}")
                if is_locked: st.error("🔒 Κλειδωμένο")
                else:
                    days = time_to_start.days
                    hours = time_to_start.seconds // 3600
                    st.info(f"⏳ Σε: {days}ημ. {hours}ώρ.")
            with c3:
                st.write("Η πρόβλεψή σου:")
                cc1, cc2 = st.columns(2)
                with cc1: ph = st.number_input(f"Σκορ {h_team}", 0, 10, int(curr_h), key=f"h_{r}", disabled=is_locked)
                with cc2: pa = st.number_input(f"Σκορ {a_team}", 0, 10, int(curr_a), key=f"a_{r}", disabled=is_locked)
                if not is_locked:
                    if st.button("💾 Αποθήκευση", key=f"s_{r}"):
                        sh_w[f"{USER_COLS[st.session_state.user]['h']}{r}"] = ph
                        sh_w[f"{USER_COLS[st.session_state.user]['a']}{r}"] = pa
                        wb_w.save(EXCEL_FILE)
                        st.success("Καταχωρήθηκε!")
            with c4:
                st.write("👀 Αποκάλυψη:")
                if is_locked:
                    st.write(f"BOIKOS: {sh_w[f'N{r}'].value or 0}-{sh_w[f'P{r}'].value or 0}")
                    st.write(f"MAVRO: {sh_w[f'U{r}'].value or 0}-{sh_w[f'W{r}'].value or 0}")
                    st.write(f"CHOUS: {sh_w[f'AB{r}'].value or 0}-{sh_w[f'AD{r}'].value or 0}")
                else:
                    st.warning("🔒 Κρυφό μέχρι το 1'")
        st.markdown("---")

# --- TAB 2: ΟΜΙΛΟΙ (ΠΛΗΡΩΣ ΔΙΟΡΘΩΜΕΝΟ & ΔΥΝΑΜΙΚΟ) ---
with tab2:
    st.header("📊 Προβλέψεις Τελικής Κατάταξης Ομίλων")
    
    # Χάρτης Ομίλων και των αρχικών στηλών τους στο Excel (GROUP A = AK(37), GROUP B = AP(42), κλπ.)
    GROUPS_MAP = {
        "GROUP A": 37, "GROUP B": 42, "GROUP C": 47, "GROUP D": 52,
        "GROUP E": 57, "GROUP F": 62, "GROUP G": 67, "GROUP H": 72,
        "GROUP I": 77, "GROUP J": 82, "GROUP K": 87, "GROUP L": 92
    }
    
    selected_group = st.selectbox("🗂️ Επιλέξτε Όμιλο για πρόβλεψη:", list(GROUPS_MAP.keys()))
    col_letter_idx = GROUPS_MAP[selected_group]
    
    # Το γενικό κλείδωμα των ομίλων ορίζεται από το 1ο ματς του Μουντιάλ (11 Ιουνίου 2026)
    world_cup_start = datetime(2026, 6, 11, 22, 0, 0)
    time_to_lock = world_cup_start - datetime.now()
    group_locked = time_to_lock.total_seconds() <= 0
    
    if group_locked:
        st.error("🔒 Οι προβλέψεις ομίλων έχουν κλειδώσει (Το Μουντιάλ ξεκίνησε)!")
    else:
        st.info(f"⏳ Χρόνος μέχρι το κλείδωμα των Ομίλων: {time_to_lock.days} ημέρες, {time_to_lock.seconds // 3600} ώρες")
        
    # Σειρές στο Excel για κάθε παίκτη (Στήλη + 1, δηλαδή AL, AQ, AV κλπ.)
    PLAYER_OFFSETS = {"BOIKOS": 11, "MAVROMICHALIS": 17, "CHOUSIADAS": 23}
    
    # Διαβάζουμε τις 4 ομάδες του επιλεγμένου ομίλου από τις σειρές 5 έως 8 της σωστής στήλης (AL=38, AQ=43, κλπ.)
    group_teams = []
    for r in range(5, 9):
        val = sheet_read.cell(row=r, column=col_letter_idx + 1).value
        if val: group_teams.append(str(val).strip())
        
    if len(group_teams) >= 4:
        st.markdown(f"### Διαχείριση {selected_group}")
        
        wb_g = openpyxl.load_workbook(EXCEL_FILE)
        sh_g = wb_g.active
        start_row = PLAYER_OFFSETS[st.session_state.user]
        
        # Διαβάζουμε τι έχει ήδη αποθηκευμένο ο παίκτης στο Excel
        current_preds = []
        for i in range(4):
            val = sh_g.cell(row=start_row+i, column=col_letter_idx + 1).value
            current_preds.append(str(val).strip() if val else group_teams[i])
            
        # Εμφάνιση των Dropdown επιλογών
        with st.container():
            st.markdown("<div class='group-container'>", unsafe_allow_html=True)
            pos1 = st.selectbox("1η Θέση (Πρόκριση):", group_teams, index=group_teams.index(current_preds[0]) if current_preds[0] in group_teams else 0, disabled=group_locked, key=f"g1_{selected_group}")
            pos2 = st.selectbox("2η Θέση (Πρόκριση):", group_teams, index=group_teams.index(current_preds[1]) if current_preds[1] in group_teams else 1, disabled=group_locked, key=f"g2_{selected_group}")
            pos3 = st.selectbox("3η Θέση:", group_teams, index=group_teams.index(current_preds[2]) if current_preds[2] in group_teams else 2, disabled=group_locked, key=f"g3_{selected_group}")
            pos4 = st.selectbox("4η Θέση:", group_teams, index=group_teams.index(current_preds[3]) if current_preds[3] in group_teams else 3, disabled=group_locked, key=f"g4_{selected_group}")
            
            if not group_locked:
                if st.button("💾 Αποθήκευση Κατάταξης", key=f"save_g_{selected_group}"):
                    if len({pos1, pos2, pos3, pos4}) < 4:
                        st.error("❌ Σφάλμα: Έχεις επιλέξει την ίδια ομάδα σε παραπάνω από μία θέσεις!")
                    else:
                        sh_g.cell(row=start_row, column=col_letter_idx + 1).value = pos1
                        sh_g.cell(row=start_row+1, column=col_letter_idx + 1).value = pos2
                        sh_g.cell(row=start_row+2, column=col_letter_idx + 1).value = pos3
                        sh_g.cell(row=start_row+3, column=col_letter_idx + 1).value = pos4
                        wb_g.save(EXCEL_FILE)
                        st.success(f"Η πρόβλεψη για τον {selected_group} αποθηκεύτηκε στο Excel!")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning(f"Δεν βρέθηκαν ομάδες στο Excel για τον {selected_group}. Ελέγξτε τις στήλες.")

# --- 📊 LIVE LEADERBOARD ---
st.write("---")
st.header("📊 Live Βαθμολογία (Από τις φόρμουλες του Excel)")
score_boikos, score_mavro, score_chous = 0, 0, 0

for r in range(5, 9):
    h_val = sheet_read[f"I{r}"].value
    has_real_score = (h_val is not None) and (str(h_val).strip() != "-") and (str(h_val).strip() != "")
    if has_real_score:
        score_boikos += float(sheet_read[f"S{r}"].value or 0)
        score_mavro += float(sheet_read[f"Z{r}"].value or 0)
        score_chous += float(sheet_read[f"AG{r}"].value or 0)

leaderboard_data = {
    "Παίκτης": ["BOIKOS", "MAVROMICHALIS", "CHOUSIADAS"],
    "Συνολικοί Πόντοι": [score_boikos, score_mavro, score_chous]
}
df_lb = pd.DataFrame(leaderboard_data).sort_values(by="Συνολικοί Πόντοι", ascending=False)
st.table(df_lb)

# --- CHAT ROOM ---
st.write("---")
st.header("💬 Live Chat")
chat_html = "<div class='chat-box'>"
for chat in st.session_state.chat_history:
    chat_html += f"<p><b>[{chat['user']}]:</b> {chat['msg']}</p>"
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

with st.form(key="ch_form", clear_on_submit=True):
    msg = st.text_input("Γράψε την ατάκα σου:")
    if st.form_submit_button("Αποστολή 🚀") and msg:
        st.session_state.chat_history.append({"user": st.session_state.user, "msg": msg})
        st.rerun()