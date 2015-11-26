# -- encoding: utf-8 --
# author: tym
# date: 2015-11-26
import os

from flask import Flask, current_app

import Sharet


app = Flask(__name__, static_folder=Sharet.config['share_dir'])

@app.route('/')
def upload():
    # TODO: implement upload page
    return 'Hello World!'

@app.route('/<route>', methods=['GET'])
def download(route):
    # share = os.path.abspath(Sharet.config['share_dir'])
    fname = Sharet.download(route)
    if fname:
        return current_app.send_static_file(fname)
        # return send_from_directory(directory=share, filename=fname)    # not work
    else:
        # TODO: 404
        return 'File not found'


# an redirect example
@app.route('/redirect/<route>')
def legacy_images(route):
    return flask.redirect(flask.url_for('http://some.url?maybe'), code=301)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
