# -*- coding:utf-8 -*-
"""
Use this module in the development environment.
"""

from dotenv import load_dotenv

load_dotenv()
from app.entry import create_app


if __name__ == '__main__':
    create_app().run(host='localhost', port=9999, debug=True)
