from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Здесь вы можете написать текст своего поста ;)'
        )
        self.fields['group'].empty_label = (
            'А здесь можно выбрать группу :)'
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
