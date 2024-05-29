from django.http import JsonResponse
from django.shortcuts import render
from .models import get_cluster_and_features

def hello(request):
    return render(request, 'hello.html', {})

def predict_cluster(request):
    transcription = request.GET.get('transcription', '')
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
