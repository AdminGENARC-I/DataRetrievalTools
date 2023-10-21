import pandas as pd
import nltk

from keybert import KeyBERT

def get_keywords_keybert(text: str):
    keyphrase_ngram_range = (1, 3)
    top_n = 5
    stop_words = 'english'
    use_maxsum = True
    use_mmr = True
    diversity = 0.7

    kw_extractor = KeyBERT('all-MiniLM-L6-v2')
    return kw_extractor.extract_keywords(text, keyphrase_ngram_range=keyphrase_ngram_range, top_n=top_n, stop_words=stop_words, use_maxsum=use_maxsum, use_mmr=use_mmr, diversity=diversity)

if __name__ == '__main__':
    nltk.download('punkt')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    with open('./data.xlsx', 'rb') as descriptions:
        data = pd.read_excel(descriptions)
        
        projectIds = data['document_id'].tolist()
        texts = data['text'].tolist()

        keywordToProjects = {}
        for description in zip(projectIds, texts):
            if isinstance(description[1], str) and description[1] != None and description[1] != '':
                sentences = tokenizer.tokenize(description[1])[1:]

                keywords = get_keywords_keybert(' '.join(sentences))
                for keywordTuple in keywords:
                    keyword = keywordTuple[0]
                    if keywordToProjects.get(keyword) == None:
                        keywordToProjects[keyword] = (1, [str(description[0])])
                    else:
                        prevValue = keywordToProjects[keyword]
                        keywordToProjects[keyword] = ( prevValue[0] + 1, prevValue[1] + [str(description[0])] )
        
        sortedKeywords = list(sorted(keywordToProjects.items(), key=lambda keyword : keyword[1][0], reverse=True))
        with open('./TopicsFromKeywordExtraction/topics.txt', 'w') as topicFile:
            topicFile.write("Topics From Keyword Extraction with KeyBERT\n\n")
            for sortedKeyword in sortedKeywords:
                projectIdStr = '\n\t'.join(sortedKeyword[1][1])
                topicFile.write("\nTopic \"{0}\" found in {1} projects:\n\t{2}".format(sortedKeyword[0], sortedKeyword[1][0], projectIdStr))