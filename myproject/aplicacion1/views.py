import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import get_cluster_and_features, print_top_features_per_cluster, get_common_clusters_by_specialty, model, vectorizer, df,get_cluster_and_features, print_top_features_per_cluster, generate_specialties_pie_chart, context
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import generate_specialties_pie_chart
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
@login_required
def hello(request):
    clusters_features = print_top_features_per_cluster(model, vectorizer, 10)
 # Extraer especialidades únicas para el select
    specialties = df['medical_specialty'].unique().tolist()

    cluster_titles = {
    0: "0- General Medicine",
    1: "1- Orthopedics: Carpal Tunnel Syndrome",
    2: "2- Progress Notes and SOAP",
    3: "3- Consultations and Medical History",
    4: "4- Surgery Reports",
    5: "5- Cervical Orthopedics",
    6: "6- Nephrology",
    7: "7- Neurology",
    8: "8- General Surgery",
    9: "9- Cardiovascular Procedures",
    10: "10- Shoulder Surgeries and Foreign Bodies",
    11: "11- Pain Management",
    12: "12- Pulmonary Studies and Stress Tests",
    13: "13- Valvular Conditions and Echocardiograms",
    14: "14- Gastroenterology",
    15: "15- Radiology",
    16: "16- Orthopedics: Lower Extremities",
    17: "17- Obstetrics/Gynecology"
}


    cluster_analysis = {
        0: "This cluster groups texts related to general medicine, covering a variety of topics such as physical exams, respiratory diseases, and other common conditions encountered in general practice. Mentions of 'office' and 'exam' suggest that many of these documents could be records of general medical consultations.",
        1: "The documents in this cluster are related to orthopedics, specifically addressing procedures and conditions such as carpal tunnel syndrome, ligament releases, and orthopedic endoscopic procedures.",
        2: "This cluster contains documents that are progress notes or SOAP records (Subjective, Objective, Assessment, Plan). Topics include diabetes, hypertension, and other dietary and weight-related aspects, which are common in patient follow-up notes.",
        3: "This cluster groups documents from consultations and medical history and physical exams. Topics such as weight loss, gastric bypass, and pain suggest that these are detailed consultations regarding the patient's medical history and physical assessments.",
        4: "The documents in this cluster are related to surgical reports and medical transcriptions. The characteristics indicate a focus on the quality and accuracy of the transcriptions and surgical reports.",
        5: "This cluster also focuses on orthopedics, with an emphasis on cervical spine conditions and procedures, such as discectomies and fusions.",
        6: "The documents in this cluster are related to nephrology, addressing kidney conditions, failures, procedures such as stent and catheter placement, and hemodialysis.",
        7: "This cluster focuses on neurology, including neurological procedures and conditions such as craniotomies, subdural hematomas, and muscle weaknesses. The use of MRI and CT suggests an emphasis on neurological radiological imaging.",
        8: "This cluster includes documents related to various surgeries, ranging from urological procedures and hernias to biopsies, nasal surgeries, and procedures in gastroenterology and otorhinolaryngology",
        9: "The documents in this cluster focus on the cardiovascular and pulmonary systems, including procedures such as arterial catheterizations, angiographies, and other cardiac and pulmonary studies.",
        10: "This cluster covers surgical procedures, specifically related to foreign body removal, rotator cuff repairs, debridements, and shoulder surgeries.",
        11: "The documents in this cluster center on pain management, including epidural injections, nerve conduction studies, and pain management using various techniques",
        12: "This cluster also focuses on the cardiovascular and pulmonary systems, with documents mentioning stress tests, bronchoscopies, and other pulmonary studies.",
        13: "This cluster encompasses topics on the cardiovascular and pulmonary systems, with a focus on valvular conditions such as atrial fibrillation, regurgitations, and echocardiograms.",
        14: "The documents in this cluster are related to gastroenterology, addressing procedures such as colonoscopies, laparoscopies, gallbladder surgeries, and appendectomies.",
        15: "This cluster is focused on radiology, including CT studies of the abdomen and pelvis, with and without contrast, and other radiological studies.",
        16: "This cluster pertains to orthopedics, specifically the lower extremities, covering fractures, joint fixations, and procedures on knees, feet, and ankles.",
        17: "The documents in this cluster are related to obstetrics and gynecology, including topics on pregnancy, uterine and vaginal procedures, and gynecological surgeries."
    }
    common_clusters_by_specialty = get_common_clusters_by_specialty(df)
    context = {
        'clusters_features': clusters_features,
        'cluster_titles': cluster_titles,
        'cluster_analysis': cluster_analysis,
        'common_clusters_by_specialty': common_clusters_by_specialty,
        'specialties': specialties
    }

    return render(request, 'hello.html', context)

