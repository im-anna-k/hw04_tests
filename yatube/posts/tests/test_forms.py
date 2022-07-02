from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост для тестирования',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создания поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'текст',
            'author': self.author,
            'group': self.group.id
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data, follow=True)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             self.author.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='текст',
                                            author=self.author).exists())

    def test_edit_post(self):
        """Валидная форма редактировани поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'отредактированный текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(('posts:post_edit'),
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', args=(1,)))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='отредактированный текст',
                group=self.group.id,
            ).exists()
        )
