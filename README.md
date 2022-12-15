# Long-Text-Question-Answering

How it works:
Store data as a chunk in Elastic Search.
Elasticsearch scour through large corpora and retrieve relevant document to question.
Apply QA model on retrieved document.
Technologies used:
FastAPI, HuggingFace, Elastic Search, Docker

How to run:
docker-compose build
docker-compose up
