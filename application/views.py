import random
import json
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from .models import Movie, NewMovieNotification, WatchlistItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserForm


def index(request):
    return render(request, 'index.html', {
        'enable_simple_search': True,
    })


def watch(request, mid):
    try:
        ctx = {
            'movie': get_object_or_404(Movie, pk=mid),
        }
    except MultipleObjectsReturned:
        ctx = {
            'movie': Movie.objects.filter(pk=mid).first(),
        }
    return render(request, 'watch.html', ctx)


@login_required
def profile(request):
    if request.method == "POST":
        userform = UserForm(request.POST, instance=request.user)
        passwordform = PasswordChangeForm(request.user, request.POST)

        error = False
        if userform.has_changed() and userform.is_valid():
            userform.save()
        elif not userform.has_changed():
            userform = UserForm(instance=request.user)
        else:
            error = True

        if passwordform.has_changed() and passwordform.is_valid():
            passwordform.save()
        elif not passwordform.has_changed():
            passwordform = PasswordChangeForm(user=request.user)
        else:
            error = True

        if not error:
            redirect('login')

    else:
        userform = UserForm(instance=request.user)
        passwordform = PasswordChangeForm(user=request.user)

    ctx = {
        'userform': userform,
        'passwordform': passwordform,
    }
    return render(request, 'profile.html', ctx)

@login_required
def new_movies(request):
    ctx = {
        'unread_notifications': [],
        'read_notifications': [],
    }

    with transaction.atomic():
        for notification in NewMovieNotification.objects.filter(user=request.user, read=False):
            ctx['unread_notifications'].append(notification.movie)
            notification.read = True
            notification.save()
        for notification in NewMovieNotification.objects.filter(user=request.user, read=True)[:10]:
            ctx['read_notifications'].append(notification.movie)

    return render(request, 'new_movies.html', ctx)


def random_movie(request):
    movies = list(Movie.objects.all())
    try:
        choice = random.choice(movies)
        return redirect('watch', mid=choice.pk)
    except IndexError:
        return render(request, 'random.html')


@login_required
def watchlist(request):
    ctx = {
        'watchlist': [wli.movie for wli in WatchlistItem.objects.filter(user=request.user)]
    }
    return render(request, 'watchlist.html', ctx)


@login_required
def watchlist_add(request):
    json_data = json.loads(request.read().decode())
    try:
        movie = Movie.objects.get(pk=json_data['movie'])
        WatchlistItem.objects.create(user=request.user, movie=movie)
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie does not exists'})

    return JsonResponse({})

@login_required
def watchlist_remove(request):
    json_data = json.loads(request.data.read())
    WatchlistItem.filter(user=request.user, pk=json_data['id']).delete()
    return JsonResponse({})


@login_required
def watchlist_list(request):
    return JsonResponse({
        'movies': list(WatchlistItem.objects.filter(user=request.user))
    })
