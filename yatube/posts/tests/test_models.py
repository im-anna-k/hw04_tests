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
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        exp_post_name = post.text[:15]
        self.assertEqual(exp_post_name, str(post))

        group = PostModelTest.group
        exp_group = group.title
        self.assertEqual(exp_group, str(group))

    def test_post_model_verbose_help(self):
        '''Проверяем поля verbose и help_text.'''
        post = self.post
        fields = {
            post._meta.get_field('text').verbose_name: 'Текст поста',
            post._meta.get_field('text').help_text: 'Введите текст поста'
        }
        for field, text in fields.items():
            with self.subTest():
                self.assertEqual(field, text)
