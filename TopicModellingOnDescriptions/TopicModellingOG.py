from typing import Mapping, Tuple
import nltk
from numpy import nan
import pandas as pd
from sympy import true

from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from bertopic.representation import KeyBERTInspired

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Preprocess Text
def preprocess_text(text: str) -> str:
    custom_stop_words = ['architect', 'architectural', 'architecture', 'building', 
                        'built', 'cities', 'city', 'design', 'designer', 'facade', 
                        'space', 'spaces', 'project', 'façade', 'buildings', 
                        'construction', 'constructions']
    
    stop_words = set(stopwords.words("english"))
    for custom_stop_word in custom_stop_words:
        stop_words.add(custom_stop_word)
    
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return " ".join(tokens)


# Get Projects with ID and preprocessed Descriptions
def get_projects():
    if len(get_projects.projects) == 0:
        with open('./data.xlsx', 'rb') as descriptions:
            data = pd.read_excel(descriptions)
            data.dropna(inplace=True)
            projects = [(x, y) for x, y in zip(data['document_id'], data['text'])]
            
            tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
            for project in projects:
                if isinstance(project[1], str):
                    preprocessed_description = ' '.join([preprocess_text(token) for token in tokenizer.tokenize(project[1])[1:]])
                    get_projects.projects.append((str(project[0]), preprocessed_description))
    
    return get_projects.projects
get_projects.projects = []

# Find Topic Words in Project Descriptions
def get_projects_for_topic(keywords: Mapping[str, Tuple[str, float]]) -> list[str]:
    project_ids = []

    projects = get_projects()
    for project in projects:
        for keyword in keywords:
            keyword_str = keyword[0]
            if project[1].find(keyword_str) != -1:
                project_ids.append(project[0])
                break
    
    return project_ids

if __name__ == '__main__':
    projects = get_projects()
    descriptions = [project[1] for project in projects]
    
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    representation_model = KeyBERTInspired()
    
    umap_param = {'n_neighbors': 6, 'n_components': 4, 'min_dist': 0.25}
    hdbscan_param = {'min_cluster_size': 2, 'min_samples': 2, 'prediction_data': True}
    
    possible_num_topics = [30, 50, 70]
    for num_topics in possible_num_topics:
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=UMAP(**umap_param),
            hdbscan_model=HDBSCAN(**hdbscan_param),
            representation_model=representation_model,
            min_topic_size=5,
            top_n_words=7,
            n_gram_range=(1, 3),
            nr_topics=num_topics,
            calculate_probabilities=True,
            )
        
        topics, probs = topic_model.fit_transform(descriptions)
        
        with open('./TopicsFromTopicModellingOG/topics_{0}.txt'.format(num_topics), 'w') as file:
            file_content = "Topic Modelling with Topic-to-Project Mappings\n"
            file_content += "UMAP Parameters: {0}\nHDBScan Parameters: {1}\n\n".format(umap_param, hdbscan_param)
            
            for index in range(len(topics)):
                topic_representation = topic_model.get_topic(index)
                if isinstance(topic_representation, bool):
                    break
                
                project_ids = get_projects_for_topic(topic_representation)
                
                file_content += "Topic: {0} -> [{1}]\n".format(str(index), ', '.join(project_ids))
                for keyword in topic_representation:
                    file_content += "{0}\n".format(keyword)
                file_content += "\n"
                
            file.write(file_content)