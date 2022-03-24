import nltk

def download_nlp():
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('omw-1.4')


if __name__ == "__main__":
    download_nlp()
