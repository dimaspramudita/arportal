
from flask import Flask, send_from_directory, request, Response
import os
import gzip
from io import BytesIO

app = Flask(__name__)

@app.after_request
def after_request(response):
    # Cek apakah respons dalam mode direct_passthrough
    if response.direct_passthrough:
        return response

    # Jika konten jenis teks atau JSON, aktifkan kompresi gzip
    if 'gzip' not in request.headers.get('Accept-Encoding', ''):
        return response

    if response.status_code < 200 or response.status_code >= 300 or \
        'Content-Encoding' in response.headers or \
        not response.headers.get('Content-Type', '').startswith(('text/', 'application/json', 'text/html')):
        return response

    gzip_buffer = BytesIO()
    gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
    gzip_file.write(response.data)
    gzip_file.close()

    response.data = gzip_buffer.getvalue()
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(response.data)

    return response

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    directory = os.getcwd()
    return send_from_directory(directory, filename)

if __name__ == "__main__":
    app.run(debug=True)

