from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Класс Group описывает модель для хранения информации о группе"""

    title = models.CharField(
        verbose_name='название сообщества',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='слаг',
        max_length=50,
        unique=True
    )
    description = models.TextField(verbose_name='описание сообщества')

    class Meta:
        verbose_name = 'сообщество'
        verbose_name_plural = 'сообщества'

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    """Класс Post описывает модель для хранения информации о посте"""

    text = models.TextField(
        verbose_name='текст публикации',
        help_text='текст нового поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор публикации',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='сообщество',
        help_text='группа, к которой будет относиться пост',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:15]}'


class Comment(models.Model):
    """Класс Comment описывает модель для хранения информации о комментариях"""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='оставьте свой комментарий'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Класс Follow описывает модель для хранения информации о подписках"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        ordering = ('author',)
