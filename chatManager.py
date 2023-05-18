import re
import pandas as pd
import datamart_profiler
import os
from contextGen import processDataset
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

class MessageManager:
    def __init__(self,datapath=None):
        if datapath:
            self.context,self.sample = processDataset(datapath) #can input a csv file.
        else:
            self.context = ''
        self.zeroMessage_history = [
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions about the dataset. The input is a random sample of 12 rows of the large dataset. \
                 Input: \n" + self.sample}]
        self.message_history = [
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions about the dataset. The input is a random sample of 12 rows of the large dataset. \
                 The context describes what the headers of the dataset are. At the end of the context the spatial coverage of the data may be described.\
                  At the end of the context the time range of the data may also be described. \n"+self.context}
            ]
        self.basic = "Question:Describe the dataset in two sentences. \
                    The first sentence describes the dataset, and the\
                     second sentence mentions where it might be from. \nAnswer:"
        self.look = "Question:What does the dataset look like? \nAnswer:"
        self.header = "Question:Can the headers of the dataset? \nAnswer:"
        self.values = "Question:What are the value types and ranges for the most important headers of the dataset? \nAnswer:"
        self.temporal = "Question:How does the dataset use time? \nAnswer:"
        self.spatial = "Question:How does the dataset use location? \nAnswer:"
        self.where = "Question:Based on all previous information, can you guess where the dataset is from? \nAnswer:"
        self.unclear = "Question: Is there anything unclear about the data? \nAnswer:"
        self.CoT = "Question:Describe the dataset using all thinking you have previously done.Create a short description\
             encapsulating all of thes elements that were stated above. Take a guess where the dataset is created from. \
                Also, after the description, describe the dataset in one sentence.  \nAnswer:"
        
        self.useCase = "Question:What can this dataset be used for? \
            Be specific, as if you are explaining it to a data science student who needs a project. \nAnswer:"
        
        self.discover="Question: Considering use cases for the dataset, what other datasets could be used with this\
             dataset for more use cases? After answering this question,  also answer: Question: What can this dataset be used for? \
                Be specific, as if you are explaining it to a data science student who needs a project,\nAnswer:"
        

    def get_message_history(self,zero=False):
        if zero:
            return self.zeroMessage_history
        else:
            return self.message_history
    
    def get_last_response(self,zero=False):
        if zero:
            return self.zeroMessage_history[-1]['content']
        else:
            return self.message_history[-1]["content"]
    
    def get_clean_code(self, message):
        '''
        code return by chatgpt is wrapper by ```python ```
        '''
        for pattern in self.regex_patterns:
            result = re.findall(pattern, message, re.DOTALL)
            if len(result):
                return result[0]
    
    def append(self, message, role="user",zero=False):
        if zero:
            self.zeroMessage_history.append(
                {
                "role": role,
                "content": message
            }
            )
        self.message_history.append(
            {
                "role": role,
                "content": message
            }
        )
    
    def reset_message_history(self):
        self.message_history = [
            {"role": "system", "content": "You are an assistant for an online dataset search engine."},
            {"role": "user", "content": "Answer the questions about the dataset. The input is a random sample of 12 rows of the large dataset. \
                The context describes what the headers of the dataset are. At the end of the context the spatial coverage of the data may be described.\
                At the end of the context the time range of the data may also be described. \n"+self.context}]
    
    def gen(self,string,temperature=0.7,zero=False):
        if zero:
            self.append(string, role="user",zero=True)
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.get_message_history(zero=True),
            temperature=temperature)
            response_message = response.choices[0].message.content
            self.append(response_message, role="assistant",zero=True)
        else:
            self.append(string, role="user")
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.get_message_history(),
            temperature=temperature)
            response_message = response.choices[0].message.content
            self.append(response_message, role="assistant")

    def genBasic(self):
        self.gen(self.basic)

    def genCoT(self,temperature=0.7):
        self.gen(self.look,temperature=temperature)
        self.gen(self.header,temperature=temperature)
        self.gen(self.values,temperature=temperature)
        self.gen(self.temporal,temperature=temperature)
        self.gen(self.spatial,temperature=temperature)
        self.gen(self.unclear,temperature=temperature)
        self.gen(self.basic,temperature=temperature)
        self.gen(self.where,temperature=temperature)
        self.gen(self.CoT,temperature=temperature)
    
    def genDiscover(self,temperature=0.7):
        self.gen(self.discover,temperature=temperature)
    
    def genZero(self,temperature=0.7):
        self.gen(self.basic,temperature=temperature,zero=True)

