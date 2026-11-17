from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from .forms import MovieForm, CommentForm, VipBookingForm
from .models import Genre, Movie, VipBooking


# ---------------- РЕГИСТРАЦИЯ И ВХОД (стандартные формы Django) ----------------

class RegisterView(generic.CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Регистрация прошла успешно! Теперь войдите.")
        return super().form_valid(form)


class AuthLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class AuthLogoutView(LogoutView):
    next_page = reverse_lazy('movie_list')


# ---------------- LIST / SEARCH / ФИЛЬТР ПО ЖАНРУ ----------------

class MovieListView(generic.ListView):
    template_name = 'CineBoard/movie_list.html'
    context_object_name = 'movies'
    model = Movie
    paginate_by = 6

    def get_queryset(self):
        return self.model.objects.prefetch_related('genres').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context


class MovieSearchView(MovieListView):
    """Поиск по названию: /search/?q=..."""

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        movies = super().get_queryset()
        if query:
            # SQLite не различает регистр только у латиницы,
            # поэтому для кириллицы проверяем несколько вариантов написания
            condition = Q()
            for variant in {query, query.lower(), query.upper(), query.capitalize(), query.title()}:
                condition |= Q(title__icontains=variant)
            movies = movies.filter(condition)
        return movies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class GenreMovieListView(MovieListView):
    """Фильтр по жанру (многие ко многим): /genre/<id>/"""

    def get_queryset(self):
        self.genre = get_object_or_404(Genre, id=self.kwargs['genre_id'])
        return self.genre.movies.prefetch_related('genres').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_genre'] = self.genre
        return context


# ---------------- DETAIL (+ комментарии и VIP-бронь) ----------------

class MovieDetailView(generic.DetailView):
    template_name = 'CineBoard/movie_detail.html'
    context_object_name = 'movie'
    model = Movie
    pk_url_kwarg = 'movie_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.object
        user = self.request.user
        context['comments'] = movie.comments.select_related('author')
        context['comment_form'] = CommentForm()
        context['vip_bookings'] = movie.vip_bookings.select_related('user')
        context['vip_form'] = VipBookingForm(movie=movie)
        context['my_booking'] = VipBooking.objects.filter(user=user).first() if user.is_authenticated else None
        return context


# ---------------- CRUD фильмов ----------------

class MovieCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'CineBoard/movie_form.html'
    form_class = MovieForm
    extra_context = {'title': 'Добавить фильм'}

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movie_id': self.object.id})


class MovieUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'CineBoard/movie_form.html'
    form_class = MovieForm
    model = Movie
    pk_url_kwarg = 'movie_id'
    extra_context = {'title': 'Редактировать фильм'}

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movie_id': self.object.id})


class MovieDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'CineBoard/movie_confirm_delete.html'
    context_object_name = 'movie'
    model = Movie
    pk_url_kwarg = 'movie_id'
    success_url = reverse_lazy('movie_list')


# ---------------- КОММЕНТАРИИ (1 ко многим, только авторизованные) ----------------

class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = CommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        form.instance.movie = get_object_or_404(Movie, id=self.kwargs['movie_id'])
        form.instance.author = self.request.user
        messages.success(self.request, "Комментарий добавлен.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Комментарий не может быть пустым.")
        return redirect('movie_detail', movie_id=self.kwargs['movie_id'])

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movie_id': self.kwargs['movie_id']}) + '#comments'


# ---------------- VIP-БРОНЬ (1 к 1: один человек — одно место) ----------------

class VipBookingCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = VipBookingForm
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        self.movie = get_object_or_404(Movie, id=kwargs['movie_id'])
        if request.user.is_authenticated and VipBooking.objects.filter(user=request.user).exists():
            messages.error(request, "У вас уже есть VIP-место. Сначала отмените старую бронь.")
            return redirect('movie_detail', movie_id=self.movie.id)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['movie'] = self.movie
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.movie = self.movie
        messages.success(self.request, f"Вы забронировали место {form.instance.seat}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Это место уже занято, выберите другое.")
        return redirect('movie_detail', movie_id=self.movie.id)

    def get_success_url(self):
        return reverse('movie_detail', kwargs={'movie_id': self.movie.id}) + '#vip'


class VipBookingCancelView(LoginRequiredMixin, generic.DeleteView):
    http_method_names = ['post']

    def get_object(self, queryset=None):
        return get_object_or_404(VipBooking, user=self.request.user)

    def get_success_url(self):
        messages.info(self.request, "Бронь отменена.")
        return reverse('movie_detail', kwargs={'movie_id': self.object.movie_id}) + '#vip'


class MyBookingView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'CineBoard/my_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = VipBooking.objects.select_related('movie').filter(user=self.request.user).first()
        return context
