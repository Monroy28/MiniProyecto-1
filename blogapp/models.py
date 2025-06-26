# blogapp/models.py

from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Avg, Count
from taggit.managers import TaggableManager
from django.core.validators import MinValueValidator, MaxValueValidator # <-- ¡AÑADE ESTA LÍNEA!


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def average_rating(self):
        # Asegúrate de que esta función esté definida para evitar errores si la usas en tus templates
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    def review_count(self):
        return self.reviews.count()

class Review(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'reviewer') # Un usuario solo puede reseñar un blog una vez
        ordering = ['-created_at']

    def __str__(self):
        return f'Reseña de {self.reviewer.username} para {self.blog.title}'

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Los comentarios más nuevos al final

    def __str__(self):
        return f'Comentario de {self.commenter.username} en reseña de {self.review.blog.title}'
