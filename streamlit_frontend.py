import streamlit as st
import requests
import pickle
import random
from PIL import Image
from io import BytesIO
import time

st.set_page_config(page_title="MovieBuddy", layout="wide")

st.markdown("""
    <style>
    
    .stApp {
        background-image: url('static\background.jpeg'); 
        background-size: cover;
        background-position: center;
        color: white;
    }

    
    .landing-page {
        font-size: 2.5em;
        color: #ffcc00;
        text-align: center;
        margin-top: 20%;
        font-family: 'Arial', sans-serif;
        background-image: url('static\background.jpeg'); 
        background-size: cover;
        background-position: center;
    }

   
    h1 {
        color: #ffcc00;
        text-align: center;
        font-family: 'Arial', sans-serif;
        font-size: 2.5em;
    }

   
    .sidebar-title {
        color: #ffcc00;
        font-size: 1.5em;
        text-align: center;
        font-family: 'Arial', sans-serif;
        margin-bottom: 0.5em;
    }

   
    .movie-poster:hover {
        transform: scale(1.05);
        transition: transform 0.3s;
    }
    </style>
""", unsafe_allow_html=True)


if "visited" not in st.session_state:
    st.session_state.visited = False
    st.write('<div class="landing-page">Welcome to the World of MovieBuddy</div>', unsafe_allow_html=True)
    time.sleep(3)  


st.session_state.visited = True

with open('movie_data.pkl', 'rb') as file:
    movies, _ = pickle.load(file)

st.title("🎬 MovieBuddy: Your Personalized Movie Recommender")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)


def fetch_recommendations(movie_title):
    url = 'http://127.0.0.1:5000/recommend' 
    response = requests.post(url, json={'title': movie_title})
    return response.json() if response.status_code == 200 else []


def fetch_poster(movie_id):
    api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8' 
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
   
    return "https://via.placeholder.com/150"  

if "search_history" not in st.session_state:
    st.session_state.search_history = []


if st.button('Get Recommendations'):
    st.session_state.search_history.append(selected_movie)
    recommendations = fetch_recommendations(selected_movie)
    
    if recommendations:
        st.write("### Top 10 Recommended Movies:")
        cols = st.columns(5)
        for i, movie in enumerate(recommendations):
            col = cols[i % 5]
            with col:
                poster_url = fetch_poster(movie['movie_id'])
                if poster_url:  
                    st.image(poster_url, width=150, use_column_width='auto', caption=movie['title'])
                else:
                    st.write(f"Poster not available for {movie['title']}")

    else:
        st.write("No recommendations found. Please try a different movie.")


st.sidebar.markdown('<div class="sidebar-title">Trending Movies</div>', unsafe_allow_html=True)
trending_movies = movies.sample(5)  
for _, row in trending_movies.iterrows():
    poster_url = fetch_poster(row['movie_id'])
    if poster_url: 
        st.sidebar.image(poster_url, width=120, caption=row['title'])
    else:
        st.sidebar.write(f"Poster not available for {row['title']}")


st.sidebar.markdown('<div class="sidebar-title">You Might Like</div>', unsafe_allow_html=True)
if st.session_state.search_history:
    recent_movie = st.session_state.search_history[-1]
    similar_movies = fetch_recommendations(recent_movie)

    
    recommended_movie_ids = {movie['movie_id'] for movie in recommendations}
    unique_similar_movies = [movie for movie in similar_movies if movie['movie_id'] not in recommended_movie_ids]

    for movie in unique_similar_movies[:5]: 
        poster_url = fetch_poster(movie['movie_id'])
        if poster_url:  
            st.sidebar.image(poster_url, width=120, caption=movie['title'])
        else:
            st.sidebar.write(f"Poster not available for {movie['title']}")
