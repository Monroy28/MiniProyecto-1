from django.urls import path
from .views import (
    BlogListView, BlogDetailView, BlogCreateView, ReviewCreateView,
    CommentCreateView, BlogStatisticsView,
    CustomLoginView, CustomSignupView # Clases de autenticación
)

app_name = 'blogapp'

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('blog/add/', BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/', CommentCreateView.as_view(), name='add_comment'),

    # URLs de Autenticación (¡NUEVOS NOMBRES SI CAMBIASTE!)
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('signup/', CustomSignupView.as_view(), name='signup'),

    # URL de Estadísticas
    path('statistics/', BlogStatisticsView.as_view(), name='blog_statistics'),
]
