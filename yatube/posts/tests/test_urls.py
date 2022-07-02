from django.test import TestCase, Client
from posts.models import Post, Group, User
from http import HTTPStatus


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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_guest(self):
        """Страница доступна гостю."""
        addresses = [
            '/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.id}/'
        ]
        for address in addresses:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_create_auth(self):
        """Страница доступна авторизованному пользователю."""
        responses = {
            self.authorized_client.get('/create/'),
            self.authorized_client.get(f'/posts/{self.post.id}/edit/')}
        for response in responses:
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_404(self):
        """404, если несуществующая страница."""
        response = self.authorized_client.get('/smth/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
