from makerbase import app


app.config.from_envvar('MAKERBASE_SETTINGS')

app.run(debug=True)
