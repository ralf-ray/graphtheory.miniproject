import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import random
import os

# Team abbreviation mapping (some teams may require manual addition)
team_abbr_map = {
    "Boston Celtics": "BOS",
    "Denver Nuggets": "DEN",
    "Golden State Warriors": "GSW",
    "Milwaukee Bucks": "MIL",
    "Los Angeles Lakers": "LAL",
    "Toronto Raptors": "TOR",
    "Cleveland Cavaliers": "CLE",
    "San Antonio Spurs": "SAS",
    "Miami Heat": "MIA",
    "Chicago Bulls": "CHI",
    "Philadelphia 76ers": "PHI",
    "New York Knicks": "NYK",
    "Houston Rockets": "HOU",
    "Seattle SuperSonics": "SEA",  # Historically used; currently OKC Thunder, but historical data uses SEA
    "Washington Bullets": "WSB",   # Later changed to WAS
    "Portland Trail Blazers": "POR",
    "Utah Stars": None,            # ABA team, requires manual handling
    "Indiana Pacers": "IND",
    "Oakland Oaks": None,          # ABA team
    "Pittsburgh Pipers": None,     # ABA team
    "Kentucky Colonels": None,
    # ...
}

def get_year_from_season(season_str):
    """
    Convert a season string to its ending year.
    For example:
      '2022-23' -> 2023
      '2023-24' -> 2024
      '1999-00' -> 2000
    For cases like 'Dec-11', returns None (manual handling required).
    """
    parts = season_str.split('-')
    if len(parts) != 2:
        return None
    try:
        end_year = int(parts[1])
        if end_year < 50:
            end_year += 2000
        else:
            end_year += 1900
        return end_year
    except Exception as e:
        print(f"Error parsing season {season_str}: {e}")
        return None

