import os, re, json, threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "./out"
MAX_WORKERS = 8
