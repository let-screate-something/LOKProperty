"""
api/index.py - Vercel serverless entry point for the Flask API.

Vercel runs Python functions as serverless endpoints. This file imports
the Flask app from server/ and exposes it as a WSGI handler for Vercel.
"""
import os
import sys

# Add server folder to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from app import create_app

app = create_app()

# Vercel expects the WSGI app as 'app'
handler = app