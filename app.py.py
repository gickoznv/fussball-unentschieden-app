import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fußball Unentschieden Analyse", layout="wide")

st.title("⚽ Fußball Unentschieden & Vorschau")

league = st.sidebar.selectbox(
    "Liga auswählen",
    ["1. Bundesliga", "2. Bundesliga", "Premier League"]
)

if league == "1. Bundesliga":
    season = "2026"
    url = f"https://api.openligadb.de/getmatchdata/bl1/{season}"
    st.header(f"1. Bundesliga - Saison {season}/2027")
elif league == "2. Bundesliga":
    season = "2026"
    url = f"https://api.openligadb.de/getmatchdata/bl2/{season}"
    st.header(f"2. Bundesliga - Saison {season}/2027")
else:
    st.header("Premier League")

# Datenauswertung durchführen
if st.button("Daten laden / Aktualisieren"):
    if "Bundesliga" in league:
        resp = requests.get(url)
        matches = resp.json()

        team_set = {m["team1"]["teamName"] for m in matches} | {m["team2"]["teamName"] for m in matches}
        team_names = sorted(list(team_set))
        matchweeks = [f"ST {i}" for i in range(1, 35)]
        df = pd.DataFrame("-", index=team_names, columns=matchweeks)

        for gw in range(1, 35):
            gw_matches = [m for m in matches if m.get("group", {}).get("groupOrderID") == gw]
            col_name = f"ST {gw}"
            for m in gw_matches:
                if m.get("matchIsFinished", False) and m.get("matchResults"):
                    res = [r for r in m["matchResults"] if r.get("resultTypeID") == 2] or [m["matchResults"][-1]]
                    if int(res[0]["pointsTeam1"]) == int(res[0]["pointsTeam2"]):
                        df.loc[m["team1"]["teamName"], col_name] = "2"
                        df.loc[m["team2"]["teamName"], col_name] = "2"

        st.subheader("📊 Unentschieden-Matrix (2 = Unentschieden)")
        st.dataframe(df)

        # Nächster Spieltag
        next_gw = next((gw for gw in range(1, 35) if not any(m.get("matchIsFinished", False) for m in [m for m in matches if m.get("group", {}).get("groupOrderID") == gw])), None)
        if next_gw:
            st.subheader(f"🔮 Nächster Spieltag (ST {next_gw})")
            prev_col = f"ST {next_gw - 1}" if next_gw > 1 else None
            next_matches = [m for m in matches if m.get("group", {}).get("groupOrderID") == next_gw]
            
            for m in next_matches:
                h, a = m["team1"]["teamName"], m["team2"]["teamName"]
                h_draw = (prev_col and df.loc[h, prev_col] == "2")
                a_draw = (prev_col and df.loc[a, prev_col] == "2")
                
                h_disp = f"**🟡 {h}**" if h_draw else h
                a_disp = f"**🟡 {a}**" if a_draw else a
                st.markdown(f"* {h_disp} vs. {a_disp}")