"""Download real passing data from StatsBomb Open Data."""

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_statsbomb_data():
    """Download real match event data from StatsBomb open data."""
    try:
        from statsbombpy import sb
    except ImportError:
        print("ERROR: pip install statsbombpy")
        return None

    print("Fetching available competitions...")
    competitions = sb.competitions()
    print(f"Found {len(competitions)} competitions")

    # Find free competitions (World Cup, FA Women's Super League, etc.)
    free_comps = competitions[
        competitions["match_available_360"].notna()
        | competitions["match_available"].notna()
    ]
    print(f"\nFree competitions available: {len(free_comps)}")

    # Filter for men's competitions that might have Manchester United or similar data
    # Let's use FA Cup or Club World Cup which might have Man Utd
    premierLeague = free_comps[free_comps["country_name"] == "England"]
    print(f"\nEngland competitions: {len(premierLeague)}")
    print(
        premierLeague[["competition_name", "season_name", "country_name"]]
        .head(10)
        .to_string()
    )

    # Try to get Premier League matches
    try:
        # Get competition ID for Premier League
        pl_comps = premierLeague[premierLeague["competition_name"] == "Premier League"]
        if len(pl_comps) > 0:
            comp_id = pl_comps.iloc[0]["competition_id"]
            season_id = pl_comps.iloc[0]["season_id"]
            print(
                f"\nFetching Premier League matches (comp={comp_id}, season={season_id})..."
            )
            matches = sb.matches(competition_id=comp_id, season_id=season_id)
            print(f"Found {len(matches)} matches")

            # Find Manchester United matches
            manu_matches = matches[
                (matches["home_team"] == "Manchester United")
                | (matches["away_team"] == "Manchester United")
            ]
            print(f"Manchester United matches: {len(manu_matches)}")

            if len(manu_matches) > 0:
                # Get first match events
                match_id = manu_matches.iloc[0]["match_id"]
                home_team = manu_matches.iloc[0]["home_team"]
                away_team = manu_matches.iloc[0]["away_team"]
                match_date = manu_matches.iloc[0]["match_date"]
                print(
                    f"\nFetching events for: {home_team} vs {away_team} ({match_date})..."
                )
                events = sb.events(match_id=match_id)
                print(f"Total events: {len(events)}")

                # Filter passes
                passes = events[events["type"] == "Pass"].copy()
                print(f"Total passes: {len(passes)}")

                # Extract passing network data
                passing_data = []
                for _, event in passes.iterrows():
                    passer = event.get("player", "Unknown")
                    receiver_name = None

                    # Try to get receiver from pass recipient
                    if "pass_recipient" in event and pd.notna(event["pass_recipient"]):
                        receiver_name = event["pass_recipient"]
                    elif "pass_end_location" in event and pd.notna(
                        event["pass_end_location"]
                    ):
                        # Try to find receiver from next event
                        continue

                    if receiver_name and passer != receiver_name:
                        passing_data.append(
                            {
                                "passer": passer,
                                "receiver": receiver_name,
                                "x": event.get("location", [0, 0])[0]
                                if isinstance(event.get("location"), list)
                                else 0,
                                "y": event.get("location", [0, 0])[1]
                                if isinstance(event.get("location"), list)
                                else 0,
                                "end_x": event.get("pass_end_location", [0, 0])[0]
                                if isinstance(event.get("pass_end_location"), list)
                                else 0,
                                "end_y": event.get("pass_end_location", [0, 0])[1]
                                if isinstance(event.get("pass_end_location"), list)
                                else 0,
                                "pass_outcome": event.get("pass_outcome", "Complete"),
                                "pass_length": event.get("pass_length", 0),
                                "pass_angle": event.get("pass_angle", 0),
                                "minute": event.get("minute", 0),
                                "second": event.get("second", 0),
                                "team": event.get("team", ""),
                                "match_id": match_id,
                                "match_date": str(match_date),
                                "opponent": away_team
                                if home_team == "Manchester United"
                                else home_team,
                            }
                        )

                df_passes = pd.DataFrame(passing_data)
                print(f"\nPassing network edges: {len(df_passes)}")

                # Save raw data
                output_file = DATA_DIR / "statsbomb_passes.csv"
                df_passes.to_csv(output_file, index=False)
                print(f"Saved to: {output_file}")

                # Also save match info
                match_info = {
                    "match_id": match_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "match_date": str(match_date),
                    "competition": "Premier League",
                    "season": str(pl_comps.iloc[0]["season_name"]),
                    "total_events": len(events),
                    "total_passes": len(passes),
                    "passing_edges": len(df_passes),
                }
                with open(DATA_DIR / "match_info.json", "w") as f:
                    json.dump(match_info, f, indent=2)

                print(f"\nMatch info saved to: {DATA_DIR / 'match_info.json'}")
                return df_passes

    except Exception as e:
        print(f"Error fetching Premier League: {e}")
        import traceback

        traceback.print_exc()

    # Fallback: Use World Cup data which is definitely free
    print("\nTrying World Cup data as fallback...")
    try:
        wc_comps = competitions[competitions["competition_name"] == "FIFA World Cup"]
        if len(wc_comps) > 0:
            wc_2022 = wc_comps[wc_comps["season_name"] == "2022"]
            if len(wc_2022) > 0:
                comp_id = wc_2022.iloc[0]["competition_id"]
                season_id = wc_2022.iloc[0]["season_id"]
                print("Fetching World Cup 2022 matches...")
                matches = sb.matches(competition_id=comp_id, season_id=season_id)
                print(f"Found {len(matches)} matches")

                # Get a good match with lots of passes
                match_id = matches.iloc[0]["match_id"]
                home = matches.iloc[0]["home_team"]
                away = matches.iloc[0]["away_team"]
                print(f"Fetching events for: {home} vs {away}...")

                events = sb.events(match_id=match_id)
                passes = events[events["type"] == "Pass"].copy()
                print(f"Total passes: {len(passes)}")

                passing_data = []
                for _, event in passes.iterrows():
                    passer = event.get("player", "Unknown")
                    receiver_name = None
                    if "pass_recipient" in event and pd.notna(event["pass_recipient"]):
                        receiver_name = event["pass_recipient"]

                    if receiver_name and passer != receiver_name:
                        passing_data.append(
                            {
                                "passer": passer,
                                "receiver": receiver_name,
                                "x": event.get("location", [0, 0])[0]
                                if isinstance(event.get("location"), list)
                                else 0,
                                "y": event.get("location", [0, 0])[1]
                                if isinstance(event.get("location"), list)
                                else 0,
                                "end_x": event.get("pass_end_location", [0, 0])[0]
                                if isinstance(event.get("pass_end_location"), list)
                                else 0,
                                "end_y": event.get("pass_end_location", [0, 0])[1]
                                if isinstance(event.get("pass_end_location"), list)
                                else 0,
                                "pass_outcome": event.get("pass_outcome", "Complete"),
                                "pass_length": event.get("pass_length", 0),
                                "pass_angle": event.get("pass_angle", 0),
                                "minute": event.get("minute", 0),
                                "second": event.get("second", 0),
                                "team": event.get("team", ""),
                                "match_id": match_id,
                                "match_date": str(
                                    matches.iloc[0].get("match_date", "")
                                ),
                                "opponent": away
                                if home != event.get("team", "")
                                else home,
                            }
                        )

                df_passes = pd.DataFrame(passing_data)
                print(f"Passing network edges: {len(df_passes)}")

                output_file = DATA_DIR / "statsbomb_passes.csv"
                df_passes.to_csv(output_file, index=False)
                print(f"Saved to: {output_file}")

                match_info = {
                    "match_id": match_id,
                    "home_team": home,
                    "away_team": away,
                    "competition": "FIFA World Cup 2022",
                    "total_events": len(events),
                    "total_passes": len(passes),
                    "passing_edges": len(df_passes),
                }
                with open(DATA_DIR / "match_info.json", "w") as f:
                    json.dump(match_info, f, indent=2)

                return df_passes

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    return None


if __name__ == "__main__":
    df = download_statsbomb_data()
    if df is not None:
        print(f"\n✓ Successfully downloaded {len(df)} real passing events")
        print("\nTop passers:")
        print(df["passer"].value_counts().head(10))
    else:
        print("\n✗ Failed to download data")
