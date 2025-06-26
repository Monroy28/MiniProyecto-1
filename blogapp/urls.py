from django.urls import path
from .views import BlogListView, BlogDetailView, BlogCreateView, ReviewCreateView, CommentCreateView, login_view, signup_view
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'blogapp'


urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('blog/add/', views.BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', views.ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/add/', views.CommentCreateView.as_view(), name='add_comment'),
    path('accounts/login/', views.login_view, name='custom_login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='blogapp:blog_list'), name='logout'),
    path('blog/statistics/', views.BlogStatisticsView.as_view(), name='blog_statistics'),
]