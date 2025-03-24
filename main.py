from flask import Flask
from waitress import serve

from album_service import get_album_pdf_path

app = Flask(__name__)


@app.route('/get_pdf_path/<jm_album_id>/<is_path>', methods=['GET'])
def get_pdf_path(jm_album_id,is_path):
    is_path = is_path.lower() in ['true', '1', 'yes']
    data,name = get_album_pdf_path(jm_album_id,is_path)
    if data is None:
        return {
            "success": False,
            "name": name,
            "data": ""
        }
    else:
        return {
            "success": True,
            "name": name,
            "data": data
        }


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8699)
