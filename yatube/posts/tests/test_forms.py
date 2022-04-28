import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostBaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )

        cls.author = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_post',
            group=cls.group,
            pub_date='test_date',
        )
        cls.url_index = '/'
        cls.url_group = f'/group/{cls.group.slug}/'
        cls.url_profile = f'/profile/{cls.author.username}/'
        cls.url_detail = f'/posts/{cls.post.pk}/'
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='noname')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()

        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class PostFormTests(PostBaseTestCase):

    def test_labels_and_help_text(self):
        """Проверка labels и help_text."""
        fields = [
            'text',
            'group',
        ]

        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    self.form.fields[field].label,
                    Post._meta.get_field(field).verbose_name.capitalize()
                )
                self.assertEqual(
                    self.form.fields[field].help_text,
                    Post._meta.get_field(field).help_text
                )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовая запись 2',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

        post = Post.objects.latest('id')
        self.assertTrue(post.text, form_data['text'])
        self.assertTrue(post.group, form_data['group'])
        self.assertTrue(post.image, 'posts/small.gif')
        self.assertTrue(post.author, self.post.author)

    def test_edit_post_author(self):
        """Валидная форма редактирует запись от имени автора."""
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='test_new_group',
            slug='test_new_group_slug',
            description='test_new_group_description',
        )
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
        form_data = {
            'text': 'Новый текст',
            'group': new_group.pk,
            'image': uploaded,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.pk}'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': f'{self.post.pk}'}))
        self.assertEqual(Post.objects.count(), posts_count)

        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertTrue(post.image, 'posts/small.gif')
        self.assertTrue(post.author, self.post.author)

    def test_edit_post_not_author(self):
        """Валидная форма не редактирует запись, если пользователь не автор."""
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='test_new_group',
            slug='test_new_group_slug',
            description='test_new_group_description',
        )
        form_data = {
            'text': 'Новый текст',
            'group': new_group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.pk}'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': f'{self.post.pk}'}))
        self.assertEqual(Post.objects.count(), posts_count)

        post = Post.objects.latest('id')
        self.assertEqual(self.post.text, 'test_post')
        self.assertEqual(self.post.group.slug, 'test_slug')
        self.assertTrue(post.author, self.post.author)

    def test_edit_post_not_authorized(self):
        """Пост не редактируется не авторизованным."""
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='test_new_group',
            slug='test_new_group_slug',
            description='test_new_group_description',
        )
        form_data = {
            'text': 'Новый текст',
            'group': new_group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.pk}'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/posts/1/edit/')
        self.assertEqual(Post.objects.count(), posts_count)

        post = Post.objects.latest('id')
        self.assertTrue(post.author, self.post.author)

    def test_comment_post_authorized(self):
        """Пост комментируется авторизованным."""
        post = self.post
        form_data = {
            'text': 'Текстовый комментарий',
            post: post,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': f'{self.post.pk}'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': f'{self.post.pk}'}))

        comment = Comment.objects.latest('id')
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(Comment.objects.count(), 1)

    def test_comment_post_not_authorized(self):
        """Пост комментируется не авторизованным."""
        post = self.post
        form_data = {
            'text': 'Текстовый комментарий',
            post: post,
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': f'{self.post.pk}'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(Comment.objects.count(), 0)
