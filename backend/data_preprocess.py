from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import string

df = pd.read_csv("./job_dataset/upwork-jobs.csv")
descriptions = df["description"].astype(str).tolist()

stop_words = set(stopwords.words('english'))


def get_metadata():
    return df.reset_index().values


def preprocess():
    preprocessed_descriptions = []
    for description in descriptions:
        text = description.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        tokens = [token for token in word_tokenize(text) if token not in stop_words]
        preprocessed_descriptions.append(" ".join(tokens))
    return preprocessed_descriptions