def fetch_roster(team_abbr, year, session):
    """
    Attempt to fetch the roster for the specified team and season from Basketball-Reference.
    First, try to parse the JSON-LD data; if that fails, try to parse the roster table from HTML.
    """
    url = f"https://www.basketball-reference.com/teams/{team_abbr}/{year}.html"
    print(f"\nFetching roster from: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = session.get(url, headers=headers, timeout=10)
    except Exception as e:
        print("Request error:", e)
        return []
    # Sleep randomly for 2-4 seconds to reduce request frequency
    time.sleep(random.uniform(2, 4))
    if response.status_code != 200:
        print(f"Unable to access URL, status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 1. First, try to parse the JSON-LD data
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            # If data is a dictionary and its @type is SportsTeam, attempt to extract the roster
            if isinstance(data, dict) and data.get("@type") == "SportsTeam":
                athletes = data.get("athlete", [])
                if isinstance(athletes, list) and athletes:
                    players = [athlete.get("name") for athlete in athletes if athlete.get("name")]
                    if players:
                        print("Roster obtained via JSON-LD.")
                        return players
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
    
    # 2. If JSON-LD extraction fails, try parsing the HTML roster table
    roster_table = soup.find("table", {"id": "roster"})
    if not roster_table:
        print("Roster table not found.")
        return []
    
    players = []
    tbody = roster_table.find("tbody")
    for row in tbody.find_all("tr"):
        player_cell = row.find("th", {"data-stat": "player"})
        if player_cell:
            player_name = player_cell.get_text(strip=True)
            players.append(player_name)
    if players:
        print("Roster obtained via HTML table.")
    return players

# Create a Session object to persist HTTP connections
session = requests.Session()

# Example: Season-Team mapping
seasons_teams = [
    ("2023-24", "Boston Celtics"),
    ("2022-23", "Denver Nuggets"),
    ("2021-22", "Golden State Warriors"),
    ("2020-21", "Milwaukee Bucks"),
    ("2019-20", "Los Angeles Lakers"),
    ("2018-19", "Toronto Raptors"),
    ("2017-18", "Golden State Warriors"),
    ("2016-17", "Golden State Warriors"),
    ("2015-16", "Cleveland Cavaliers"),
    ("2014-15", "Golden State Warriors"),
    ("2013-14", "San Antonio Spurs"),
    ("2012-13", "Miami Heat"),
    ("Dec-11", "Miami Heat"),
    ("Nov-10", "Dallas Mavericks"),
    ("Oct-09", "Los Angeles Lakers"),
    ("Sep-08", "Los Angeles Lakers"),
    ("Aug-07", "Boston Celtics"),
    ("Jul-06", "San Antonio Spurs"),
    ("Jun-05", "Miami Heat"),
    ("May-04", "San Antonio Spurs"),
    ("Apr-03", "Detroit Pistons"),
    ("Mar-02", "San Antonio Spurs"),
    ("Feb-01", "Los Angeles Lakers"),
    ("Jan-00", "Los Angeles Lakers"),
    ("1999-00", "Los Angeles Lakers"),
    ("1998-99", "San Antonio Spurs"),
    ("1997-98", "Chicago Bulls"),
    ("1996-97", "Chicago Bulls"),
    ("1995-96", "Chicago Bulls"),
    ("1994-95", "Houston Rockets"),
    ("1993-94", "Houston Rockets"),
    ("1992-93", "Chicago Bulls"),
    ("1991-92", "Chicago Bulls"),
    ("1990-91", "Chicago Bulls"),
    ("1989-90", "Chicago Bulls"),
    ("1988-89", "Chicago Bulls"),
    ("1987-88", "Los Angeles Lakers"),
    ("1986-87", "Los Angeles Lakers"),
    ("1985-86", "Boston Celtics"),
    ("1984-85", "Los Angeles Lakers"),
    ("1983-84", "Boston Celtics"),
    ("1982-83", "Philadelphia 76ers"),
    ("1981-82", "Los Angeles Lakers"),
    ("1980-81", "Boston Celtics"),
    ("1979-80", "Los Angeles Lakers"),
    ("1978-79", "Seattle SuperSonics"),
    ("1977-78", "Washington Bullets"),
    ("1976-77", "Portland Trail Blazers"),
    ("1975-76", "Boston Celtics"),
    ("1975-76", "New York Nets"),
    ("1974-75", "Golden State Warriors"),
    ("1974-75", "Kentucky Colonels"),
    ("1973-74", "Boston Celtics"),
    ("1973-74", "New York Nets"),
    ("1972-73", "New York Knicks"),
    ("1972-73", "Indiana Pacers"),
    ("1971-72", "Los Angeles Lakers"),
    ("1971-72", "Indiana Pacers"),
    ("1970-71", "Milwaukee Bucks"),
    ("1970-71", "Utah Stars"),
    ("1969-70", "New York Knicks"),
    ("1969-70", "Indiana Pacers"),
    ("1968-69", "Boston Celtics"),
    ("1968-69", "Oakland Oaks"),
    ("1967-68", "Boston Celtics"),
    ("1967-68", "Pittsburgh Pipers"),
    ("1966-67", "Philadelphia 76ers"),
    ("1965-66", "Boston Celtics"),
    ("1964-65", "Boston Celtics"),
    ("1963-64", "Boston Celtics"),
    ("1962-63", "Boston Celtics"),
    ("1961-62", "Boston Celtics"),
    ("1960-61", "Boston Celtics"),
    ("1959-60", "Boston Celtics"),
    ("1958-59", "Boston Celtics"),
    ("1957-58", "St. Louis Hawks")
]

results = []
for season_str, team_name in seasons_teams:
    end_year = get_year_from_season(season_str)
    if not end_year:
        print(f"Unable to parse season: {season_str}")
        continue
    team_abbr = team_abbr_map.get(team_name, None)
    if not team_abbr:
        print(f"Team {team_name} is missing an abbreviation mapping; manual handling is required.")
        continue
    players = fetch_roster(team_abbr, end_year, session)
    if not players:
        print(f"No roster fetched for {team_name} {season_str}.")
    for p in players:
        results.append({
            "Season": season_str,
            "Team": team_name,
            "Year": end_year,
            "Player": p
        })

df_results = pd.DataFrame(results)
output_file = "nba_champions_rosters.xlsx"
df_results.to_excel(output_file, index=False)
print(f"\nGenerated {output_file} containing the rosters for the specified season-team entries.")
print("Current working directory:", os.getcwd())
print("Sample Results Data:")
print(df_results.head(10))
