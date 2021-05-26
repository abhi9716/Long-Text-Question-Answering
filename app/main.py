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
from elasticsearch import AsyncElasticsearch, Elasticsearch, RequestsHttpConnection
from qa.elastic import Elastic
import time
import asyncio



# time.sleep(30)

ports = ['localhost:9200']
index = "myindex"
text = """
The city existed for over 1,500 years before Muhammad's migration from Mecca,[5] otherwise known as the Hijrah. Medina was the capital of a rapidly increasing Muslim caliphate under Muhammad's leadership, serving as its base of operations and as the cradle of Islam, where Muhammad's Ummah (Community), composed of the citizens of Medina, known as the Ansar and those who immigrated with Muhammad, known as the Muhajirun, collectively known as the Sahaba, gained huge influence. Medina is home to three prominent mosques, namely al-Masjid an-Nabawi, Masjid Quba'a, and Masjid al-Qiblatayn, with the masjid at Quba'a being the oldest in Islam. A larger portion of the Qur'an was revealed in Medina in contrast to the earlier Meccan surahs.[6][7]

Much like most of the Hejaz, Medina has seen numerous exchanges of power within its comparatively short existence. The region has been controlled by Arabian Jewish tribes (up to the 5th century CE), the 'Aws and Khazraj (up to Muhammad's arrival), Muhammad and the Rashidun (622–660 CE), Umayyads (660–749 CE), Abbasids (749–1254 CE), the Mamluks of Egypt (1254–1517 CE), the Ottomans (1517–1805 CE), the First Saudi State (1805–1811 CE), Muhammad Ali Pasha (1811–1840 CE), the Ottomans for a second time (1840–1918), the Hashemite Sharifate of Mecca (1918–1925 CE) and finally is in the hands of the modern-day Kingdom of Saudi Arabia (1925–present CE).[4]
"""

# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
# es.indices.create(
#                 index=index,
#                 ignore=400,
#             )
# list_of_strings = es.splitTextonWords(text, 20)
# print(list_of_strings)

# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

cd = str(Path(__file__).absolute().parents[0]) # root/.../../app
print(cd)
class PredictRequest(BaseModel):
    data: List[str]

    @validator('data')
    def length(cls, v):
        if len(v) == 2:
            return v
        else:
            raise ValueError('Length of incoming list must be 2.')

class PredictResponse(BaseModel):
    data: str


app = FastAPI()
# es = AsyncElasticsearch([{'host': 'localhost', 'port': 9200}])

es = Elasticsearch(hosts=[{"host": "es01", "port": 9200}],
                # connection_class=RequestsHttpConnection, 
                # max_retries=30,
                # retry_on_timeout=True, 
                # request_timeout=30
                       )
print(es)
print(es.ping())
print()
es.indices.create(
                index=index,
                ignore=400,
            )

async def do_things():
    await es.indices.create(
            index="myindex",
            ignore=400,
        )
    print("index Created...................")

# loop = asyncio.get_event_loop()
# loop.run_until_complete(do_things())    
# do_things(index)

app.mount("/static", StaticFiles(directory=cd+"/static"), name="static")


templates = Jinja2Templates(directory=cd+"/templates")
@app.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    result = "Type a number"
    return templates.TemplateResponse("home.html", {"request": request, "result": result})

@app.post("/submittext")
async def read_item(request: Request, text: str = Form(...)):
    result=text
    return templates.TemplateResponse("home.html", {"request": request, "result": result})


@app.post("/predict", response_model=PredictResponse)
def predict(input: PredictRequest, model: Model = Depends(get_model)):
    a = np.array(input.data)
    que, text = a[0], a[1]
    ans = model.predict(que, text)
    return PredictResponse(data=ans)