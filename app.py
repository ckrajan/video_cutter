from flask import Flask, render_template, request, make_response
import os

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def cutter():
    return render_template('cutter.html')


if __name__ == '__main__':
    app.run(port=8080, debug=True)