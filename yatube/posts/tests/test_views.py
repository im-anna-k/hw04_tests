from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='usname')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.post.author.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                if template != '/posts/1/edit/':
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Тест контекста для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_group_show_correct_context(self):
        """Тест контекста для group_list."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_profile_show_correct_context(self):
        """Тест контекста для profile."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username':
                                                      self.post.author.username
                                                      }))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)

    def test_detail_show_correct_context(self):
        """Тест контекста для detail."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      self.post.id}))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_total_0 = first_object.author.posts.count()
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_total_0, self.post.author.posts.count())

    def test_create_show_correct_context(self):
        """Тест контекста для create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Тест контекста для edit."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                              kwargs={'post_id':
                                                      self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertEqual(response.context['is_edit'], True)
