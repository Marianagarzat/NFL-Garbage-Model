# Let's do some data exploration. 

import nflreadpy as nfl 
import pandas as pd #since I'll work with data

print("loading")

games = nfl.load_pbp([2023, 2024, 2025]) # nfl.load_pbp() loads information about every action that happened during a game (passes, touchdowns, goals, etc)
# here I'm downloading data from 2023, 2024, 2025 seasons.

df = games.to_pandas() # I need to convert to a Pandas dataframe.

# Get the score before each play

df = df.sort_values(["game_id", "play_id"]).copy() # organizing plays by game.

df["home_score_before"] = (
    df.groupby("game_id")["total_home_score"] 
    .shift(1)
    .fillna(0)
)

# Get the away team's score before each play

df["away_score_before"] = (
    df.groupby("game_id")["total_away_score"]
    .shift(1)
    .fillna(0)
)


#calculate the score difference before the play

df["score_difference_before"] = abs(
    df["home_score_before"] - df["away_score_before"]
)

 


print("Total plays:", len(df)) # let's see how many rows are in the DataFrame

print("Total games:", df["game_id"].nunique()) #    df["game_id"] selects a column. 
                                             #    .nunique() counts the NUMBER of unique values in that column!
print(df.head()) # .head() will display the first 5 rows.


game = df[df["game_id"] == "2023_01_ARI_WAS"]  # getting ONLY the rows belonging to the Cardinals vs. Commanders game

columns = [
    "qtr", # quarters
    "game_seconds_remaining", 
    "posteam", #team with ball possession 
    "play_type", 
    "yards_gained",
    "total_home_score",
    "total_away_score",
    "desc" # description of events
    
]

# Print 4th quarter only

fourth_quarter = game[game["qtr"] == 4] # creating a variable containing the plays of the fourth quarter

print("Fourth Quarter Plays")
print(fourth_quarter[columns].head(15).to_string(index=False)) 


# analysis on the 4th quarter

fourth_quarter_plays = fourth_quarter[ 
    (fourth_quarter["game_seconds_remaining"] <= 900) &
    (fourth_quarter["game_seconds_remaining"] >= 0)
].copy()

print("Entire Fourth Quarter")
print(fourth_quarter_plays[columns].to_string(index=False))


# Now let's calculate the score difference

fourth_quarter_plays["score_difference"] = abs(
    fourth_quarter_plays["total_home_score"] - fourth_quarter_plays["total_away_score"]
) 

print("Score differences")
print(fourth_quarter_plays[[
    "game_seconds_remaining",
    "total_home_score",
    "total_away_score",
    "score_difference"
]].to_string(index=False))

# ---------------------#
# Analysis of all NFL games
# 4th quarter
all_fourth_quarter = df[
    (df["qtr"] == 4) &
    (df["game_seconds_remaining"] <900) &
    (df["game_seconds_remaining"] >= 0)
].copy()

#score difference

all_garbage_time = all_fourth_quarter[
    all_fourth_quarter["score_difference_before"] >=14 # Team leads by at least 14 points
].copy() 


all_garbage_time["home_is_losing"] = (
    all_garbage_time["home_score_before"] < all_garbage_time["away_score_before"]
)


# Identify the losing team

# Is the home team losing?

all_garbage_time["losing_team_has_ball"] = (
    all_garbage_time["losing_team"] ==
    all_garbage_time["posteam"]
)
print("Is the home team losing?")

print(all_garbage_time[[
    "home_team",
    "away_team", 
    "total_home_score",
    "total_away_score",
    "home_is_losing"
]].head(15).to_string(index=False))


all_garbage_time["losing_team"] = (
    all_garbage_time["home_team"].where(
        all_garbage_time["home_is_losing"],
        all_garbage_time["away_team"]
    )
)

print("Losing teams")

print(all_garbage_time)[[
    "home_team",
    "away_team",
    "total_home_score",
    "total_away_score",
    "losing_team"
]].head(15).to_string(index=False)


# now we must check if the losing team has the possession of the ball

all_garbage_time["losing_team_has_ball"] = (
    all_garbage_time["losing_team"] == all_garbage_time["posteam"]
)

print("Does the losing team have possession?")

print(all_garbage_time[[
    "losing_team",
    "posteam",
    "losing_team_has_ball"
]].head(15).to_string(index=False))

# Did the losing team score again?

