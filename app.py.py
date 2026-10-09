import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fußball Unentschieden Analyse", layout="wide")

st.title("⚽ Fußball Unentschieden & Vorschau")

league = st.sidebar.selectbox(
    "Liga auswählen",
    ["1. Bundesliga", "2. Bundesliga", "Premier League"]
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

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

        # Nächster Spieltag Bundesliga
        next_gw = next((gw for gw in range(1, 35) if not any(m.get("matchIsFinished", False) for m in [m for m in matches if m.get("group", {}).get("groupOrderID") == gw])), None)
        if next_gw:
            st.subheader(f"🔮 Nächster Spieltag (ST {next_gw})")
            prev_col = f"ST {next_gw - 1}" if next_gw > 1 else None
            next_matches = [m for m in matches if m.get("group", {}).get("groupOrderID") == next_gw]
            
            for m in next_matches:
                h, a = m["team1"]["teamName"], m["team2"]["teamName"]
                h_draw = (prev_col and prev_col in df.columns and df.loc[h, prev_col] == "2")
                a_draw = (prev_col and prev_col in df.columns and df.loc[a, prev_col] == "2")
                
                h_disp = f"**🟡 {h}**" if h_draw else h
                a_disp = f"**🟡 {a}**" if a_draw else a
                st.markdown(f"* {h_disp} vs. {a_disp}")

    else:
        # Code für Premier League (FPL API)
        bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"

        resp_bootstrap = requests.get(bootstrap_url, headers=headers)
        bootstrap_data = resp_bootstrap.json()
        teams = {team["id"]: team["name"] for team in bootstrap_data.get("teams", [])}
        team_names = sorted(list(teams.values()))

        resp_fixtures = requests.get(fixtures_url, headers=headers)
        fixtures = resp_fixtures.json()

        matchweeks = [f"ST {i}" for i in range(1, 39)]
        df = pd.DataFrame("-", index=team_names, columns=matchweeks)

        for gw in range(1, 39):
            gw_fixtures = [f for f in fixtures if f.get("event") == gw]
            col_name = f"ST {gw}"
            for f in gw_fixtures:
                if f.get("finished", False) and f.get("team_h_score") is not None and f.get("team_a_score") is not None:
                    if int(f["team_h_score"]) == int(f["team_a_score"]):
                        home_team = teams.get(f["team_h"])
                        away_team = teams.get(f["team_a"])
                        if home_team in df.index and away_team in df.index:
                            df.loc[home_team, col_name] = "2"
                            df.loc[away_team, col_name] = "2"

        st.subheader("📊 Unentschieden-Matrix (2 = Unentschieden)")
        st.dataframe(df)

        # Nächster Spieltag Premier League
        next_gw = next((gw for gw in range(1, 39) if not any(f.get("finished", False) for f in [f for f in fixtures if f.get("event") == gw])), None)
        if next_gw:
            st.subheader(f"🔮 Nächster Spieltag (ST {next_gw})")
            prev_col = f"ST {next_gw - 1}" if next_gw > 1 else None
            next_fixtures = [f for f in fixtures if f.get("event") == next_gw]

            for f in next_fixtures:
                h = teams.get(f["team_h"])
                a = teams.get(f["team_a"])
                h_draw = (prev_col and prev_col in df.columns and df.loc[h, prev_col] == "2")
                a_draw = (prev_col and prev_col in df.columns and df.loc[a, prev_col] == "2")

                h_disp = f"**🟡 {h}**" if h_draw else h
                a_disp = f"**🟡 {a}**" if a_draw else a
                st.markdown(f"* {h_disp} vs. {a_disp}")