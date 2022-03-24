# WSE
import flask
from flask import request, jsonify
# inference
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from nltk.corpus import wordnet as wn
import pickle
import jieba
import csv
from wafer_ids import wafer_ids

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.
TestResults = [
    {'transaction_id': 'PLSC2105050001',
     'inference_model': 'PLScomment',
     'inference_content': 'PROMIS帳入ERF=8，實物移至Hold Lot Room的”已收費暫放區”存放',
     'inference_file': 'smb://AI_TEMP/LabelInspection/AMD_BOX_0001.jpg',
     'inference_Result': 'Continue',
     'inference_ResultFile': 'smb://AI_TEMP/LabelInspection/Result/AMD_BOX_0001.jpg',
     'inference_ResultConfidence': 99.82
     }
]


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>NLP API for applications.</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/api/inference/PLScomment/test', methods=['GET'])
def api_all():
    return jsonify(TestResults)


@app.route('/api/inference/PLScomment', methods=['GET'])
def api_content():
    if 'content' in request.args:
        content = request.args['content']
    else:
        return "Error: No content provided."

    # return content

    # inference model
    # WordNetLemmatizer requires Pos tags to understand if the word is noun or verb or adjective etc.
    # By default it is set to Noun
    tag_map = defaultdict(lambda: wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    #print(tag_map[tag[0]])
    # keywords
    keywords = []
    with open('keywords.csv') as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            keywords.append(row[0])

    #print(keywords)

    def text_preprocessing(text):
        # lower & remove specific
        text = text.lower()
        text = text.replace('@', ' ')
        text = text.replace('/', ' ')
        text = text.replace('#', ' ')
        text = text.replace('-', ' ')
        text = text.replace('(', ' ')
        text = text.replace(')', ' ')
        text = text.replace('[', ' ')
        text = text.replace(']', ' ')
        text = text.replace(':', ' ')
        text = text.replace('\n', ' ')

        # 中文斷詞
        seg_list = jieba.cut(text, cut_all=False)
        text = " ".join(seg_list)
        #print(text)

        text_words_list = word_tokenize(text)
        #print(text_words_list)
        Final_words = []
        # Initializing WordNetLemmatizer()
        word_Lemmatized = WordNetLemmatizer()
        #print(pos_tag(text_words_list))
        #print(keywords)
        # pos_tag function below will provide the 'tag' i.e if the word is Noun(N) or Verb(V) or something else.
        for word, tag in pos_tag(text_words_list):
            # if word not in all_stopwords:
            if word in keywords:
                word_Final = word_Lemmatized.lemmatize(word, tag_map[tag[0]])

                #print(word_Final)
                Final_words.append(word_Final)
            # The final processed set of words for each iteration will be stored in 'text_final'
        #print(str(Final_words))    
        return str(Final_words)
        

    # Loading Label encoder
    labelencode = pickle.load(open('labelencoder_fitted.pkl', 'rb'))
    # Loading TF-IDF Vectorizer
    Tfidf_vect = pickle.load(open('Tfidf_vect_fitted.pkl', 'rb'))
    # Loading models
    SVM = pickle.load(open('svm_trained_model.sav', 'rb'))

    # Inference
    sample_text = str(content)
    text_file = open("sample_text.txt", "w")
    text_file.write(sample_text)
    text_file.close()

    sample_text_processed = text_preprocessing(sample_text)
    # print(sample_text_processed)

    text_file = open("sample_text_processed.txt", "w")
    text_file.write(sample_text_processed)
    text_file.close()
    sample_text_processed_vectorized = Tfidf_vect.transform([sample_text_processed])

    prediction_SVM = SVM.predict(sample_text_processed_vectorized)
    prediction_SVM_p = SVM.predict_proba(sample_text_processed_vectorized)[0]

    confd = str(round(prediction_SVM_p[prediction_SVM[0]] * 100, 2))
    classname = labelencode.inverse_transform(prediction_SVM)[0]
    # print(classname[9:])
    
    wafer_id = wafer_ids(sample_text)[0]
    wafer_qty = wafer_ids(sample_text)[1]

    ##print(labelencode.inverse_transform(prediction_SVM)[0])

    # export json text_file
    data = {'result': []}
    data['result'].append({
        'classname': classname[9:],
        'confidence': confd,
        'keywords': sample_text_processed,
        'additional_info':{
            'wafer_id:': wafer_id,
            'wafer_qty': wafer_qty
        }
    })
    return jsonify(data)


app.run()
