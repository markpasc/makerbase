from flask import Flask


app = Flask(__name__)


import makerbase.tags
import makerbase.views
