from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch import helpers
import re

ports = ['localhost:9200']
index = "myindex"
text = """
The city existed for over 1,500 years before Muhammad's migration from Mecca,[5] otherwise known as the Hijrah. Medina was the capital of a rapidly increasing Muslim caliphate under Muhammad's leadership, serving as its base of operations and as the cradle of Islam, where Muhammad's Ummah (Community), composed of the citizens of Medina, known as the Ansar and those who immigrated with Muhammad, known as the Muhajirun, collectively known as the Sahaba, gained huge influence. Medina is home to three prominent mosques, namely al-Masjid an-Nabawi, Masjid Quba'a, and Masjid al-Qiblatayn, with the masjid at Quba'a being the oldest in Islam. A larger portion of the Qur'an was revealed in Medina in contrast to the earlier Meccan surahs.[6][7]

Much like most of the Hejaz, Medina has seen numerous exchanges of power within its comparatively short existence. The region has been controlled by Arabian Jewish tribes (up to the 5th century CE), the 'Aws and Khazraj (up to Muhammad's arrival), Muhammad and the Rashidun (622–660 CE), Umayyads (660–749 CE), Abbasids (749–1254 CE), the Mamluks of Egypt (1254–1517 CE), the Ottomans (1517–1805 CE), the First Saudi State (1805–1811 CE), Muhammad Ali Pasha (1811–1840 CE), the Ottomans for a second time (1840–1918), the Hashemite Sharifate of Mecca (1918–1925 CE) and finally is in the hands of the modern-day Kingdom of Saudi Arabia (1925–present CE).[4]
"""

class Elastic:
    def __init__(self):
        self.es = None
        # self.index = index
        # self.ports = ports
        
    def connect_elasticsearch(self, ports):    
        self.es = AsyncElasticsearch(hosts=ports)
        if self.es.ping():
            print('ElasticSearch  Connected ')
        else:
            print('Awww it could not connect!')
        return self.es

    def delete_index(self, index):
        self.es.indices.delete(index=index, ignore=[400, 404])
        print("index: {} has been deleted.".format(index))

    def create_index(self, index):
        #   Creates an index in Elasticsearch if one isn't already there.

        body = {
        "settings":{
            "number_of_shards":1
        },
        "mappings":{
            "properties":{
                "text":{
                    "type":"text"
                }
            }
        }
        }
  
        # if index not in self.es.indices.get_alias().keys():
        self.es.indices.create(
            index=index,
            body=body,
            ignore=400,
        )
        print("new index: {} created.".format(index))

        # else:
        #     print("{} already exist.".format(index))

    async def bulk_list_data(self, list_of_strings, index):
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

    async def bulk_post(self, list_of_strings, index):
        try:
            # make the bulk call, and get a response
            response = await helpers.async_bulk(self.es, self.bulk_list_data(list_of_strings, index))

            #response = helpers.bulk(elastic, actions, index='employees', doc_type='people')
            print ("\nRESPONSE:", response)
        except Exception as e:
            print("\nERROR:", e)

    def splitTextonWords(self, Text, numberOfWords=1):
        if (numberOfWords > 1):
            t = str.maketrans("\n\t\r", "   ")
            text = Text.translate(t)
            sentlist = text.split(". ")
            x = []
            s = ""
            for item in sentlist:
                s += item
                s = s+". "
                if len(s.split()) > numberOfWords:
                    s = re.sub(' +', ' ', s)
                    x.append(s)
                    s = ""
            # pattern = '(?:\S+\s*){1,'+str(numberOfWords-1)+'}\S+(?!=\s*)'
            # x =re.findall(pattern,text)

        elif (numberOfWords == 1):
            t = str.maketrans("\n\t\r", "   ")
            text = Text.translate(t)
            x = text.split()
        else: 
            x = None
        return x
        

# es = Elastic()
# client = es.connect_elasticsearch(ports)
# es.create_index(index)
# list_of_strings = splitTextonWords(text, 20)
# print(list_of_strings)