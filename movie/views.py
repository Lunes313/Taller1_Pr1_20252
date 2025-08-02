from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

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
    return render(request, 'home.html', {'movies': movies, 'searchTerm': searchTerm})

def about(request):
    #return HttpResponse("<h1>About Us</h1>")
    return render(request, 'about.html')

