from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment, Tag
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from .forms import ReviewForm
from django.contrib import messages
from .forms import BlogForm
from django.db.models import Count, Avg



class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 5  # Muestra 5 blogs por página. Puedes ajustar este número.
    ordering = ['-created_at']  # Ordena los blogs por fecha de creación, los más nuevos primero.

    
    


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        context['average'] = round(blog.average_rating(), 1)
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



from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Review
from .forms import ReviewForm
from django.core.paginator import Paginator

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'blogapp/review_form.html'
    login_url = 'login'  # Asegúrate de que esta sea la URL name de tu vista de login

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para dejar una reseña.")
            return redirect(self.login_url)

        blog_id = self.kwargs['pk']
        user = request.user

        # Previene duplicados
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


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('blogapp:blog_list')  # Redirige a la vista basada en clase de blog_list
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})



def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Crear el usuario
            login(request, user)  # Iniciar sesión automáticamente después del registro
            return redirect('blogapp:blog_list')  # Redirigir al listado de blogs
        else:
            print("Formulario no válido", form.errors)
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 4  # Cambiado a 4 para mostrar 4 blogs por página
    ordering = ['-created_at']  # Ordena los blogs por fecha de creación, los más nuevos primero.

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_filter'] = self.request.GET.get('tag')  # para mostrarlo en la plantilla

        # 🔹 Blogs más comentados
        context['most_commented'] = Blog.objects.annotate(
            num_comments=Count('reviews')
        ).order_by('-num_comments')[:3]

        # 🔹 Blogs mejor puntuados
        context['top_rated'] = Blog.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:3]
        return context

