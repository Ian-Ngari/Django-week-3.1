from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from social.models import Profile, Post, Comment
from social.api.serializers import (
    UserSerializer, 
    ProfileSerializer,
    PostSerializer,
    CommentSerializer
)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Profile.objects.filter(user__id=user_id)
        return Profile.objects.all()

    @action(detail=True, methods=['put'])
    def update_profile(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.method == 'POST':
            post.likes.add(request.user)
            return Response({'status': 'liked'}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            post.likes.remove(request.user)
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post__id=post_id).order_by('-created_at')

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        comment = self.get_object()
        if request.method == 'POST':
            comment.likes.add(request.user)
            return Response({'status': 'liked'}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            comment.likes.remove(request.user)
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post', 'delete'])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()
        profile = request.user.profile
        
        if request.method == 'POST':
            if profile.following.filter(user=user_to_follow).exists():
                return Response({'status': 'already following'}, status=status.HTTP_400_BAD_REQUEST)
            profile.following.add(user_to_follow.profile)
            return Response({'status': 'following'}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if not profile.following.filter(user=user_to_follow).exists():
                return Response({'status': 'not following'}, status=status.HTTP_400_BAD_REQUEST)
            profile.following.remove(user_to_follow.profile)
            return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)

class SearchViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response([], status=status.HTTP_200_OK)
        
        users = User.objects.filter(username__icontains=query)
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)