# Long-Text-Question-Answering

## How it works:

1) Store data as a chunk in Elastic Search.
2) Elasticsearch scour through large corpora and retrieve relevant document to question.
3) Apply QA model on retrieved document.

## Technologies used:
FastAPI, HuggingFace, Docker

## How to run:

1) docker-compose build
2) docker-compose up
