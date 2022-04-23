from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * 3,
            group=cls.group,
            pub_date='Тестовая дата',
        )

    def test_str_correct(self):
        """Проверяем, что у моделей корректно работает __str__."""

        post = PostModelTest.post
        expected_post_text = post.text[:15]

        self.assertEqual(expected_post_text, str(post))

        group = PostModelTest.group
        expected_group_title = group.title

        self.assertEqual(expected_group_title, str(group))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""

        field_verboses = {
            'author': 'автор публикации',
            'text': 'текст публикации',
            'group': 'сообщество',
            'pub_date': 'дата публикации',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""

        field_help_texts = {
            'text': 'текст нового поста',
            'group': 'группа, к которой будет относиться пост',
        }

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
