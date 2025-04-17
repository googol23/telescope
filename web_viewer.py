from flask import Flask, render_template
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("plots.html")

if __name__ == "__main__":
    print("Running from:", os.getcwd())
    app.run(debug=True)