import pandas as pd


def transform_length(time):
    minutes = 0
    if 'h' in time:
        minutes += int(time.split("h")[0]) * 60
        time = time.split('h')[1]
    if "min" in time:
        minutes += int(time.split("min")[0])
    return minutes


tv_series_df = pd.read_csv("data/tv_series_rated.csv")
imdb_series_df = pd.read_sql_table("tv_series", "sqlite:///imdb.db")

# Get a list of all the possible genres.
genres = set(" ".join(imdb_series_df["genres"].tolist()).split(" "))
genres = list(filter(lambda x: len(x) > 0, genres))

# Create and fill columns in the dataframe.
for i, row in imdb_series_df.iterrows():
    # OneHotEncoding of genres.
    for genre in genres:
        imdb_series_df.loc[i, f"genre_{genre.lower()}"] = int(genre in row["genres"])

    # Change ep_length format.
    imdb_series_df.loc[i, "ep_length"] = transform_length(row["ep_length"])
imdb_series_df = imdb_series_df.drop(columns=["genres"])

imdb_series_df.to_csv("data/imdb_shows.csv")