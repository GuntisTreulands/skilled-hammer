import logging
import os
import subprocess

from flask import Flask, request, jsonify

from skilled_hammer import repositories, exceptions, log
from skilled_hammer.utils import valid_github_http_headers, pull, random_secret

log.setup()
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.update({
    'HAMMER_SECRET': os.environ.get('HAMMER_SECRET', random_secret()),
    'HAMMER_VERSION': "1.0.0",
    'HAMMER_REPOSITORIES': repositories.load(),
})


@app.route('/', methods=['POST'])
def deploy():
    try:
        if not valid_github_http_headers(request):
            raise exceptions.SuspiciousOperation("Invalid HTTP headers")

        payload = request.get_json()

        if not payload \
                or 'repository' not in payload \
                or 'url' not in payload['repository']:
            raise exceptions.SuspiciousOperation("Invalid payload")

        url = payload['repository']['url']

        if url not in app.config['HAMMER_REPOSITORIES']:
            raise exceptions.UnknownRepository("Unknown repository")

        pull_succeeded = False
        for _, repo in app.config['HAMMER_REPOSITORIES'].items():
            if repo['origin'] == url:
                pull_succeeded = pull(repo['directory'])
                if pull_succeeded and 'command' in repo:
                    logger.info("Running command: {0}".format(repo['command']))
                    subprocess.call(repo['command'], shell=True, cwd=repo['directory'])
                break

        return jsonify({'status': pull_succeeded})
    except exceptions.HammerException as e:
        logger.error(e)


if __name__ == "__main__":
    app.run(debug=True)
