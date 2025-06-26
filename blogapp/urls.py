from django.urls import path

from .views import (
    BlogListView, BlogDetailView, ReviewCreateView, CommentCreateView, BlogCreateView,
    blog_statistics_view, 
    custom_login_view,    
    signup_view           
)

app_name = 'blogapp'

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('blog/add/', BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('statistics/', blog_statistics_view, name='blog_statistics'),
    path('login/', custom_login_view, name='custom_login'),
    path('signup/', signup_view, name='signup'),
]