from django.http import JsonResponse
from django.shortcuts import render
from .models import get_cluster_and_features, print_top_features_per_cluster, get_common_clusters_by_specialty, model, vectorizer, df
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

@login_required
def hello(request):
    clusters_features = print_top_features_per_cluster(model, vectorizer, 10)
    common_clusters_by_specialty = get_common_clusters_by_specialty(df)
    return render(request, 'hello.html', {'clusters_features': clusters_features, 'common_clusters_by_specialty': common_clusters_by_specialty})

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