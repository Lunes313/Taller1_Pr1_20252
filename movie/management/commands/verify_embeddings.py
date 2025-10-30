import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Verifica los embeddings almacenados en las películas"

    def handle(self, *args, **kwargs):
        for movie in Movie.objects.all():
            if hasattr(movie, 'emb') and movie.emb:
                embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)
                print(movie.title, embedding_vector[:5])  # Muestra los primeros valores
            else:
                print(f"{movie.title} no tiene embedding almacenado.")
