# Web Scraper

## Overview
A lightweight Flask-based web scraping API that:
- crawls webpages
- extracts structured article content
- removes boilerplate HTML
- organizes content into sections
- returns clean JSON for downstream NLP/RAG systems

## Features
- Multi-page crawling
- Retry logic
- Structured extraction
- Readability-based cleaning
- JSON API
- Link discovery
- Section parsing

## Tech Stack
- Python
- Flask
- BeautifulSoup
- Requests
- Readability-lxml

## Example Request
GET /scrape?url=...&pages=3

## Example Output
{ ... }

## Future Improvements
- Async crawling
- JS rendering with Playwright
- Embedding generation
- Vector DB integration
- Robots.txt compliance
