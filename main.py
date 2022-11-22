from flask import Flask, request
from flask_cors import CORS
import os
import pandas as pd
import json
# Models
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pysentiment2 as ps

vader = SentimentIntensityAnalyzer()
hiv4 = ps.HIV4()
lm = ps.LM()
# ...

app = Flask(__name__)
CORS(app)

CSV_PATH = os.path.abspath('hotels.csv')
hotels = pd.read_csv(CSV_PATH)

# Routes
@app.route("/", methods = ['GET'])
def home():
    return """
    <h1>Welcome to the Hotel Summary API</h1>
    <p>
    Endpoints:
    <ul>
        <li>[GET] /hotels?year=<b>{year:int}</b>&name=<b>{name:str}</b></li>
        <li>[GET] /search/<b>{name:str}</b></li>
        <li>[POST] /rate (body:{"SUMMARY":<b>{summary:str}</b>}</li>
    </ul>
    </p>
    """

@app.route("/hotels", methods = ['GET'])
def get_hotels():
    year = request.args.get('year')
    name = request.args.get('name')

    filter_hotels = hotels

    if name:
        filter_hotels = filter_hotels[filter_hotels["HOTEL_NAME"]==name]

    if year:
        try:
            year = int(year)
            filter_hotels = filter_hotels[filter_hotels["REVIEW_DATE"]==year]
        except:
            return "<h1>Error</h1> <p>The year must be an integer number </p>"

    return json.loads(filter_hotels.to_json(orient='records'))

@app.route("/search/<value>", methods = ['GET'])
def get_search(value: str):
    year = request.args.get('year')
    hotel = contains_name(hotels, value)
    if year:
        try:
            year = int(year)
            year_hotels = hotel[hotels["REVIEW_DATE"]==year]
            return json.loads(year_hotels.to_json(orient='records'))
        except:
            return "<h1>Error</h1> <p>The year must be an integer number </p>"
    else:
        return json.loads(hotel.to_json(orient='records'))

@app.route("/rate", methods = ['POST'])
def post_rate():
    data = request.get_json()
    summary = data["REVIEW"]

    vader_rating = vaderRating(summary)
    hiv4_rating = hiv4Rating(summary)
    lm_rating = lmRating(summary)
    overall_rating = round((vader_rating + hiv4_rating + lm_rating)/3)

    return {
        "VADER_RATING":vader_rating,
        "HIV4_RATING":hiv4_rating,
        "LM_RATING":lm_rating,
        "OVERALL_RATING":overall_rating
    }
# ...

def contains_name(df, value: str):
    return df[df["HOTEL_NAME"].str.contains(value, case=False)]

# Rating
def vaderRating(text):
    compound = vader.polarity_scores(text)["compound"]
    return normalize((-1, 1), (1, 5), compound)

def hiv4Rating(text):
    polarity = hiv4.get_score(hiv4.tokenize(text))['Polarity']
    return normalize((-1, 1), (1, 5), polarity)

def lmRating(text):
    polarity = lm.get_score(lm.tokenize(text))['Polarity']
    return normalize((-1, 1), (1, 5), polarity)

def normalize(from_range, to_range, value):
    on_decimal = to_range[0] + ( (value - from_range[0]) * (to_range[1] - to_range[0]) / (from_range[1] - from_range[0]) )
    return round(on_decimal)
# ...

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)