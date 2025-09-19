import streamlit as st
import numpy as np
import pickle
import requests
import streamlit.components.v1 as components
import os

# ------------------- Load similarity (split into 8 parts or fallback) -------------------
def load_similarity():
    similarity = []  # initialize the variable before using it

    try:
        # assuming you have multiple parts like similarity_part_1.pkl, similarity_part_2.pkl
        parts = ["similarity_part_1.pkl", "similarity_part_2.pkl"]  # add all your parts here
        for part_file in parts:
            with open(part_file, "rb") as f:
                similarity_part = pickle.load(f)
                similarity.extend(similarity_part)  # now this works
    except FileNotFoundError:
        print("Some similarity files are missing!")

    return similarity

similarity = load_similarity()

# ------------------- Safe fetch poster -------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent server blocking
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=No+Image"

# ------------------- Load movies -------------------
movies = pickle.load(open("movies_list.pkl", "rb"))
movies_list = movies["title"].values

st.header("🎬 Movie Recommender System")

# ------------------- Carousel -------------------
imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")
top_movie_ids = [1632, 299536, 17455, 2830, 429422, 9722, 13972, 240, 155, 598, 914, 255709, 572154]
imageUrls = [fetch_poster(mid) for mid in top_movie_ids]
imageCarouselComponent(imageUrls=imageUrls, height=200)

# ------------------- Dropdown -------------------
selectvalue = st.selectbox("Select movie from dropdown", movies_list)

# ------------------- Recommend function -------------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommend_movie = []
    recommend_poster = []
    for i in distance[1:6]:
        movie_id = movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movie_id))
    return recommend_movie, recommend_poster

# ------------------- Show recommendations -------------------
if st.button("Show Recommend"):
    movie_name, movie_poster = recommend(selectvalue)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        col.text(movie_name[idx])
        col.image(movie_poster[idx])
