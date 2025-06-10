from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Profile, Post, Comment, Notification
from .forms import UserRegisterForm, ProfileUpdateForm, PostForm, CommentForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'social/home.html', {'posts': posts})

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_following = request.user.profile.following.filter(user=profile_user).exists()
    return render(request, 'social/profiles/profile.html', {
        'profile_user': profile_user,
        'is_following': is_following
    })

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'social/profiles/edit_profile.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'social/posts/create.html', {'form': form})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            Notification.objects.create(
                user=post.author,
                message=f"{request.user.username} commented on your post",
                link=reverse('post_detail', args=[post.pk])
            )
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'social/posts/detail.html', {
        'post': post,
        'comment_form': form
    })

@login_required
def share_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        Notification.objects.create(
            user=post.author,
            message=f"{request.user.username} shared your post",
            link=reverse('post_detail', args=[post.pk])
        )
        messages.success(request, "Post shared successfully!")
        return redirect('home')
    return render(request, 'social/posts/share.html', {'post': post})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        Notification.objects.create(
            user=post.author,
            message=f"{request.user.username} liked your post",
            link=reverse('post_detail', args=[post.pk])
        )
    return redirect(request.META.get('HTTP_REFERER', 'home'))

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def mark_notifications_read(request):
    if request.user.is_authenticated:
        request.user.notifications.filter(read=False).update(read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=401)

@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You can't edit this post!")
        return redirect('post_detail', pk=post.pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'social/posts/update.html', {'form': form, 'post': post})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            Notification.objects.create(
                user=post.author,
                message=f"{request.user.username} commented on your post",
                link=reverse('post_detail', args=[post.pk])
            )
            messages.success(request, 'Comment added!')
    return redirect('post_detail', pk=post.pk)

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You can't delete this post!")
        return redirect('post_detail', pk=post.pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'social/posts/confirm_delete.html', {'post': post})

@login_required
def follow_user(request, pk):
    user_to_follow = get_object_or_404(User, pk=pk)
    if request.user == user_to_follow:
        messages.error(request, "You can't follow yourself!")
    else:
        profile_to_follow = user_to_follow.profile
        if request.user.profile.following.filter(user=user_to_follow).exists():
            request.user.profile.following.remove(profile_to_follow)
            messages.success(request, f'You unfollowed {user_to_follow.username}')
        else:
            request.user.profile.following.add(profile_to_follow)
            messages.success(request, f'You followed {user_to_follow.username}')
    return redirect('profile', username=user_to_follow.username)

@login_required
def update_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        messages.error(request, "You can't edit this comment!")
        return redirect('post_detail', pk=comment.post.pk)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated!')
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'social/comments/update.html', {'form': form})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        messages.error(request, "You can't delete this comment!")
    else:
        comment.delete()
        messages.success(request, 'Comment deleted!')
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query) if query else User.objects.none()
    return render(request, 'social/search.html', {'users': users, 'query': query})