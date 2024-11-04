from flask import Flask, jsonify, request
import pandas as pd
import pickle
import requests

app = Flask(__name__)


with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

def get_recommendations(title):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices].to_dict(orient='records')

def fetch_poster(movie_id):
    api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'  
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    full_path = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    return full_path

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    title = data.get('title')
    recommendations = get_recommendations(title)
    
    for movie in recommendations:
        movie['poster_url'] = fetch_poster(movie['movie_id'])
    
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
