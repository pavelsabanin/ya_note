from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from django.http import Http404

from notes.models import Note

from django.contrib.auth import get_user_model

# Получаем модель пользователя.
User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # 3 пользователя, один автор, другой якобы просто пользователь,и аноним
        cls.author = User.objects.create(username='Автор')

        cls.reader = User.objects.create(username='Читатель')
        cls.user = User.objects.create(username='testUser') # аноним
        #cls.user_client = Client() # обычный клиент, аноним

        # Создаю от лица автора заметку.
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)
 # Тест на получение главной страницы, отдельной записи, и на страницы логина,
 # логаута и регистрации пользователей



# Страницы доступны АНОНИМНОМУ пользователю. (1 и 6 пункты)
    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


# Страница редактирования,удаления и отдельной записи доступна только автору. (3 пункт)
    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
        # Логиним пользователя в клиенте:
            self.client.force_login(user)   # здесь логиним автора из self.author
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

# Проверяем доступность отдельной записи для автора (3 пункт )
    def test_detail_note_for_author(self):
        url = reverse('notes:detail', args=(self.note.slug,))
        #Логиним пользователя
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

# Проверяем доступность отдельной записи для анонима (3 пункт )
    def test_detail_note_for_not_the_author(self):
        url = reverse('notes:detail', args=(self.note.slug,))
        self.client.force_login(self.reader)   #проверяем с авторизованным
        response = self.client.get(url) 
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.client.get(url)  #проверяем с анонимом
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

# Проверяем может ли авторизованный пользователь зайти на данные страницы (2)
    def test_pages_availability_for_authorized(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        self.client.force_login(self.reader)
        for name, args in urls:
            with self.subTest(user=self.reader, name=name):
                url = reverse(name, args=args,)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

# Проверяем, перенаправит ли анонима с данных страниц на страницу логина (4)
    def test_pages_availability_for_authorized_login(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
