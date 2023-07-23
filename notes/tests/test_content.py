from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from django.http import Http404

from notes.models import Note

from django.contrib.auth import get_user_model

from notes.views import NoteCreate, NoteUpdate

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        #cls.user1 = User.objects.create_user(username='user1', password='password1')
        #cls.user2 = User.objects.create(username='user2', password='password2')
        #cls.note1 = Note.objects.create(author=cls.user1, title='Note1')
        #cls.note2 = Note.objects.create(author=cls.user2, title='Note2')
        #cls.user_client = Client()
        #cls.user_client.force_login(cls.user)

        #cls.author = User.objects.create(username='Автор')
        #cls.reader = User.objects.create(username='Читатель')
        #cls.note = Note.objects.create(title='Заголовок',
                                      # text='Текст',
                                      # author=cls.author)
        #новое 
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.user)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)


# 2 . в список заметок одного пользователя не попадают заметки другого пользователя

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        response = self.reader_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.note, response.context['object_list'])

# 1 отдельная заметка передаётся на страницу со списком заметок в списке object_list, в словаре context;
    def test_note_list_view(self):  # ГОТОВО
        url = reverse('notes:list')
        response = self.auth_client.get(url)
        # Проверяем, что ответ имеет статус 200 (успешный запрос)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, что заметка передается в список object_list в контексте
        self.assertIn(self.note, response.context['object_list'])

# создание
    def test_create_note_page_contains_form(self):
        url = reverse('notes:add')
        response = self.auth_client.get(url)
        #self.assertIsInstance(response.context['form'], NoteCreate.form_class)
        self.assertIn('form', response.context)

# 3 редактирование
    #def test_note_update_view(self):
        #self.update_url = reverse('notes:form', args=[1])
        # Аутентифицируем пользователя
       #self.client.login(username='user1', password='password1')
        # Получаем ответ от страницы редактирования заметки
        #response = self.client.get(self.update_url)
        # Проверяем, что ответ имеет статус 200 (успешный запрос)
       # self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, что на страницу передана форма
        #self.assertIsInstance(response.context['form'], NoteUpdate.form_class)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args=(self.note.slug,))
    # Запрашиваем страницу редактирования заметки:
        response = self.auth_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
        #assert 'form' in response.context 
        self.assertIn('form', response.context)
