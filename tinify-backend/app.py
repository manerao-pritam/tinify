from chalice import Chalice, Response

app = Chalice(app_name="tinify-backend")


@app.route("/")
def index():
    return {"hello": "world"}


@app.route('/redirect', content_types=['application/json'])
def redirect():
    url = app.current_request.raw_body.strip()
    return Response(
        status_code=301,
        body='',
        headers={'Location': 'https://cloudunfold.com/'}
    )
