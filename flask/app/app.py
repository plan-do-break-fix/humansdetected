from flask import Flask


app = Flask(__name__)

@app.route("/")
def gallery():
    pass

@app.route("/")
def about():
    pass
