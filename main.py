from flask import Flask, request, send_from_directory
import os
import pandas as pd

app = Flask(__name__)

CSV_PATH = os.path.abspath('hotels.csv')
hotels = pd.read_csv(CSV_PATH)

# Routes
@app.route("/")
def home():
    return """
    <h1>Welcome to the Hotel Summary API</h1>
    <p>
    Enpoints:
    <ul>
        <li>[GET] /hotels</li>
        <li>[GET] /hotels/{name}</li>
    </ul>
    Queries:
    <ul>
        <li>year {integer}: The year of the summary. </li>
    </ul>
    </p>
    """

@app.route("/hotels")
def get_hotels():
    year = request.args.get('year')
    if year:
        try:
            year = int(year)
            year_hotels = hotels[hotels["REVIEW_DATE"]==year]
            return year_hotels.to_json(orient='records')
        except:
            return "<h1>Error</h1> <p>The year must be an integer number </p>"
    else:
        return hotels.to_json(orient='records')

@app.route("/hotels/<name>")
def get_hotel(name: str):
    year = request.args.get('year')
    if year:
        try:
            year = int(year)
            hotel = hotels[hotels["HOTEL_NAME"] == name]
            year_hotels = hotel[hotels["REVIEW_DATE"]==year]
            return year_hotels.to_json(orient='records')
        except:
            return "<h1>Error</h1> <p>The year must be an integer number </p>"
    else:
        hotel = hotels[hotels["HOTEL_NAME"] == name]
        return hotel.to_json(orient='records')
#...

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)