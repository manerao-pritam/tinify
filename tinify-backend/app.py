import logging
from hashlib import sha512

import boto3
from boto3.dynamodb.conditions import Key
from chalice import BadRequestError, Chalice, Response

# logger details
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the service resource.
dynamodb = boto3.resource('dynamodb')

# table name, can also be refered from environment variables
table = dynamodb.Table('TinifyAppResources-TinifyTable-8D0O6AX7GX5F')

# App
app = Chalice(app_name="tinify-backend")
app.debug = False


# util to get base url
def get_base_url(current_request):
    headers = current_request.headers
    base_url = '%s://%s' % (headers.get('x-forwarded-proto',
                            'http'), headers['host'])
    if 'stage' in current_request.context:
        base_url = '%s/%s' % (base_url, current_request.context.get('stage'))
    return base_url


# shorten then url
@app.route("/shorten", methods=['POST'])
def shorten():
    request_body = app.current_request.json_body
    logger.info(f'Request body: {request_body}')

    try:
        # get the url from requet body and encode it
        url = request_body['url']
        logger.info(f'Received url: {url}')

        # generate hash, and get first 6 chars, these will be enough to handle enough records
        urlHash = sha512(url.encode('utf-8')).hexdigest()[:6]
        logger.info(f'Hashed url: {urlHash}')

        # put the record to db
        table.put_item(
            Item={
                'urlHash': urlHash,
                'url': url
            }
        )

        return_url = f'{get_base_url(app.current_request)}/{urlHash}'
        logger.info(f'Return url: {return_url}')

        return Response(
            body=return_url,
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )

    except:
        raise BadRequestError("Oops! The url is invalid!")


# Route to get the tiny url and then to redirect to the actual url
@app.route("/{urlHash}")
def redirect(urlHash):
    response = table.get_item(
        Key={
            'urlHash': urlHash
        }
    )
    logger.info(f'DB query result: {response}')

    try:
        # get url from urlHash
        url = response['Item']['url']
        logger.info(f'Received url: {url}')

        return Response(
            status_code=301,
            body='',
            headers={'Location': url}
        )

    except IndexError:
        raise BadRequestError("Oops! The url is invalid!")
