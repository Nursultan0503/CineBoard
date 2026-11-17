from django.contrib import admin
from .models import Genre, Movie, Comment, VipBooking


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'year', 'country', 'created_at')
    list_filter = ('genres', 'year')
    search_fields = ('title', 'director')
    filter_horizontal = ('genres',)
    inlines = [CommentInline]


admin.site.register(Genre)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'movie', 'created_at')


@admin.register(VipBooking)
class VipBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'seat', 'created_at')
