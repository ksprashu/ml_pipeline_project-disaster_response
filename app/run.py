import json
import re
import plotly
import pandas as pd

import nltk
nltk.download(['punkt', 'wordnet', 'stopwords'])

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from plotly.graph_objs import Pie

import joblib
from sqlalchemy import create_engine


app = Flask(__name__)
app.static_folder = 'static'

def tokenize(text):
    """Defines the tokenizer for the text messages

    The method first tokenizes the text into words using nltk.
    Then we will remove all the words that contains only special characters
    or punctuations. Next we will remove all the stop words based on wordnet
    Finally we will lemmatize the words to its root for both nouns and verbs
    
    Args:
        text: A tweet or message that has to be analyzed

    Returns:
        The tokens associated with the given text
    """
    
    tokens = word_tokenize(text)
    tokens = [tok for tok in tokens if re.search('[A-Za-z0-9]', tok) != None]
    tokens = [tok.lower().strip() for tok in tokens 
                    if tok not in stopwords.words('english')]
    wnl = WordNetLemmatizer()
    tokens = [wnl.lemmatize(wnl.lemmatize(tok), pos='v') for tok in tokens]            

    return tokens


# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('messages', engine)

# load model
model = joblib.load("../models/classifier.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)

    # get the counts of messages against each label and category
    cat_counts = df.filter(df.columns[4:7].tolist()).sum().sort_values(ascending=False)
    cat_names = list(cat_counts.index)

    label_counts = df.filter(df.columns[7:].tolist()).sum().sort_values(ascending=False)
    label_names = list(label_counts.index)
    # print(df.columns[4:].str.title())
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Pie(
                    labels=genre_names,
                    values=genre_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Genres'
            }
        },
        {
            'data': [
                Pie(
                    labels=cat_names,
                    values=cat_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Label Categories'
            }
        },
        {
            'data': [
                Bar(
                    x=label_names,
                    y=label_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Labels',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Labels"
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))
    # print(classification_results)

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results,
        ids=[], graphJSON=[]
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()