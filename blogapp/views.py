from django.views.generic import ListView, DetailView, CreateView, FormView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment # NO importamos 'Tag' directamente aquí
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm, BlogForm # Asegúrate que estas forms existen en blogapp/forms.py
from django.contrib import messages
from django.db.models import Count, Avg
from django import forms # Mueve esta importación al principio si no está


# --- Vistas del Blog ---

class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 5
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_filter'] = self.request.GET.get('tag')

        context['most_commented'] = Blog.objects.annotate(
            num_comments=Count('reviews')
        ).order_by('-num_comments')[:3]

        context['top_rated'] = Blog.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:3]
        return context


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        context['average'] = round(blog.average_rating(), 1) if hasattr(blog, 'average_rating') else 0
        context['tags'] = blog.tags.all()
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    template_name = 'blogapp/blog_form.html'
    form_class = BlogForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'blogapp/review_form.html'
    login_url = 'blogapp:custom_login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para dejar una reseña.")
            return redirect(reverse_lazy(self.login_url))

        blog_id = self.kwargs['pk']
        user = request.user

        if Review.objects.filter(blog_id=blog_id, reviewer=user).exists():
            messages.error(request, "Ya has enviado una reseña para este blog.")
            return redirect('blogapp:blog_detail', pk=blog_id)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['blog'] = get_object_or_404(Blog, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        form.instance.blog_id = self.kwargs['pk']
        messages.success(self.request, "¡Gracias por tu reseña!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blogapp/comment_form.html'

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.review_id = self.kwargs['review_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})


class BlogStatisticsView(ListView):
    model = Blog
    template_name = 'blogapp/blog_statistics.html'
    context_object_name = 'blogs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_commented'] = Blog.objects.annotate(
            comment_count=Count('reviews')
        ).order_by('-comment_count')[:3]
        context['top_rated'] = Blog.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:3]
        return context


# --- Vistas de Autenticación (¡AHORA USANDO FORMVIEW Y NUEVAS RUTAS!) ---
class CustomLoginView(FormView):
    template_name = 'blogapp/auth/signin.html' # <-- ¡RUTA ACTUALIZADA!
    form_class = AuthenticationForm

class CustomSignupView(FormView):
    template_name = 'blogapp/auth/create_account.html' # <-- ¡RUTA ACTUALIZADA!
    form_class = UserCreationForm
