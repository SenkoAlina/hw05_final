from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.following = User.objects.create_user(username='following')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_post',
            group=cls.group,
        )
        cls.url_index = '/'
        cls.url_group = f'/group/{cls.group.slug}/'
        cls.url_profile = f'/profile/{cls.author.username}/'
        cls.url_detail = f'/posts/{cls.post.pk}/'
        cls.url_unexisting = '/unexisting_page/'
        cls.url_create = '/create/'
        cls.url_edit = f'/posts/{cls.post.pk}/edit/'
        cls.url_follow_index = '/follow/'
        cls.url_follow = f'/profile/{cls.following.username}/follow/'
        cls.url_unfollow = f'/profile/{cls.following.username}/unfollow/'

    def setUp(self) -> None:
        self.guest_client = Client()

        self.user = User.objects.create_user(username='Noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_urls_for_guest_client(self):
        """Statuscode страниц для не авторизованного пользователя."""
        urls = {
            self.url_index: HTTPStatus.OK,
            self.url_group: HTTPStatus.OK,
            self.url_profile: HTTPStatus.OK,
            self.url_detail: HTTPStatus.OK,
            self.url_unexisting: HTTPStatus.NOT_FOUND,
            self.url_create: HTTPStatus.FOUND,
            self.url_edit: HTTPStatus.FOUND,
            self.url_follow_index: HTTPStatus.FOUND,
            self.url_follow: HTTPStatus.FOUND,
            self.url_unfollow: HTTPStatus.FOUND,
        }
        for url, status in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_for_authorized_client(self):
        """Statuscode страниц для авторизованного пользователя."""
        urls = {
            self.url_create: HTTPStatus.OK,
            self.url_edit: HTTPStatus.FOUND,
            self.url_follow_index: HTTPStatus.OK,
            self.url_follow: HTTPStatus.FOUND,
            self.url_unfollow: HTTPStatus.FOUND,
        }
        for url, status in urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_for_author(self):
        """Страница /edit/ доступна автору."""
        response = self.author_client.get(self.url_edit)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_detail: 'posts/post_detail.html',
            self.url_create: 'posts/create_post.html',
            self.url_edit: 'posts/create_post.html',
            self.url_unexisting: 'core/404.html',
            self.url_follow_index: 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_cache_index_page(self):
        """Проверка работы cache на главной странице"""
        response_before_cache = self.guest_client.get(self.url_index).content
        self.post.delete()
        response_after_cache = self.guest_client.get(self.url_index).content
        self.assertEqual(response_before_cache, response_after_cache)

        cache.clear()
        response_after_clear_cache = self.guest_client.get(
            self.url_index).content
        self.assertNotEqual(response_before_cache, response_after_clear_cache)
