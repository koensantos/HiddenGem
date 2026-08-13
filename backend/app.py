import flask
from similarity_score import calculate_similarity_score
from flask import Flask, render_template
app = Flask(__name__)

def get_recommendations(song_name, min_monthly_listeners, max_monthly_listeners, genre):
    recommendations = calculate_similarity_score(
        song_1=song_name,
        min_monthly_listeners=min_monthly_listeners,
        max_monthly_listeners=max_monthly_listeners,
        genre=genre
    )
    return recommendations

@app.route('/')
def run_recommendation():
    song_name = "Not Like Us"
    min_monthly_listeners = 1000000
    max_monthly_listeners = 10000000
    genre = "pop"

    recommendations = get_recommendations(song_name, min_monthly_listeners, max_monthly_listeners, genre)
    return recommendations
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)