import os
from django.shortcuts import render
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import plotly.express as px
import plotly.io as pio

# Construir la ruta absoluta al archivo CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, 'data', 'mtsamples.csv')

# Cargar y preprocesar los datos
df = pd.read_csv(csv_path)
df = df.drop_duplicates()
df = df.dropna()
df['medical_specialty'] = df['medical_specialty'].str.strip().str.lower()

# Eliminar algunas filas de 'surgery' para balancear el dataset
if 'medical_specialty' in df.columns:
    count_surgery = df[df['medical_specialty'] == 'surgery'].shape[0]
    if count_surgery > 400:
        surgery_indices = df[df['medical_specialty'] == 'surgery'].index[:500]
        df.drop(surgery_indices, inplace=True)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
    text = re.sub(r'\s+', ' ', text, flags=re.I)
    text = text.strip()
    return text

if 'keywords' in df.columns:
    df['cleaned_keywords'] = df['keywords'].apply(lambda x: clean_text(str(x)))

data = df['keywords']
vectorizer = TfidfVectorizer(stop_words='english', sublinear_tf=True)
X = vectorizer.fit_transform(data)#parametro que va a contener preescripcione vectorizadas

true_k = 18 #definimos numero de clusters
model = KMeans(n_clusters=true_k, max_iter=100, n_init=5)
model.fit(X)

df['cluster'] = model.labels_

if 'medical_specialty' in df.columns:
    specialty_cluster_df = df[['medical_specialty', 'cluster']]
    specialty_cluster_df.to_csv('specialty_cluster_df.csv', index=False)
    most_common_specialty_per_cluster = specialty_cluster_df.groupby('cluster')['medical_specialty'].agg(lambda x: x.mode()[0]).to_dict()

specialty_to_cluster = df.groupby('medical_specialty')['cluster'].agg(lambda x: [x.mode()[0]]).to_dict()

def extract_keywords(text):
    text = clean_text(text)
    tfidf_matrix = vectorizer.transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()
    return feature_names, scores

def get_cluster_and_features(transcription):
    feature_names, scores = extract_keywords(transcription)
    new_tfidf = vectorizer.transform([transcription])
    predicted_cluster = model.predict(new_tfidf)
    common_specialty = most_common_specialty_per_cluster[int(predicted_cluster[0])]  # Convertir a int
    
    # Obtenemos  los índices de las 10 características más importantes
    top_feature_indices = scores.argsort()[::-1][:10]
    top_features = [feature_names[i] for i in top_feature_indices]
    
    print(f"Cluster: {predicted_cluster[0]}, Common Specialty: {common_specialty}, Top Features: {top_features}")
    return str(predicted_cluster[0]), common_specialty, top_features

def print_top_features_per_cluster(model, vectorizer, num_features):
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    
    clusters_features = {}
    for i in range(true_k):
        cluster_features = [terms[ind] for ind in order_centroids[i, :num_features]]
        common_specialty = most_common_specialty_per_cluster[i]  # Obtener la especialidad más común
        clusters_features[i] = {
            'features': cluster_features,
            'specialty': common_specialty
        }
    
    return clusters_features

def get_common_clusters_by_specialty(df):
    common_clusters = df.groupby('medical_specialty')['cluster'].agg(lambda x: x.mode()[0]).to_dict()
    return common_clusters

def generate_interactive_pca_plot():
    # PCA para reducir a 3 componentes principales
    pca = PCA(n_components=3)
    reduced_features = pca.fit_transform(X.toarray())

    # Creo un gráfico interactivo 3D con Plotly
    fig = px.scatter_3d(
        x=reduced_features[:, 0], 
        y=reduced_features[:, 1], 
        z=reduced_features[:, 2], 
        color=model.labels_,
        labels={'x': 'PC1', 'y': 'PC2', 'z': 'PC3'},
        title='KMeans Clusters (3D PCA)',
    )

    # Guardoel gafiko interactivo como archivo HTML
    output_path = os.path.join(BASE_DIR, 'static', 'assets', 'clusters_3d.html')
    pio.write_html(fig, file=output_path, auto_open=False)
    print(f"Guardando el gráfico en: {output_path}")

# Llamado a la funcion para generar grafico
generate_interactive_pca_plot()

def generate_specialties_pie_chart():
    # Contar el número de textos por especialidad
    specialties_count = df['medical_specialty'].value_counts().reset_index()
    specialties_count.columns = ['Especialidad', 'Conteo']

    # Crear gráfico de pastel
    fig = px.pie(
        specialties_count, 
        names='Especialidad', 
        values='Conteo', 
        title='Distribución de Especialidades Médicas'
    )

    # Guardar el gráfico interactivo como archivo HTML
    output_path = os.path.join(BASE_DIR, 'static', 'assets', 'specialties_pie_chart.html')
    print(f"Guardando el gráfico en: {output_path}")
    pio.write_html(fig, file=output_path, auto_open=False)
    return output_path


