from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    
    path('', views.home, name='home'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:pk>/update/', views.update_post, name='update_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/share/', views.share_post, name='share_post'),
    
    
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/update/', views.update_comment, name='update_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    

    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    
    
    path('user/<int:pk>/follow/', views.follow_user, name='follow_user'),
    
    
    path('search/', views.search_users, name='search_users'),
    
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)