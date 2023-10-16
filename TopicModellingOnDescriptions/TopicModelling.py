import nltk
import pandas as pd
import itertools

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

# Keyword Extraction: For each project, find keywords -> For each keyword, find which projects it belongs to
# Topic Modelling: Hyperparameter A -> For each topic, go to each project and find if that topic exists in the project

# Preprocess Text
def preprocess_text(text: str) -> str:
  tokens = word_tokenize(text.lower())

  tokens = [word for word in tokens if word.isalpha()]

  stop_words = set(stopwords.words("english"))
  tokens = [word for word in tokens if word not in stop_words]

  lemmatizer = WordNetLemmatizer()
  tokens = [lemmatizer.lemmatize(word) for word in tokens]

  return " ".join(tokens)

def get_possible_umap_params() -> list:
  n_neighbor_params, base_n_neighbor, n_neighbor_multiplier = [], 3, 3
  n_components_params, base_n_components, n_components_multiplier = [], 2, 2
  min_dist_params, base_min_dist, min_dist_multiplier = [], 0.05, 0.1
  for increment in range(0, 3):
    n_neighbor_params.append(base_n_neighbor + (n_neighbor_multiplier * increment))
    n_components_params.append(base_n_components + (n_components_multiplier * increment))
    min_dist_params.append(base_min_dist + (min_dist_multiplier * increment))

  umap_combinations = itertools.product(n_neighbor_params, n_components_params, min_dist_params)
  return list(map(lambda combination : {'n_neighbors': combination[0], 'n_components': combination[1], 'min_dist': combination[2]}, umap_combinations))

def get_possible_hdbscan_params() -> list:
  min_cluster_size_params, base_min_cluster_size, min_cluster_size_multiplier = [], 2, 3
  min_samples_size_params, base_min_samples, min_samples_multiplier = [], 2, 3
  for increment in range(0, 3):
    min_cluster_size_params.append(base_min_cluster_size + (min_cluster_size_multiplier * increment))
    min_samples_size_params.append(base_min_samples + (min_samples_multiplier * increment))

  hdbscan_combinations = itertools.product(min_cluster_size_params, min_samples_size_params)
  return list(map(lambda combination : {'min_cluster_size': combination[0], 'min_samples': combination[1], 'prediction_data': True}, hdbscan_combinations))

if __name__ == '__main__':
    with open('./data.xlsx', 'rb') as descriptions:
        data = pd.read_excel(descriptions)
        data['text'].dropna(inplace=True)
        texts = data['text'].tolist()

        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        preprocessed_texts = []
        for text in texts:
           preprocessed_text = [preprocess_text(token) for token in tokenizer.tokenize(str(text))[1:]]
           preprocessed_texts.append(' '.join(preprocessed_text))

        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        representation_model = KeyBERTInspired()

        umap_params = get_possible_umap_params()
        hdbscan_params = get_possible_hdbscan_params()
        for umap_index, umap_param in enumerate(umap_params):
            for hdbscan_index, hdbscan_param in enumerate(hdbscan_params):
                topic_model = BERTopic(
                    embedding_model=embedding_model,
                    umap_model=UMAP(**umap_param),
                    hdbscan_model=HDBSCAN(**hdbscan_param),
                    representation_model=representation_model,
                    min_topic_size=5,
                    top_n_words=7,
                    n_gram_range=(1, 3),
                    nr_topics=50,
                    calculate_probabilities=True,
                )

                topics, probs = topic_model.fit_transform(preprocessed_texts)
                file_path = './TopicsFromTopicModelling/umap_{0}_hdbscan_{1}.txt'.format(umap_index, hdbscan_index)
                with open(file_path, 'w') as param_file:
                    file_content = "UMAP Parameters: {0}\n\nHDBScan Parameters: {1}\n\n\n".format(umap_param, hdbscan_param)
                    for index in range(len(topics)):
                        topic_representation = topic_model.get_topic(index)
                        if isinstance(topic_representation, bool):
                            break

                        file_content += "Topic: {0}\n".format(index)
                        for keyword in topic_representation:
                            file_content += "{0}\n".format(keyword)
                        file_content += "\n"

                    param_file.write(file_content)