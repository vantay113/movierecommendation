import os
import sqlite3
import webbrowser

import numpy as np
import pandas as pd

from web import matrix_factorization_utilities

db = "../../db.sqlite3"


def convert_to_movie_csv():
    conn = sqlite3.connect(db, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM web_movie", conn)
    headers = ['id', 'title', 'genre', 'movie_logo']
    db_df.to_csv('movies.csv', sep=',', header=headers, index=None)


def convert_to_rating_csv():
    conn = sqlite3.connect(db, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM web_myrating", conn)
    db_df.drop(['id'], axis=1, inplace=True)
    headers = ['rating', 'movie_id', 'user_id']
    db_df.to_csv('rating.csv', sep=',', header=headers, index=None)


def create_preview_matrix():
    df = pd.read_csv('rating.csv')
    ratings_df = pd.pivot_table(df, index='user_id', columns='movie_id', aggfunc=np.max)
    # print(ratings_df)
    # Create a web page view of the data for easy viewing
    html = ratings_df.to_html(na_rep="")

    # Save the html to a temporary file
    with open("review_matrix.html", "w") as f:
        f.write(html)

    # Open the web page in web browser
    full_filename = os.path.abspath("review_matrix.html")
    webbrowser.open("file://{}".format(full_filename))


def create_view_data():
    data_table = pd.read_csv("rating.csv")
    # Create a web page view of the data for easy viewing
    html = data_table[0:100].to_html()

    # Save the html to a temporary file
    with open("data.html", "w") as f:
        f.write(html)


def create_view_rating():
    data_table = pd.read_csv("movies.csv", index_col="id")
    # Create a web page view of the data for easy viewing
    html = data_table.to_html()
    # Save the html to a temporary file
    with open("movie_list.html", "w") as f:
        f.write(html)

    # Open the web page in our web browser
    full_filename = os.path.abspath("movie_list.html")
    webbrowser.open("file://{}".format(full_filename))


def factor_review_maxtrix():
    # Load user ratings
    raw_dataset_df = pd.read_csv('rating.csv')
    # Convert the running list of user ratings into a matrix
    ratings_df = pd.pivot_table(raw_dataset_df, index='user_id', columns='movie_id', aggfunc=np.max)

    # Apply matrix factorization to find the latent features
    U, M = matrix_factorization_utilities.low_rank_matrix_factorization(ratings_df.to_numpy(), num_features=15,regularization_amount=0.1)

    # Find all predicted ratings by multiplying the U by M
    predicted_ratings = np.matmul(U, M)

    # Save all the ratings to a csv file
    predicted_ratings_df = pd.DataFrame(index=ratings_df.index, columns=ratings_df.columns, data=predicted_ratings)

    predicted_ratings_df.to_csv("predicted_ratings.csv")

    html = predicted_ratings_df.to_html()
    # Save the html to a temporary file
    with open("predicted_ratings.html", "w") as f:
        f.write(html)
    # Open the web page in our web browser
    full_filename = os.path.abspath("predicted_ratings.html")
    webbrowser.open("file://{}".format(full_filename))


if __name__ == '__main__':
    convert_to_movie_csv()
    convert_to_rating_csv()
    create_preview_matrix()
    create_view_data()
    create_view_rating()
    factor_review_maxtrix()
