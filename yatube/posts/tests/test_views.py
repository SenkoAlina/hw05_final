import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User
from yatube.settings import POSTS_PER_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POSTS_COUNT = 17
POSTS_COUNT_ON_SECOND_PAGE = POSTS_COUNT - POSTS_PER_PAGE


class ViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.user = User.objects.create_user(username='auth')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_post',
            group=cls.group,
            pub_date='test_date',
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='test_comment')
        cls.follower = User.objects.create_user(username='follower')
        cls.url_index = reverse('posts:index')
        cls.url_group = reverse('posts:group_list', kwargs={
            'slug': f'{cls.group.slug}'})
        cls.url_profile = reverse('posts:profile', kwargs={
            'username': f'{cls.user.username}'})
        cls.url_detail = reverse('posts:post_detail', kwargs={
            'post_id': f'{cls.post.pk}'})
        cls.url_create = reverse('posts:post_create')
        cls.url_edit = reverse('posts:post_edit', kwargs={
            'post_id': f'{cls.post.pk}'})
        cls.url_follow_index = reverse('posts:follow_index')
        cls.url_follow = reverse('posts:profile_follow', kwargs={
            'username': f'{cls.user.username}'})
        cls.url_unfollow = reverse('posts:profile_unfollow', kwargs={
            'username': f'{cls.user.username}'})

    def setUp(self) -> None:

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_paginator_correct(self):

        posts_list = []
        for x in range(1, POSTS_COUNT):
            posts_list.append(
                Post(text=f'text{x}', author=self.user, group=self.group))

        Post.objects.bulk_create(posts_list)

        urls = [
            self.url_index,
            self.url_group,
            self.url_profile,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                page_obj = response.context.get('page_obj')

                self.assertEqual(len(page_obj), POSTS_PER_PAGE)

                response_second = self.guest_client.get(url + '?page=2')
                page_obj_second = response_second.context.get('page_obj')

                self.assertEqual(len(page_obj_second),
                                 POSTS_COUNT_ON_SECOND_PAGE)

    def test_templates(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_page_names = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_detail: 'posts/post_detail.html',
            self.url_create: 'posts/create_post.html',
            self.url_edit: 'posts/create_post.html',
            self.url_follow_index: 'posts/follow.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post(self, post):
        context_objects = {
            self.post.author.id: post.author.id,
            self.post.text: post.text,
            self.post.pub_date: post.pub_date,
            self.post.group.title: post.group.title,
            self.post.group.slug: post.group.slug,
            self.post.id: post.id,
            self.post.image: post.image
        }

        for expected_value, field in context_objects.items():
            with self.subTest(field=field):
                self.assertEqual(expected_value, field)

    def test_index_page_obj_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.authorized_client.get(self.url_index)

        first_object = response.context['page_obj'][0]
        self.check_post(first_object)

    def test_group_list_group_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""

        response = self.authorized_client.get(self.url_group)

        first_object = response.context['page_obj'][0]
        self.check_post(first_object)

        title = response.context.get('group').title
        description = response.context.get('group').description

        self.assertEqual(title, self.group.title)
        self.assertEqual(description, self.group.description)

    def test_group_has_not_wrong_post(self):
        """В группу не попадает пост, не принадлежащий этой группе."""

        group = Group.objects.create(
            title='test_group_2',
            slug='test_slug_2',
            description='test_description_2',
        )
        url = reverse('posts:group_list', kwargs={
            'slug': f'{group.slug}'})

        response = self.authorized_client.get(url)

        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.authorized_client.get(self.url_profile)

        first_object = response.context['page_obj'][0]
        self.check_post(first_object)

        author = response.context.get('author')

        self.assertEqual(author, self.post.author)

    def test_detail_post_correct_context(self):
        """Шаблон detail сформирован с правильным контекстом 'post'."""

        response = self.authorized_client.get(self.url_detail)
        post = response.context.get('post')

        self.check_post(post)

        comment = response.context.get('comments').last()
        self.assertEqual(comment, self.comment)

    def test_create_form_correct_context(self):
        """Шаблон create сформирован с правильным контекстом 'form'."""

        response = self.authorized_client.get(self.url_create)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        form = response.context.get('form')

        self.assertIsInstance(form, PostForm)

    def test_edit_form_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом 'form'."""

        response = self.authorized_client.get(self.url_edit)

        form = response.context.get('form')

        self.assertIsInstance(form, PostForm)
        self.assertEqual(form.instance, self.post)

        is_edit = response.context.get('is_edit')

        self.assertIsInstance(is_edit, bool)
        self.assertEqual(is_edit, True)

    def test_follow_index_context_for_follower(self):

        Follow.objects.create(
            user=self.follower,
            author=self.user
        )
        response = self.follower_client.get(self.url_follow_index)
        first_object = response.context['page_obj'][0]

        self.check_post(first_object)

    def test_follow_index_context_for_not_follower(self):

        not_follower = User.objects.create_user(username='not_follower')
        not_follower_client = Client()
        not_follower_client.force_login(not_follower)

        response = not_follower_client.get(self.url_follow_index)

        self.assertEqual(len(response.context['page_obj']), 0)

    def test_follow(self):

        self.follower_client.get(self.url_follow)

        follow = Follow.objects.filter(
            user=self.follower,
            author=self.user
        )
        self.assertTrue(follow.exists())

    def test_unfollow(self):

        Follow.objects.create(
            user=self.follower,
            author=self.user
        )
        self.follower_client.get(self.url_unfollow)

        follow = Follow.objects.filter(
            user=self.follower,
            author=self.user
        )
        self.assertFalse(follow.exists())
