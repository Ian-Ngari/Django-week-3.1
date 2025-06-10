from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    PostViewSet,
    CommentViewSet,
    UserViewSet,
    SearchViewSet
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'users', UserViewSet, basename='user')
router.register(r'search', SearchViewSet, basename='search')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_id>/comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-comments'),
    path('posts/<int:post_id>/comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),
    path('posts/<int:pk>/like/', PostViewSet.as_view({
        'post': 'like',
        'delete': 'like'
    }), name='post-like'),
    path('comments/<int:pk>/like/', CommentViewSet.as_view({
        'post': 'like',
        'delete': 'like'
    }), name='comment-like'),
    path('users/<int:pk>/follow/', UserViewSet.as_view({
        'post': 'follow',
        'delete': 'follow'
    }), name='user-follow'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]