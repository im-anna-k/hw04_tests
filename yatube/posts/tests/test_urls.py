from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
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
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_main(self):
        """Страница доступна гостю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_urls_group(self):
        """Страница доступна гостю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_urls_detail(self):
        """Страница доступна гостю."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_urls_create_auth(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_urls_edit_auth(self):
        """Редактирование поста доступно только автору поста."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_urls_404(self):
        """404, если несуществующая страница."""
        response = self.authorized_client.get('/smth/')
        self.assertEqual(response.status_code, 404)
