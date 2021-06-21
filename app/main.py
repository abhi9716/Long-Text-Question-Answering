import numpy as np
from typing import List, Dict
from fastapi import FastAPI,Request, Form
from fastapi import Depends
from pydantic import BaseModel,validator
from qa.qamodel import get_model, Model
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from elasticsearch import AsyncElasticsearch, Elasticsearch, RequestsHttpConnection, helpers
from qa.elastic import Elastic
import schemas as s
import time
import asyncio

cd = str(Path(__file__).absolute().parents[0]) # root/.../../app
# print(cd)
time.sleep(50) #let wait for elastic to start its server
index = "myindex1"

els = Elastic()
es= els.connect_elasticsearch(ports=[{"host": "es01", "port": 9200}])
print(els.es)
# els.create_index(index)

app = FastAPI()
app.mount("/static", StaticFiles(directory=cd+"/static"), name="static")
templates = Jinja2Templates(directory=cd+"/templates")

@app.on_event("shutdown")
async def app_shutdown():
    await es.close()

@app.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    result = "Answer"
    return templates.TemplateResponse("home.html", {"request": request, "result": result})

@app.post("/submittext")
async def read_item(res: s.Response):
    result=res.text
    textarr = els.splitTextonWords(result, numberOfWords=10)
    await els.delete_index(index)
    await els.create_index(index)
    response = await els.bulk_post(textarr, index)
    print("\nRESPONSEee:",response)
    return textarr

@app.post("/submitque")
async def read_item(res: s.Response, model: Model = Depends(get_model)):
    ques = res.text
    print(ques)
    doc = await els.find_relevant_doc(index, ques)
    print(doc["hits"]["hits"])
    if len(doc["hits"]["hits"])!=0:
        print(doc["hits"]["hits"])
        rel_doc = doc["hits"]["hits"][0]["_source"]["text"]
        ans = model.predict(ques, rel_doc)
        print(ans)
        return ans
    else:
        return "No answer found"
    

# @app.post("/predict", response_model = s.PredictResponse)
# def predict(input: s.PredictRequest, model: Model = Depends(get_model)):
#     a = np.array(input.data)
#     que, text = a[0], a[1]
#     ans = model.predict(que, text)
#     return s.PredictResponse(data=ans)

