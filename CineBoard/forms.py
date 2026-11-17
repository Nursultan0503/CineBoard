from django import forms
from .models import Movie, Comment, VipBooking


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'poster', 'director', 'year', 'duration', 'country', 'genres']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'genres': forms.CheckboxSelectMultiple(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш комментарий...'})}
        labels = {'text': ''}


class VipBookingForm(forms.ModelForm):
    class Meta:
        model = VipBooking
        fields = ['seat']

    def __init__(self, *args, movie=None, **kwargs):
        super().__init__(*args, **kwargs)
        # показываем только свободные места на этот фильм
        taken = set(VipBooking.objects.filter(movie=movie).values_list('seat', flat=True))
        self.fields['seat'].choices = [s for s in VipBooking.SEATS if s[0] not in taken]
