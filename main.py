import subprocess

import git
from flask import Flask, request

from skilled_hammer import exceptions
from skilled_hammer.utils import valid_github_http_headers

app = Flask(__name__)
app.config.from_object('skilled_hammer.settings')
app.config.from_envvar('HAMMER_SETTINGS', silent=True)
app.config['HAMMER_SECRET'] or (print("Did you forget to define HAMMER_SECRET environment variable?"), exit(1))


@app.route('/', methods=['POST'])
def deploy():
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

    for repo in app.config['HAMMER_REPOSITORIES']:
        if repo['origin'] == url:
            pull(repo['directory'], repo['command'])
            break

    return ""


def pull(directory, command):
    try:
        repo = git.Repo(directory)
        info = repo.remotes.origin.pull()[0]

        if info.flags & info.ERROR:
            print("Git pull failed: {0}".format(info.note))
        elif info.flags & info.REJECTED:
            print("Could not merge after git pull: {0}".format(info.note))
        elif info.flags & info.HEAD_UPTODATE:
            print("Head is already up to date")
        else:
            subprocess.call(command, shell=True, cwd=directory)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run(debug=True)
