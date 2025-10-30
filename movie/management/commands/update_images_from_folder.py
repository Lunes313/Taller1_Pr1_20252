import os
import csv
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Update movie images in the database from a media folder"

    def handle(self, *args, **kwargs):
        # 📥 Ruta de la carpeta con las imágenes
        images_folder = 'media/movie/images/'

        # ✅ Verifica si la carpeta existe
        if not os.path.exists(images_folder):
            self.stderr.write(f"Images folder '{images_folder}' not found.")
            return

        updated_count = 0

        # 📖 Procesamos cada archivo de imagen en la carpeta
        from django.core.files import File
        for image_file in os.listdir(images_folder):
            if image_file.endswith('.png'):
                movie_title = image_file[2:-4]  # Extraemos el título de la película
                try:
                    movie = Movie.objects.get(title=movie_title)
                    image_path = os.path.join(images_folder, image_file)
                    with open(image_path, 'rb') as f:
                        movie.image.save(image_file, File(f), save=True)
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
                except Movie.DoesNotExist:
                    self.stderr.write(f"Movie not found: {movie_title}")
                except Exception as e:
                    self.stderr.write(f"Failed to update {movie_title}: {str(e)}")

        # ✅ Al finalizar, muestra cuántas películas se actualizaron
        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movies from images."))