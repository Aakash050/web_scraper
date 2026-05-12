import requests
from bs4 import BeautifulSoup
from readability import Document
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
import urllib3
import json
from flask import Flask, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_session():
    session = requests.Session()
    retries = Retry(
        total = 3,
        backoff_factor = 1,
        status_forcelist = [429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries = retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
VERIFY_SSL = False #Configurable, local MacOS SSL issue
def fetch_page(url, session):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = session.get(url, 
                            headers = headers,
                            timeout = 5, 
                            verify = VERIFY_SSL)
    if response.status_code != 200:
        raise Exception(f"Error: {url}")
    return response.text
def extract_links(soup, base_url): 
    links = set()
    for a in soup.find_all("a", href = True):
        href = a["href"]
        if href.startswith("/wiki/") and ":" not in href:
            full_url = urljoin(base_url, href)
            links.add(full_url)
    return list(links)
def crawl(start_url, max_pages = 5):
    session = create_session()
    visited = set()
    to_visit = [start_url]
    results = []
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try: 
            html = fetch_page(url, session)
            data, new_links = parse_page(html, url)
            results.append(data)
            to_visit.extend(new_links[:5])
            visited.add(url)
        except Exception as e:
            print(e)
    return results
def parse_page(html, url):
    doc = Document(html)
    clean_html = doc.summary()
    soup = BeautifulSoup(clean_html, "lxml")
    for table in soup.find_all("table"):
        table.decompose()
    title = soup.find("h1").get_text(strip = True) if soup.find("h1") else ""
    sections = []
    current_section = {"heading": "Introduction", "paragraphs": []}
    for tag in soup.find_all(["h2", "p"]):
        if tag.name == "h2": 
            if current_section["paragraphs"]: 
                sections.append(current_section)
            current_section = {
                "heading": tag.get_text(strip = True),
                "paragraphs": []
            }
        elif tag.name == "p": 
            text = tag.get_text(" ", strip = True)
            if text: 
                current_section["paragraphs"].append(text)
    if current_section["paragraphs"]: 
        sections.append(current_section)
    links = extract_links(soup, url)
    return {
        "url": url,
        "title": title,
        "sections": sections
    }, links
def save_results(results):
    with open("article.json", "w", encoding = "utf-8") as f: 
        json.dump(results, f, indent = 2, ensure_ascii = False)
        
app = Flask(__name__)
@app.route("/scrape", methods = ["GET"])
def scrape(): 
    url = request.args.get("url")
    if not url: 
        return jsonify({"Error": "Missing url parameter"}), 400
    pages = int(request.args.get("pages", 3))
    
    results = crawl(url, max_pages = pages)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug = True)
