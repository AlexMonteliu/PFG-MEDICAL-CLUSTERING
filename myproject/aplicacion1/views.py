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

@login_required
@login_required
def hello(request):
    clusters_features = print_top_features_per_cluster(model, vectorizer, 10)

    cluster_titles = {
        0: "0- Medicina General",
        1: "1- Ortopedia Síndrome del Túnel Carpiano",
        2: "2- Notas de Progreso y SOAP",
        3: "3- Consultas e Historial Clínico",
        4: "4- Informes de Cirugía",
        5: "5- Ortopedia Cervical",
        6: "6- Nefrología",
        7: "7- Neurología",
        8: "8- Cirugía General",
        9: "9- Procedimientos Cardiovasculares",
        10:"10 Cirugía de Hombro",
        11:"11- Manejo del Dolor",
        12:"12- Estudios Pulmonares y Pruebas de Esfuerzo",
        13:"13- Condiciones Valvulares y Ecocardiogramas",
        14:"14- Gastroenterología",
        15:"15- Radiología",
        16:"16- Ortopedia Extremidades Inferiores",
        17:"17- Obstetricia/Ginecología"
    }

    cluster_analysis = {
        0: "Este cluster agrupa textos relacionados con la medicina general, cubriendo una variedad de temas como exámenes físicos, enfermedades respiratorias y otras condiciones comunes que se encuentran en la práctica general. Las menciones de 'office' y 'exam' sugieren que muchos de estos documentos podrían ser registros de consultas médicas generales.",
        1: "Los documentos en este cluster están relacionados con la ortopedia, específicamente con procedimientos y condiciones como el síndrome del túnel carpiano, liberaciones de ligamentos y procedimientos endoscópicos ortopédicos.",
        2: "Este cluster contiene documentos que son notas de progreso o registros SOAP (Subjective, Objective, Assessment, Plan). Los temas incluyen diabetes, hipertensión y otros aspectos dietéticos y de peso, que son comunes en las notas de seguimiento de pacientes.",
        3: "Este cluster agrupa documentos de consultas y exámenes de historia clínica y física. Los temas de pérdida de peso, bypass gástrico y dolor sugieren que se trata de consultas detalladas sobre el historial médico del paciente y evaluaciones físicas.",
        4: "Los documentos en este cluster están relacionados con informes de cirugía y transcripciones médicas. Las características indican un enfoque en la calidad y precisión de las transcripciones y reportes quirúrgicos.",
        5: "Este cluster también se enfoca en ortopedia con un enfoque en condiciones y procedimientos de la columna cervical, como discectomías y fusiones.",
        6: "Los documentos en este cluster están relacionados con la nefrología, abordando condiciones renales, fallas, procedimientos como la colocación de stents y catéteres, y la hemodiálisis.",
        7: "Este cluster se centra en neurología, incluyendo procedimientos y condiciones neurológicas como craniotomías, hematomas subdurales y debilidades musculares. El uso de MRI y CT indica un enfoque en imágenes radiológicas neurológicas.",
        8: "Este cluster incluye documentos relacionados con diversas cirugías, desde urológicas y herdesde urológicas y hernias hasta biopsias, cirugías nasales, y procedimientos en gastroenterología y otorrinolaringología.",
        9: "Los documentos en este cluster están enfocados en el sistema cardiovascular y pulmonar, incluyendo procedimientos como cateterismos arteriales, angiografías, y otros estudios cardiacos y pulmonares.",
        10: "Este cluster trata sobre procedimientos quirúrgicos, específicamente relacionados con la eliminación de cuerpos extraños, reparaciones del manguito rotador, desbridamientos y cirugías de hombro.",
        11: "Los documentos en este cluster se centran en el manejo del dolor, incluyendo inyecciones epidurales, estudios de conducción nerviosa y manejo del dolor mediante diversas técnicas.",
        12: "Este cluster también se centra en el sistema cardiovascular y pulmonar, con documentos que mencionan pruebas de esfuerzo, broncoscopias y otros estudios pulmonares.",
        13: "Este cluster abarca temas del sistema cardiovascular y pulmonar, con un enfoque en condiciones valvulares como fibrilación auricular, regurgitaciones y ecocardiogramas.",
        14: "Los documentos en este cluster están relacionados con la gastroenterología, abordando procedimientos como colonoscopias, laparoscopias, y cirugías de vesícula biliar y apendicectomías.",
        15: "Este cluster está enfocado en radiología, incluyendo estudios de CT en abdomen y pelvis, con y sin contraste, y otros estudios radiológicos.",
        16: "Este cluster trata sobre ortopedia, específicamente en extremidades inferiores, abarcando fracturas, fijaciones de articulaciones, y procedimientos en rodillas, pies y tobillos.",
        17: "Los documentos en este cluster están relacionados con obstetricia y ginecología, incluyendo temas de embarazo, procedimientos uterinos y vaginales, y cirugías ginecológicas."
    }
    common_clusters_by_specialty = get_common_clusters_by_specialty(df)
    context = {
        'clusters_features': clusters_features,
        'cluster_titles': cluster_titles,
        'cluster_analysis': cluster_analysis,
        'common_clusters_by_specialty': common_clusters_by_specialty
    }

    return render(request, 'hello.html', context)

@login_required
def predict_cluster(request):
    transcription = request.GET.get('transcription', '')
    try:
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
            if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
                # Autentica al usuario manualmente
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('hello')  # Redirige a 'hello' después del login exitoso
                else:
                    # Crear el usuario manualmente si no existe
                    from django.contrib.auth.models import User
                    user = User.objects.create_user(username=username, password=password)
                    user.save()
                    login(request, user)
                    return redirect('hello')
            else:
                return HttpResponse("Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



def success_view(request):
    return HttpResponse("Login successful!")

def specialties_pie_chart_view(request):
    output_path = generate_specialties_pie_chart()
    with open(output_path, 'r') as file:
        response = HttpResponse(file.read(), content_type='text/html')
    response['Content-Disposition'] = 'inline; filename="specialties_pie_chart.html"'
    return response