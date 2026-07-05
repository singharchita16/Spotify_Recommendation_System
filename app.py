from flask import Flask, render_template, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# -------------------------------
# Load Dataset
# -------------------------------
df = pd.read_csv("clustered_df.csv")

# Features used for similarity
features = [
    "valence",
    "danceability",
    "energy",
    "tempo",
    "acousticness",
    "liveness",
    "speechiness",
    "instrumentalness"
]


# -------------------------------
# Recommendation Function
# -------------------------------
def recommend_songs(song_name, num_recommendations=5):

    # Song not found
    if song_name not in df["name"].values:
        return None

    # Find selected song cluster
    cluster = df.loc[
        df["name"] == song_name,
        "Cluster"
    ].values[0]

    # Songs from same cluster
    cluster_df = df[df["Cluster"] == cluster].reset_index(drop=True)

    # Cosine similarity
    similarity = cosine_similarity(cluster_df[features])

    # Selected song index
    song_index = cluster_df[
        cluster_df["name"] == song_name
    ].index[0]

    similarity_scores = list(
        enumerate(similarity[song_index])
    )

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for score in similarity_scores[1:num_recommendations + 1]:

        row = cluster_df.iloc[score[0]]

        recommendations.append({

            "name": row["name"],
            "artist": row["artists"],
            "cluster": row["Cluster"]

        })

    return recommendations


# -------------------------------
# Home Page
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    recommendations = None
    selected_song = ""

    if request.method == "POST":

        selected_song = request.form["song"]

        recommendations = recommend_songs(selected_song)

    songs = sorted(df["name"].unique())

    return render_template(
        "index.html",
        songs=songs,
        recommendations=recommendations,
        selected_song=selected_song
    )


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)