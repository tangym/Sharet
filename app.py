# -- encoding: utf-8 --
# author: tym
# date: 2015-11-26
import os
import io

from flask import Flask, current_app, render_template, request, redirect, url_for, send_file
from werkzeug import secure_filename
import qrcode
import qrcode.image.svg

import Sharet

app = Flask(__name__, static_folder=Sharet.config['share_dir'])
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'tex', 'md', 'markdown',
                              'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ps', 'psd', 'ai', 'eps', 'svg',
                              'mp3', 'wav', 'flac',
                              'flv', 'avi', 'mp4', 'rm', 'ogg',
                              'zip', '7z', 'rar', 'gz'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/qr/<route>')
def qr(route, method='basic'):
    if method == 'basic':
        # Simple factory, just a set of rects.
        factory = qrcode.image.svg.SvgImage
    elif method == 'fragment':
        # Fragment factory (also just a set of rects)
        factory = qrcode.image.svg.SvgFragmentImage
    else:
        # Combined path factory, fixes white space that may occur when zooming
        factory = qrcode.image.svg.SvgPathImage
    text = 'http://%s/%s' % (Sharet.config['domain'], route)
    img = qrcode.make(text, image_factory=factory)
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return send_file(buffer, mimetype='image/svg+xml')


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Sharet.config['upload_dir'], filename))
            route = Sharet.upload(filename)
            # return render_template('success.html', route=route, port=app.config['PORT'], domain=Sharet.config['domain'])
            return route
    return render_template('upload.html')


@app.route('/<route>', methods=['GET'])
def download(route):
    share = os.path.abspath(Sharet.config['share_dir'])
    fname = Sharet.download(route)
    if fname:
        return current_app.send_static_file(fname)
        # return send_from_directory(directory=share, filename=fname)    # not work
        # return send_file(os.path.join(share, fname), as_attachment=True)   # not work
    else:
        # TODO: 404
        return 'File not found'


# an redirect example
@app.route('/redirect/<route>')
def legacy_images(route):
    return redirect(flask.url_for('http://some.url?maybe'), code=301)

if __name__ == '__main__':
    app.run(port=9000)
