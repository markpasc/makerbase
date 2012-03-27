from flask import Flask


app = Flask(__name__)

app.debug_log_format = '%(asctime)-8s %(levelname)-8s %(name)-15s %(message)s'


import makerbase.tags
import makerbase.views
