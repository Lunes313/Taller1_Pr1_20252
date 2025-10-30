import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os

def statics_view(request):
    
    data = Movie.objects.values('year').annotate(count=Count('id')).order_by('year')
    years = [d['year'] for d in data]
    counts = [d['count'] for d in data]

    plt.figure(figsize=(10,5))
    plt.bar(years, counts, color='skyblue')
    plt.xlabel('Año')
    plt.ylabel('Cantidad de películas')
    plt.title('Películas por año')
    plt.xticks(rotation=90)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Gráfica de películas por género (solo el primero de cada película)
    movies = Movie.objects.all().values('genre')
    genero_count = {}
    for m in movies:
        if m['genre']:
            first_genre = m['genre'].split(',')[0].strip()
            if first_genre:
                genero_count[first_genre] = genero_count.get(first_genre, 0) + 1

    plt.figure(figsize=(8,5))
    plt.bar(genero_count.keys(), genero_count.values(), color='salmon')
    plt.xlabel('Género')
    plt.ylabel('Cantidad de películas')
    plt.title('Películas por género (solo el primero)')
    plt.xticks(rotation=90)
    plt.tight_layout()

    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    plt.close()
    buf2.seek(0)
    genre_image_base64 = base64.b64encode(buf2.getvalue()).decode('utf-8')

    return render(request, 'statics.html', {'chart': image_base64, 'genre_chart': genre_image_base64})


# Create your views here.

def home(request):
    #return HttpResponse("<h1>Welcome to Home Page<h1>")
    #return render(request, 'home.html', {'name': 'Laura Restrepo'})
    searchTerm = request.GET.get('searchMovie')
    movies = Movie.objects.all()
    if searchTerm:
        movies = movies.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()

    # Procesar recomendación
    recommended = None
    similarity = None
    prompt = None
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        if prompt:
            load_dotenv('openAI.env')
            client = OpenAI(api_key=os.environ.get('openai_apikey'))
            response = client.embeddings.create(
                input=[prompt],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
            best_movie = None
            max_similarity = -1
            for movie in Movie.objects.all():
                if movie.emb:
                    movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                    sim = np.dot(prompt_emb, movie_emb) / (np.linalg.norm(prompt_emb) * np.linalg.norm(movie_emb))
                    if sim > max_similarity:
                        max_similarity = sim
                        best_movie = movie
            if best_movie:
                recommended = best_movie
                similarity = max_similarity

    return render(request, 'home.html', {
        'movies': movies,
        'searchTerm': searchTerm,
        'recommended': recommended,
        'similarity': similarity,
        'prompt': prompt
    })

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get("email")
    return render(request, 'signup.html', {'email': email})

def recommend_movie(request):
    recommended = None
    similarity = None
    prompt = None
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        if prompt:
            load_dotenv('openAI.env')
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.embeddings.create(
                input=[prompt],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
            best_movie = None
            max_similarity = -1
            for movie in Movie.objects.all():
                if movie.emb:
                    movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                    sim = np.dot(prompt_emb, movie_emb) / (np.linalg.norm(prompt_emb) * np.linalg.norm(movie_emb))
                    if sim > max_similarity:
                        max_similarity = sim
                        best_movie = movie
            if best_movie:
                recommended = best_movie
                similarity = max_similarity
    return render(request, 'recommend.html', {'recommended': recommended, 'similarity': similarity, 'prompt': prompt})

