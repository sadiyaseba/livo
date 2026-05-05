from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import PostForm
from .models import Post
from comments.models import Comment
from django.contrib import messages
import json


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            # User is already validated by form logic but we explicitly set it for clarity
            post.user = request.user
            post.save()
            messages.success(request, f"Your {post.get_type_display()} has been published successfully!")
            return redirect('dashboard')
    else:
        form = PostForm(user=request.user)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Your {post.get_type_display()} has been updated.")
            return redirect('dashboard')
    else:
        form = PostForm(instance=post, user=request.user)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post_type = post.get_type_display()
        post.delete()
        messages.success(request, f"Your {post_type} has been deleted.")
    return redirect('dashboard')


def post_feed(request, post_type):
    valid_types = ['ROOM', 'FOOD', 'HELP']
    if post_type not in valid_types:
        return redirect('landing')

    context = {
        'post_type': post_type,
    }

    category_names = {
        'ROOM': 'Roommate Listings',
        'FOOD': 'Meal Discoveries',
        'HELP': 'Household Services Directory'
    }
    context['category_name'] = category_names.get(post_type, 'Community Wall')

    if post_type == 'HELP':
        # HELP feed queries Househelp profiles directly, not Posts.
        from househelp.models import Househelp, SkillTag
        helps = Househelp.objects.all().select_related('user')

        max_salary = request.GET.get('max_salary')
        skill_ids = request.GET.getlist('skills')
        city = request.GET.get('city')
        area = request.GET.get('area')

        if city:
            helps = helps.filter(city__icontains=city)
        if area:
            helps = helps.filter(area__icontains=area)
        if max_salary and max_salary.isdigit():
            helps = helps.filter(expected_salary__lte=int(max_salary))
        if skill_ids:
            # Filter helps who have ANY of the selected skills
            helps = helps.filter(skills__id__in=skill_ids)

        context['househelps'] = helps.distinct()
        context['skills'] = SkillTag.objects.all()
        # Pass selected skills back to context for checkbox state
        context['selected_skills'] = [int(sid) for sid in skill_ids if sid.isdigit()]


    else:
        # ROOM and FOOD feeds query Posts.
        posts = Post.objects.filter(type=post_type, availability=True) \
            .order_by('-created_at') \
            .select_related('user', 'apartment') \
            .prefetch_related('comments', 'comments__user')

        max_price = request.GET.get('max_price')

        if post_type == 'ROOM':
            area = request.GET.get('area')
            city = request.GET.get('city')
            if area:
                posts = posts.filter(apartment__area__icontains=area)
            if city:
                posts = posts.filter(apartment__city__icontains=city)
            if max_price and max_price.replace('.', '', 1).isdigit():
                posts = posts.filter(price__lte=float(max_price))


        elif post_type == 'FOOD':
            meal_type = request.GET.get('meal_type')
            if max_price and max_price.replace('.', '', 1).isdigit():
                posts = posts.filter(price__lte=float(max_price))
            if meal_type:
                # Basic text match in title/description for meal types since VENDORS use posts.
                from django.db.models import Q
                posts = posts.filter(Q(title__icontains=meal_type) | Q(description__icontains=meal_type))

        context['posts'] = posts

    return render(request, 'posts/feed.html', context)


@login_required
@require_POST
def toggle_like_ajax(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Since we are using simple integer likes as requested:
    # We'll just increment for now. (Facebook style usually toggles, but without liked_by list,
    # we'll just implement a simple +1 "heart" action).
    post.likes += 1
    post.save()
    return JsonResponse({
        'status': 'success',
        'likes_count': post.likes
    })


@login_required
@require_POST
def add_comment_ajax(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = json.loads(request.body)
    content = data.get('content')

    if content:
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        return JsonResponse({
            'status': 'success',
            'comment': {
                'user': comment.user.username,
                'content': comment.content,
                'created_at': 'Just now'
            }
        })

    return JsonResponse({'status': 'error', 'message': 'Empty content'}, status=400)
