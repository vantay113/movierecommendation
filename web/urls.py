from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/', views.detail, name='detail'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('listMovies/', views.listMovies, name='listMovies'),
    path('userRecommend/', views.userRatingRecommend, name='userRatingRecommend'),
    path('itemRecommend/', views.itemRatingRecommend, name='itemRatingRecommend'),
    path('statistics/', views.statistics, name='statistics'),
    path('evaluation/', views.evaluation, name='evaluation'),
]
