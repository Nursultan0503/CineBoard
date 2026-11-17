from django.urls import path
from . import views

urlpatterns = [
    # фильмы
    path('', views.MovieListView.as_view(), name='movie_list'),
    path('search/', views.MovieSearchView.as_view(), name='movie_search'),
    path('genre/<int:genre_id>/', views.GenreMovieListView.as_view(), name='genre_movies'),
    path('movie/create/', views.MovieCreateView.as_view(), name='movie_create'),
    path('movie/<int:movie_id>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movie/<int:movie_id>/update/', views.MovieUpdateView.as_view(), name='movie_update'),
    path('movie/<int:movie_id>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),

    # комментарии и VIP-бронь
    path('movie/<int:movie_id>/comment/', views.CommentCreateView.as_view(), name='comment_create'),
    path('movie/<int:movie_id>/vip/', views.VipBookingCreateView.as_view(), name='vip_book'),
    path('vip/cancel/', views.VipBookingCancelView.as_view(), name='vip_cancel'),
    path('my-booking/', views.MyBookingView.as_view(), name='my_booking'),

    # пользователи
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.AuthLoginView.as_view(), name='login'),
    path('logout/', views.AuthLogoutView.as_view(), name='logout'),
]
