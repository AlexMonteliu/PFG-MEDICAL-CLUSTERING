from django.http import JsonResponse
from django.shortcuts import render
from .models import get_cluster_and_features, print_top_features_per_cluster, get_common_clusters_by_specialty, model, vectorizer, df

def hello(request):
    clusters_features = print_top_features_per_cluster(model, vectorizer, 10)
    common_clusters_by_specialty = get_common_clusters_by_specialty(df)
    return render(request, 'hello.html', {'clusters_features': clusters_features, 'common_clusters_by_specialty': common_clusters_by_specialty})

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
