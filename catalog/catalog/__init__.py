# from flask import Flask
# app = Flask(__name__)
# @app.route("/")
# def hello():
#     return "Hello, I love Digital Ocean!"
# if __name__ == "__main__":
#     app.run()

from flask import Flask
from flask.ext.seasurf import SeaSurf

app = Flask(__name__)
csrf = SeaSurf()
csrf.init_app(app)


import catalog.views

