"""
app.py - starts the LOK Property Solutions API.

Run it with:   python app.py
It then listens on http://localhost:5000
"""
import os

from flask import Flask, jsonify, request

import config
import db
from routes.public import public_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    db.init_app(app)                  # connect database + create tables
    app.register_blueprint(public_bp)  # routes for visitors
    app.register_blueprint(admin_bp)   # routes for the admin

    # ---- CORS: lets the two websites (different addresses) call this API ----
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if "*" in config.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif origin in config.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return response

    @app.route("/api/<path:_>", methods=["OPTIONS"])
    def preflight(_):
        """Browsers send an OPTIONS 'preflight' request first; just say OK."""
        return "", 204

    # ---- simple health check (useful to see if the server is awake) ----
    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    # ---- friendly JSON errors instead of HTML pages ----
    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def server_error(_):
        return jsonify(error="Something went wrong on the server"), 500

    return app


app = create_app()

if __name__ == "__main__":
    # debug=True auto-restarts on code changes. Turn it off in production.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("DEBUG", "1") == "1")
