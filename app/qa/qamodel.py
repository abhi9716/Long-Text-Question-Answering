import json
import torch
from time import time
from transformers import AutoTokenizer
from onnxruntime import GraphOptimizationLevel, InferenceSession, SessionOptions, get_all_providers
from pathlib import Path

cd = str(Path(__file__).absolute().parents[0]) # root/.../app/qa
pd = str(Path(__file__).absolute().parents[1]) # root/.../../app

# model_path = "qa.opt.quant.onnx"
# provider = "CPUExecutionProvider"

with open(pd+"/config.json") as json_file:
    config = json.load(json_file)

class Model:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(config["tokenizer"])
        self.model = self.create_model_for_provider(cd + "/" + config["model_path"], config["provider"])

    def create_model_for_provider(self, model_path: str, provider: str) -> InferenceSession: 
    
        assert provider in get_all_providers(), f"provider {provider} not found, {get_all_providers()}"

        # Few properties that might have an impact on performances (provided by MS)
        options = SessionOptions()
        options.intra_op_num_threads = 1
        options.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL

        # Load the model as a graph and prepare the CPU backend 
        session = InferenceSession(model_path, options, providers=[provider])
        session.disable_fallback()
            
        return session

    def predict(self, question, text):
        inputs = self.tokenizer(question, text, add_special_tokens=True, return_tensors="pt")
        input_ids = inputs["input_ids"].tolist()[0]
        inputs_onnx= {
                'input_ids' : inputs.input_ids.numpy(),
                'attention_mask' : inputs.attention_mask.numpy(), 
                'token_type_ids' : inputs.token_type_ids.numpy(),
                }
        start_scores, end_scores=self.model.run(None,inputs_onnx)
        answer_start = torch.argmax(torch.tensor(start_scores))
        answer_end = torch.argmax(torch.tensor(end_scores))+1
        answer=self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(input_ids[answer_start : answer_end]))

        return answer

model = Model()

def get_model():
    return model

question = "where Liana Barrientos got married?"
text = r""" New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York.
A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband.
Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other.
In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage.
Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the
2010 marriage license application, according to court documents.
Prosecutors said the marriages were part of an immigration scam.
On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further.
After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective
Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002.
All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say.
Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages.
Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted.
The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s
Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali.
Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force.
If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18.
"""

# a=model.predict(question,text)
# print(a)