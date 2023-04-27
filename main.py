import datamart_profiler
import io
import pandas as pd
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def formatContext(contextArr,sample):
    result=""
    for d in contextArr:
        result+="Column "+d['name']+" is a "+d['structural_type']+". "
        if('num_distinct_values' in d.keys()):
            result+="There are "+str(d['num_distinct_values'])+" distinct values. "
        if('coverage' in d.keys()):
            result+="The range of values are from "+str(d['coverage'][0])+" to "+str(d['coverage'][1])+". "
        result+="The semantic types are: "
        for s in d['semantic_types']:
            result+=s+", "
        result=result[:-2]
        result+=". "
        result+="\n"
    final = "Input: \n" + sample + "\n\n" + "Context: \n" + result
    return final

def processDataset(datapath):
    print("Processing dataset:" +datapath)
    print('\n')
    metadata = datamart_profiler.process_dataset(datapath)
    contextArr=[]
    for i in range(len(metadata['columns'])):
        metDict = metadata['columns'][i]
        cDict={'name':metDict['name']
               ,'structural_type':metDict['structural_type'],
               'semantic_types':metDict['semantic_types']}
        if('num_distinct_values' in metDict.keys()):
            cDict['num_distinct_values'] = metDict['num_distinct_values']
        if('coverage' in metDict.keys()):
            low=0
            high=0
            for i in range(len(metDict['coverage'])):
                if(metDict['coverage'][i]['range']['gte']<low):
                    low=metDict['coverage'][i]['range']['gte']
                if(metDict['coverage'][i]['range']['lte']>high):
                    high=metDict['coverage'][i]['range']['lte']
            cDict['coverage'] = [low,high]
        contextArr.append(cDict)
    
    df = pd.read_csv(datapath)
    df = df.sample(5)
    sample = df.to_csv(index=False)

    context=formatContext(contextArr,sample)
    return context

def genPrompts(context):

    beginOneS = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question:Describe the dataset in two sentences. The first sentence describes the dataset, and the second sentence mentions where it might be from. \nAnswer:"},
            ],
        temperature=0.85)
    print("2 Sentence dataset description: "+beginOneS.choices[0]['message']['content'])
    print('\n')

    second = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question:What does the dataset look like?\nAnswer:"},
            ],
        temperature=0.75)
    print("What the dataset looks like: "+second.choices[0]['message']['content'])
    print('\n')

    third = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question: Can the headers be grouped in any way? How?\nAnswer:"},
            ],
        temperature=0.75)
    print("How can the headers be grouped?: "+third.choices[0]['message']['content'])
    print('\n')

    fourth = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question: What are the value type and ranges for the most important headers?\nAnswer:"},
            ],
        temperature=0.75)
    print("Header value information: "+fourth.choices[0]['message']['content'])
    print('\n')

    fifth = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions about the dataset. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are.\n"+context+"\
                    Question: Where may the dataset from? Make a guess. \nAnswer:"},
            ],
        temperature=0.9)
    print("Where might the dataset be from: "+fifth.choices[0]['message']['content'])
    print('\n')

    sixth = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question: In what way does the dataset mention time? \nAnswer:"},
            ],
        temperature=0.75)
    print("How the dataset uses time: "+sixth.choices[0]['message']['content'])
    print('\n')

    seventh = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question: In what way does the dataset mention location? \nAnswer:"},
            ],
        temperature=0.75)
    print("How the dataset uses location: "+seventh.choices[0]['message']['content'])
    print('\n')

    eigth = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question: Is the dataset clear, or is there reason to doubt quality? \nAnswer:"},
            ],
        temperature=0.75)
    print("Inferred data quality: "+eigth.choices[0]['message']['content'])
    print('\n')

    ninth = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are an assistant for an online dataset search engine."},
                {"role": "user", "content": "Answer the questions while using the input and context. The input is a random sample of 5 rows of the large dataset. \
                 The context describes what the headers of the dataset are. If you are not sure about the answer, infer it on your own.\n"+context+"\
                    Question: What can this dataset be used for? Be specific, as if you are explaining it to a data science student who needs a project.  \nAnswer:"},
            ],
        temperature=0.9)
    print("Dataset possibilites: "+ninth.choices[0]['message']['content'])
    print('\n')


if __name__ == "__main__":
    context = processDataset('datasets/meeting.csv')
    genPrompts(context)