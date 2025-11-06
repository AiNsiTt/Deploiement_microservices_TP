from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/users/status', methods=['GET'])
def status():
    return jsonify({
        "service": "User Service",
        "status": "Running",
        "database": os.environ.get("DB_HOST", "localhost")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
