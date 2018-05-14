#!/usr/bin/env python3

"gunicorn entry point"

from app import APP as application

if __name__ == "__main__":
    application.run()