@csrf_exempt
@require_POST
@login_required
def predict_cluster(request):
    try:
        data = json.loads(request.body)
        transcription = data.get('transcription', '')
        if transcription:
            cluster, common_specialty, top_features = get_cluster_and_features(transcription)
            response = {
                'cluster': cluster,
                'common_specialty': common_specialty,
                'top_features': top_features
            }
            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'No transcription provided'}, status=400)
    except Exception as e:
        print(f"Error in predict_cluster: {e}")
        return JsonResponse({'error': str(e)}, status=500)



# Especifica el nombre de usuario y la contraseña correctos
CORRECT_USERNAME = 'admin'
CORRECT_PASSWORD = 'admin'

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('hello')  # Redirige a 'hello' después del login exitoso
            else:
                return HttpResponse("Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})




def success_view(request):
    return HttpResponse("Login successful!")

@login_required
def specialties_pie_chart_view(request):
    output_path = generate_specialties_pie_chart()
    with open(output_path, 'r') as file:
        response = HttpResponse(file.read(), content_type='text/html')
    response['Content-Disposition'] = 'inline; filename="specialties_pie_chart.html"'
    return response

# @login_required
@csrf_exempt
def get_reports_by_cluster(request):
    if request.method == 'GET':
        cluster_id = request.GET.get('cluster_id', '').strip()
        if cluster_id:
            try:
                # Convertir el cluster_id a entero si es necesario
                cluster_id = int(cluster_id)

                # Filtrar el DataFrame por el cluster seleccionado
                filtered_df = df[df['cluster'] == cluster_id]

                if not filtered_df.empty:
                    # Obtener los 5 primeros informes. Ajustar el nombre de la columna con el texto del informe
                    top_5_reports = filtered_df['transcription'].tolist()
                    return JsonResponse({'reports': top_5_reports})
                else:
                    return JsonResponse({'reports': [], 'message': 'No se encontraron informes para este clúster.'})
            except ValueError:
                # Si cluster_id no es convertible a int
                return JsonResponse({'error': 'Cluster ID inválido'}, status=400)
            except Exception as e:
                print(f"Error al procesar la solicitud: {e}")
                return JsonResponse({'error': 'Error interno del servidor'}, status=500)
        else:
            return JsonResponse({'error': 'Cluster ID no proporcionado'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

    
@csrf_exempt
def get_reports_by_clusters_and_specialties(request):
    if request.method == 'GET':
        clusters_str = request.GET.get('clusters', '').strip()   # e.g. "0,1,2" ó "ALL"
        specialties_str = request.GET.get('specialties', '').strip()  # e.g. "cardiology,gastroenterology" ó "ALL"

        # Parámetros de paginación (por defecto page=1, page_size=20)
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        if clusters_str and specialties_str:
            try:
                # Manejo de "ALL" para clusters
                if clusters_str == "ALL":
                    cluster_ids = None
                else:
                    # Convierte "0,1,2" a [0,1,2]
                    cluster_ids = [int(cid) for cid in clusters_str.split(',') if cid.isdigit()]

                # Manejo de "ALL" para specialties
                if specialties_str == "ALL":
                    selected_specialties = None
                else:
                    # p.ej. "cardiology,gastroenterology" => ["cardiology","gastroenterology"]
                    selected_specialties = [s.strip().lower() for s in specialties_str.split(',')]

                # 1. Empezamos con df completo
                filtered_df = df

                # 2. Filtro por clusters si no es ALL
                if cluster_ids is not None:
                    filtered_df = filtered_df[filtered_df['cluster'].isin(cluster_ids)]

                # 3. Filtro por especialidades si no es ALL
                if selected_specialties is not None:
                    filtered_df = filtered_df[
                        filtered_df['medical_specialty'].str.strip().str.lower().isin(selected_specialties)
                    ]

                # Si no hay datos
                if filtered_df.empty:
                    return JsonResponse({
                        'clusters_reports': {},
                        'message': 'No se encontraron informes para esos clústeres y especialidades.'
                    })

                # 4. Ordenamos por 'cluster' para que salgan primero todos los informes del cluster más bajo
                filtered_df = filtered_df.sort_values(by='cluster', ascending=True)

                # 5. Unificamos informes en una sola lista, indicando a qué cluster pertenecen
                all_items = []
                for _, row in filtered_df.iterrows():
                    all_items.append({
                        'cluster': row['cluster'],
                        'report': row['transcription']
                    })

                # 6. Paginación manual
                import math
                total_results = len(all_items)
                total_pages = math.ceil(total_results / page_size)
                # Ajustamos página si excede el rango
                if total_pages > 0 and page > total_pages:
                    page = total_pages

                start = (page - 1) * page_size
                end = start + page_size
                paginated_slice = all_items[start:end]

                # 7. Reconstruimos clusters_reports sólo con la parte paginada
                clusters_dict = {}
                for item in paginated_slice:
                    cid = str(item['cluster'])
                    if cid not in clusters_dict:
                        clusters_dict[cid] = []
                    clusters_dict[cid].append(item['report'])

                # 8. Construimos la respuesta con metadatos
                response_data = {
                    'clusters_reports': clusters_dict,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'total_results': total_results,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }

                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'clusters o specialties no proporcionados'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
