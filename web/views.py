import numpy as np
import pandas as pd
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from .CollaborativeFiltering import CF
from .forms import UserForm
from .models import Movie, Myrating

# ignore divide by zero or divide by NaN
np.seterr(divide='ignore', invalid='ignore')


def index(request):
    return render(request, 'web/index.html')


def statistics(request):
    num_users = User.objects.count()
    num_movies = Movie.objects.count()
    num_rated = Myrating.objects.count()
    return render(request, 'web/statistics.html',
                  {'num_users': num_users, 'num_movies': num_movies, 'num_rated': num_rated})


def evaluation(request):
    return render(request, 'web/evaluation.html')


def userRatingRecommend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    if Myrating.objects.filter(user_id=request.user.id):
        df = pd.DataFrame(list(Myrating.objects.all().values()))
        for col in df:
            if col.startswith('rating'):
                df[col] = df[col].astype(np.float_)
        df.drop('id', inplace=True, axis=1)
        current_user_id = request.user.id
        Y_data = df.to_numpy()
        rs = CF(Y_data, k=2, uuCF=1)
        rs.fit()
        recommendItems = rs.recommend(current_user_id)
        list_id = [idx for idx, val in recommendItems]
        # temp = [value for idx, value in recommendItems]
        # list_rating = []
        # # for val in temp:
        # #     rating = AverageRating(val)
        # #     list_rating.append(rating)
        #
        # print(list_rating)
        movie_list = list(Movie.objects.filter(id__in=list_id))
        list_average = []
        for id in list_id:
            average = Myrating.objects.filter(movie_id=id).aggregate(Avg('rating'))['rating__avg']
            list_average.append(average)
        items = list(zip(list_average, movie_list))
        # # items = list(zip(movie_list, temp))
        # print(items)
        return render(request, 'web/userRecommend.html', {'items': items})
    else:
        messages.warning(request, "Please rate some movies before the system makes recommendations ")
        return render(request, 'web/userRecommend.html')


def itemRatingRecommend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    if Myrating.objects.filter(user_id=request.user.id):
        df = pd.DataFrame(list(Myrating.objects.all().values()))
        print(df)
        current_user_id = request.user.id
        for col in df:
            if col.startswith('rating'):
                df[col] = df[col].astype(np.float_)
        df.drop('id', inplace=True, axis=1)
        print(df)
        Y_data = df.to_numpy()
        # uuCF=1 <=> User-user CF (1) or Item-item CF = 0
        # k is neighbors point
        rs = CF(Y_data, k=2, uuCF=0)
        rs.fit()
        recommendItems = rs.recommend(current_user_id)
        list_id = [idx for idx, val in recommendItems]
        movie_list = list(Movie.objects.filter(id__in=list_id))
        list_average = []
        for id in list_id:
            average = Myrating.objects.filter(movie_id=id).aggregate(Avg('rating'))['rating__avg']
            list_average.append(average)
        items = list(zip(list_average, movie_list))
        return render(request, 'web/itemRecommend.html', {'items': items})
    else:
        messages.warning(request, "Please rate some movies before the system makes recommendations ")
        return render(request, 'web/itemRecommend.html')


# List view
def listMovies(request):
    movies = Movie.objects.all().order_by('genre')
    page = request.GET.get('page', 1)
    query = request.GET.get('q')
    paginator = Paginator(movies, 12)
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    if query:
        movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
        list_average = []
        for member in movies:
            average = Myrating.objects.filter(movie_id=member.id).aggregate(Avg('rating'))['rating__avg']
            list_average.append(average)
        for i in range(len(list_average)):
            if list_average[i] is None:
                list_average[i] = 0
        items = list(zip(list_average, movies))
        return render(request, 'web/search.html', {'items': items})
    return render(request, 'web/list.html', {'movies': movies})


# detail view
def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    movies = get_object_or_404(Movie, id=movie_id)
    # for rating
    if request.method == "POST":
        rate = request.POST['rating']
        ratingObject = Myrating()
        ratingObject.user = request.user
        ratingObject.movie = movies
        ratingObject.rating = rate
        ratingObject.save()
        messages.success(request, "Your Rating is submited ")
        return redirect("listMovies")
    return render(request, 'web/detail.html', {'movies': movies})


# Register user
def signUp(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("listMovies")
    context = {
        'form': form
    }
    return render(request, 'web/signUp.html', context)


# Login User
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("listMovies")
            else:
                return render(request, 'web/login.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'web/login.html', {'error_message': 'Invalid Login'})
    return render(request, 'web/login.html')


# Logout user
def Logout(request):
    logout(request)
    return redirect("login")
