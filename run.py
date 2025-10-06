from flask import jsonify, request, send_from_directory
from app import create_app

app = create_app()
# Endpoint para el Service Worker
@app.route("/sw.js")
def sw():
    return send_from_directory("static", "sw.js")

if __name__ == '__main__':
    app.run(debug=True)