from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.shortcuts import render, redirect # Importación única de render y redirect
from django import forms # Importa 'forms' una sola vez al inicio

# Si vas a usar formularios de autenticación de Django directamente (aunque el JS lo envíe a GraphQL)
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
# (Pero no los necesitas si estás usando forms.Form simples como has definido abajo)


class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content']
    # Asegúrate de que este template 'blog_form.html' esté en:
    # blogapp/templates/blog_form.html
    # O si está en blogapp/templates/blogapp/, cambia a 'blogapp/blog_form.html'
    template_name = 'blog_form.html' 

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})


class ReviewCreateView(CreateView):
    model = Review
    fields = ['rating', 'comment']
    template_name = 'blogapp/review_form.html'

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        form.instance.blog_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blogapp/comment_form.html'

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.review_id = self.kwargs['review_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})

# La función blog_statistics_view está correctamente fuera de las clases ahora
def blog_statistics_view(request):
    """
    Vista para mostrar estadísticas del blog.
    Calcula los blogs más comentados y mejor puntuados.
    """
    # Blogs más comentados:
    most_commented = Blog.objects.annotate(
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-review_count')[:5]

    # Blogs mejor puntuados:
    top_rated = Blog.objects.exclude(reviews__rating__isnull=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:5]

    context = {
        'most_commented': most_commented,
        'top_rated': top_rated,
    }
    return render(request, 'blogapp/blog_statistics.html', context)

# Vistas para los formularios de Autenticación (para renderizar los templates)
# Las clases de formulario (LoginForm, SignupForm) ahora se definen fuera de las funciones
class LoginForm(forms.Form):
    """Formulario simple de login para renderizar los campos."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

def custom_login_view(request):
    """Vista para renderizar el formulario de inicio de sesión."""
    context = {'form': LoginForm()}
    return render(request, 'blogapp/registration/login.html', context)

class SignupForm(forms.Form):
    """Formulario simple de registro para renderizar los campos."""
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

def signup_view(request):
    """Vista para renderizar el formulario de creación de cuenta."""
    context = {'form': SignupForm()}
    return render(request, 'blogapp/registration/signup.html', context)
