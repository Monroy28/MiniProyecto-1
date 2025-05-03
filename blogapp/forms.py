from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '★' * i) for i in range(1, 6)]),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.blog = kwargs.pop('blog')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if Review.objects.filter(blog=self.blog, reviewer=self.user).exists():
            raise forms.ValidationError("You have already submitted a review for this blog.")
        return cleaned_data