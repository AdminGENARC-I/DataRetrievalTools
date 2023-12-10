import pandas as pd

from os import environ
from openai import OpenAI

# TODO: OpenAI KEY
api_key = "Paste your OpenAI key in place of this text"

with open('./data.xlsx', 'rb') as data_file:
    data = pd.read_excel(data_file)
    data['text'].dropna(inplace=True)
    descriptions = data['text'].tolist()
    formatted_descriptions = " | ".join(list(map(lambda text: str(text), descriptions)))
    
    client = OpenAI(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a very efficient and fast but equally wise architecture professor. Your task is to go over the descriptions we provide and find 100 most common topics found in these descriptions."},
            {"role": "user", "content": "Here are the descriptions, each seperated by a vertical line: {0}".format(formatted_descriptions)}
        ]
    )
        
    with open('./output.txt', 'w') as output_file:
        output_file.write(completion['choices'][0]['message']['content'])