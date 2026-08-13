from dataclasses import dataclass
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import KBArticle

@dataclass
class RetrievedArticle:
    id: str
    title: str
    body: str
    category: str
    score: float

class KnowledgeBaseIndex:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self.articles: List[KBArticle] = []

    def build(self, articles: List[KBArticle]):
        self.articles = articles
        corpus = [a.title + ". " + a.body for a in articles]
        if not corpus:
            self.matrix = None
            return
        self.matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, k: int = 3, min_score: float = 0.25):
        if self.matrix is None or not self.articles:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix)[0]
        ranked = sorted(zip(self.articles, sims), key=lambda x: x[1], reverse=True)
        out = []
        for article, score in ranked[:k]:
            if score < min_score:
                continue
            out.append(RetrievedArticle(article.id, article.title, article.body, article.category, float(round(score, 4))))
        return out

kb_index = KnowledgeBaseIndex()
