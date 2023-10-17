from flask import Flask, render_template, request
import os
import pickle
import numpy as np
import urllib.parse  # Add this import

app = Flask(__name__)

# Assuming the files are located in the same directory as the Python script 'app.py'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load data from the files with absolute paths
popular_file_path = os.path.join(BASE_DIR, 'popular.pkl')
pt_file_path = os.path.join(BASE_DIR, 'pt.pkl')
books_file_path = os.path.join(BASE_DIR, 'books.pkl')
similarity_scores_file_path = os.path.join(BASE_DIR, 'similarity_scores.pkl')

try:
    with open(popular_file_path, 'rb') as f:
        popular_df = pickle.load(f)
    with open(pt_file_path, 'rb') as f:
        pt = pickle.load(f)
    with open(books_file_path, 'rb') as f:
        books = pickle.load(f)
    with open(similarity_scores_file_path, 'rb') as f:
        similarity_scores = pickle.load(f)
except FileNotFoundError:
    print("One or more data files not found. Please check the file paths.")

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    # Check if user_input exists in pt.index
    if user_input not in pt.index:
        error_message = f"'{user_input}' not found in the dataset."
        return render_template('recommend.html', error_message=error_message)

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        # Use urllib.parse.quote to handle spaces and special characters in URLs
        item.extend([urllib.parse.quote(temp_df.iloc[0]['Image-URL-M'], safe=":/")])

        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

