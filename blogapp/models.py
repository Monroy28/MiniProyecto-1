from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField # <-- Importa esto
from ckeditor_uploader.fields import RichTextUploadingField # <-- Importa esto para subir imágenes

# Modelo de Blog (Artículo)
class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField() # <-- Cambiado a RichTextUploadingField
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)
        return 0.0

# Modelo de Reseña (Review)
class Review(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_made')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = RichTextField(blank=True, null=True, config_name='simple_toolbar') # <-- Cambiado a RichTextField y usa una toolbar específica
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'reviewer')

    def __str__(self):
        return f'Review for "{self.blog.title}" by {self.reviewer.username}'

# Modelo de Comentario (Comment)
class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_made')
    content = RichTextField(config_name='simple_toolbar') # <-- Cambiado a RichTextField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.commenter.username} on review for "{self.review.blog.title}"'