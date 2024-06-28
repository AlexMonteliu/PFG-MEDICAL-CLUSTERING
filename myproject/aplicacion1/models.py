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

def clean_text(text):#funsion utilizada para preprocesado de texto
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
model = KMeans(n_clusters=true_k, max_iter=100, n_init=5,random_state=42)#Creamos algoritmo k-means
model.fit(X)

df['cluster'] = model.labels_

if 'medical_specialty' in df.columns:
    specialty_cluster_df = df[['medical_specialty', 'cluster']]
    #specialty_cluster_df.to_csv('specialty_cluster_df.csv', index=False)
    most_common_specialty_per_cluster = specialty_cluster_df.groupby('cluster')['medical_specialty'].agg(lambda x: x.mode()[0]).to_dict()

specialty_to_cluster = df.groupby('medical_specialty')['cluster'].agg(lambda x: [x.mode()[0]]).to_dict()


def extract_keywords(text):#Funcion para extraer las palabras clave de informe medico transcrito introducido
    text = clean_text(text)
    tfidf_matrix = vectorizer.transform([text])#Se aplica mismo sistema de vectorizado
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


# Calcula las tres especialidades más comunes por clúster
def get_top_specialties_per_cluster(df, n=3):
    specialty_cluster_df = df[['medical_specialty', 'cluster']]
    top_specialties_per_cluster = {}

    for cluster in range(true_k):
        top_specialties = (
            specialty_cluster_df[specialty_cluster_df['cluster'] == cluster]
            .groupby('medical_specialty')
            .size()
            .nlargest(n)
            .index.tolist()
        )
        top_specialties_per_cluster[cluster] = top_specialties
    
    return top_specialties_per_cluster

top_specialties_per_cluster = get_top_specialties_per_cluster(df)


def print_top_features_per_cluster(model, vectorizer, num_features):
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    
    clusters_features = {}
    for i in range(true_k):
        cluster_features = [terms[ind] for ind in order_centroids[i, :num_features]]
        common_specialties = top_specialties_per_cluster[i]  # Obtener las tres especialidades más comunes
        clusters_features[i] = {
            'features': cluster_features,
            'specialties': common_specialties
        }
    
    return clusters_features

clusters_features = print_top_features_per_cluster(model, vectorizer, 10)


def get_common_clusters_by_specialty(df):
    common_clusters = {}
    grouped = df.groupby('medical_specialty')['cluster'].apply(lambda x: x.value_counts().index[:3])
    
    for specialty, clusters in grouped.items():
        common_clusters[specialty] = list(clusters) + ['No disponible'] * (3 - len(clusters))
        
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



# Variables globales para el contexto de la vista
clusters_features = print_top_features_per_cluster(model, vectorizer, 10)

cluster_titles = {
    0: "0-Medicina General",
    1: "1-Ortopedia Síndrome del Túnel Carpiano",
    2: "2-Notas de Progreso y SOAP",
    3: "3-Consultas e Historial Clínico",
    4: "4-Informes de Cirugía",
    5: "5-Ortopedia Cervical",
    6: "6-Nefrología",
    7: "7-Neurología",
    8: "8-Cirugía General",
    9: "9-Cardiovascular/Pulmonar",
    10: "10-Cirugía de Hombro",
    11: "11-Manejo del Dolor",
    12: "12-Cardiovascular/Pulmonar",
    13: "13-Cardiovascular/Pulmonar",
    14: "14-Gastroenterología",
    15: "15-Radiología",
    16: "16-Ortopedia Extremidades Inferiores",
    17: "17-Obstetricia/Ginecología"
}

cluster_analysis = {
    0: "Este cluster agrupa textos relacionados con la medicina general, cubriendo una variedad de temas como exámenes físicos, enfermedades respiratorias y otras condiciones comunes que se encuentran en la práctica general. Las menciones de 'office' y 'exam' sugieren que muchos de estos documentos podrían ser registros de consultas médicas generales.",
    1: "Los documentos en este cluster están relacionados con la ortopedia, específicamente con procedimientos y condiciones como el síndrome del túnel carpiano, liberaciones de ligamentos y procedimientos endoscópicos ortopédicos.",
    2: "Este cluster contiene documentos que son notas de progreso o registros SOAP (Subjective, Objective, Assessment, Plan). Los temas incluyen diabetes, hipertensión y otros aspectos dietéticos y de peso, que son comunes en las notas de seguimiento de pacientes.",
    3: "Este cluster agrupa documentos de consultas y exámenes de historia clínica y física. Los temas de pérdida de peso, bypass gástrico y dolor sugieren que se trata de consultas detalladas sobre el historial médico del paciente y evaluaciones físicas.",
    4: "Los documentos en este cluster están relacionados con informes de cirugía y transcripciones médicas. Las características indican un enfoque en la calidad y precisión de las transcripciones y reportes quirúrgicos.",
    5: "Similar al Cluster 1, este cluster también se enfoca en ortopedia pero con un enfoque en condiciones y procedimientos de la columna cervical, como discectomías y fusiones.",
    6: "Los documentos en este cluster están relacionados con la nefrología, abordando condiciones renales, fallas, procedimientos como la colocación de stents y catéteres, y la hemodiálisis.",
    7: "Este cluster se centra en neurología, incluyendo procedimientos y condiciones neurológicas como craniotomías, hematomas subdurales y debilidades musculares. El uso de MRI y CT indica un enfoque en imágenes radiológicas neurológicas.",
    8: "Este cluster incluye documentos relacionados con diversas cirugías, desde urológicas y hernias hasta biopsias, cirugías nasales, y procedimientos en gastroenterología y otorrinolaringología.",
    9: "Los documentos en este cluster están enfocados en el sistema cardiovascular y pulmonar, incluyendo procedimientos como cateterismos arteriales, angiografías, y otros estudios cardiacos y pulmonares.",
    10: "Este cluster trata sobre procedimientos quirúrgicos, específicamente relacionados con la eliminación de cuerpos extraños, reparaciones del manguito rotador, desbridamientos y cirugías de hombro.",
    11: "Los documentos en este cluster se centran en el manejo del dolor, incluyendo inyecciones epidurales, estudios de conducción nerviosa y manejo del dolor mediante diversas técnicas.",
    12: "Este cluster también se centra en el sistema cardiovascular y pulmonar, con documentos que mencionan pruebas de esfuerzo, broncoscopias y otros estudios pulmonares.",
    13: "Similar a los clusters 9 y 12, este cluster abarca temas del sistema cardiovascular y pulmonar, con un enfoque en condiciones valvulares como fibrilación auricular, regurgitaciones y ecocardiogramas.",
    14: "Los documentos en este cluster están relacionados con la gastroenterología, abordando procedimientos como colonoscopias, laparoscopias, y cirugías de vesícula biliar y apendicectomías.",
    15: "Este cluster está enfocado en radiología, incluyendo estudios de CT en abdomen y pelvis, con y sin contraste, y otros estudios radiológicos.",
    16: "Este cluster trata sobre ortopedia, específicamente en extremidades inferiores, abarcando fracturas, fijaciones de articulaciones, y procedimientos en rodillas, pies y tobillos.",
    17: "Los documentos en este cluster están relacionados con obstetricia y ginecología, incluyendo temas de embarazo, procedimientos uterinos y vaginales, y cirugías ginecológicas."
}

# Variables para el contexto de la vista
context = {
    'clusters_features': clusters_features,
    'cluster_titles': cluster_titles,
    'cluster_analysis': cluster_analysis,
}
