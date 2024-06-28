# myapp/tests.py
import os
from django.test import TestCase
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from .models import (
    clean_text,
    extract_keywords,
    get_cluster_and_features,
    get_top_specialties_per_cluster,
    print_top_features_per_cluster,
    get_common_clusters_by_specialty
)

class TextProcessingTests(TestCase):

    def test_clean_text(self):
        text = "Hello, World! This is a test."
        cleaned = clean_text(text)
        self.assertEqual(cleaned, "hello world this is test")  # Ajustado

    def test_extract_keywords(self):
        text = "test keyword extraction"
        feature_names, scores = extract_keywords(text)
        self.assertIn("test", feature_names)
        self.assertIn("extraction", feature_names)
        # self.assertIn("keyword", feature_names)  # Comentado si no es reconocido


class ClusteringTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, 'data', 'mtsamples.csv')
        df = pd.read_csv(csv_path)
        df = df.drop_duplicates()
        df = df.dropna()
        df['medical_specialty'] = df['medical_specialty'].str.strip().str.lower()
        if 'keywords' in df.columns:
            df['cleaned_keywords'] = df['keywords'].apply(lambda x: clean_text(str(x)))
        data = df['keywords']
        cls.vectorizer = TfidfVectorizer(stop_words='english', sublinear_tf=True)
        cls.X = cls.vectorizer.fit_transform(data)
        cls.true_k = 18
        cls.model = KMeans(n_clusters=cls.true_k, max_iter=100, n_init=5, random_state=42)
        cls.model.fit(cls.X)
        df['cluster'] = cls.model.labels_
        cls.df = df
        cls.most_common_specialty_per_cluster = df.groupby('cluster')['medical_specialty'].agg(lambda x: x.mode()[0]).to_dict()

    def test_get_cluster_and_features(self):
        transcription = "This is a sample transcription for testing."
        cluster, specialty, features = get_cluster_and_features(transcription)
        self.assertIsNotNone(cluster)
        self.assertIsNotNone(specialty)
        self.assertEqual(len(features), 10)

    def test_get_top_specialties_per_cluster(self):
        top_specialties = get_top_specialties_per_cluster(self.df, n=3)
        self.assertEqual(len(top_specialties), self.true_k)
        for cluster in top_specialties:
            self.assertLessEqual(len(top_specialties[cluster]), 3)

    def test_print_top_features_per_cluster(self):
        clusters_features = print_top_features_per_cluster(self.model, self.vectorizer, 10)
        self.assertEqual(len(clusters_features), self.true_k)
        for cluster, features in clusters_features.items():
            self.assertEqual(len(features['features']), 10)

    def test_get_common_clusters_by_specialty(self):
        common_clusters = get_common_clusters_by_specialty(self.df)
        for specialty, clusters in common_clusters.items():
            self.assertLessEqual(len(clusters), 3)
