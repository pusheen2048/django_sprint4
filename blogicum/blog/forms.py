from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from blog.models import Post, Comment


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'is_published', 'location', 'category', 'image')
        widgets = {'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )


class UserUpdateForm(ModelForm):
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Этот адрес электронной почты уже используется')
        return email
