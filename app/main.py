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
from qa.elastic import Elastic, splitTextonWords
import schemas as s
import time
import asyncio


cd = str(Path(__file__).absolute().parents[0]) # root/.../../app
# print(cd)
time.sleep(50) #let wait for elastic to start its server
ports = ['localhost:9200']
index = "myindex1"
text = """
The city existed for over 1,500 years before Muhammad's migration from Mecca,[5] otherwise known as the Hijrah. Medina was the capital of a rapidly increasing Muslim caliphate under Muhammad's leadership, serving as its base of operations and as the cradle of Islam, where Muhammad's Ummah (Community), composed of the citizens of Medina, known as the Ansar and those who immigrated with Muhammad, known as the Muhajirun, collectively known as the Sahaba, gained huge influence. Medina is home to three prominent mosques, namely al-Masjid an-Nabawi, Masjid Quba'a, and Masjid al-Qiblatayn, with the masjid at Quba'a being the oldest in Islam. A larger portion of the Qur'an was revealed in Medina in contrast to the earlier Meccan surahs.[6][7]
Much like most of the Hejaz, Medina has seen numerous exchanges of power within its comparatively short existence. The region has been controlled by Arabian Jewish tribes (up to the 5th century CE), the 'Aws and Khazraj (up to Muhammad's arrival), Muhammad and the Rashidun (622–660 CE), Umayyads (660–749 CE), Abbasids (749–1254 CE), the Mamluks of Egypt (1254–1517 CE), the Ottomans (1517–1805 CE), the First Saudi State (1805–1811 CE), Muhammad Ali Pasha (1811–1840 CE), the Ottomans for a second time (1840–1918), the Hashemite Sharifate of Mecca (1918–1925 CE) and finally is in the hands of the modern-day Kingdom of Saudi Arabia (1925–present CE).[4]
"""

# list_of_strings = es.splitTextonWords(text, 20)
# print(list_of_strings)

els = Elastic()
es=els.connect_elasticsearch(ports=[{"host": "es01", "port": 9200}])
print(els.es)
els.create_index(index)


# es = Elasticsearch(hosts=[{"host": "es01", "port": 9200}],
#                 connection_class=RequestsHttpConnection, 
#                 max_retries=300,
#                 retry_on_timeout=True, 
#                 request_timeout=100
#                        )
# print(es)
# print(es.ping())
# es.indices.create(
#                 index=index,
#                 ignore=400,
#             )



app = FastAPI()
app.mount("/static", StaticFiles(directory=cd+"/static"), name="static")
templates = Jinja2Templates(directory=cd+"/templates")

async def bulk_list_data(list_of_strings, index):
        # use a `yield` generator so that the data
        # isn't loaded into memory
    for i, doc in enumerate(list_of_strings):

        if '{"index"' not in text:
            yield {
                "_index": index,
                # "_type": doc_type,
                "_id": i,
                "_source": {"text": doc}
            } 

@app.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    result = "Type a number"
    return templates.TemplateResponse("home.html", {"request": request, "result": result})

@app.post("/submittext")
async def read_item(res: s.Response):
    result=res.text
    textarr = els.splitTextonWords(result, numberOfWords=10)
    els.delete_index(index)
    els.create_index(index)
    response = await els.bulk_post(textarr, index)
    print(response)
    return textarr

@app.post("/predict", response_model = s.PredictResponse)
def predict(input: s.PredictRequest, model: Model = Depends(get_model)):
    a = np.array(input.data)
    que, text = a[0], a[1]
    ans = model.predict(que, text)
    return s.PredictResponse(data=ans)

@app.on_event("shutdown")
async def app_shutdown():
    await es.close()