from sklearn.feature_extraction.text import TfidfVectorizer


class Vectorizer:
    def __init__(self, corpus):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=5,
            max_df=0.7
        )
        self.descriptions = corpus

    def fit_corpus(self):
        self.tfidf_vectorizer.fit(self.descriptions)

    def transform(self, **kwargs):
        text = kwargs.get("description", self.descriptions)
        return self.tfidf_vectorizer.transform(text)
