from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.template.defaultfilters import slugify
# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.models import Note
from notes.forms import WARNING
User = get_user_model()


class TestNoteCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода, 
    # поэтому запишем его в атрибуты класса.
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        # Адрес страницы с новостью.
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.anonymous = User.objects.create(username='Аноним')
        #cls.note = Note.objects.create(title='Заголовок',
                                       #text='Текст',
                                      # author=cls.user)
        cls.url = reverse('notes:add')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {'text': cls.NOTE_TEXT,
                         'slug': 'slug',
                         'title': 'title'}

# Проверяем, НЕ может ли АНОНИМ создать запись (1) ГОТОВ
    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом записи.     
        self.client.post(self.url, data=self.form_data)
        # Считаем количество записей.
        notes_count = Note.objects.count()
        # Ожидаем, что записей в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

# Проверяем, что  АВТОРИЗОВАННЫЙ юзер МОЖЕТ создать запись (1)
    def test_user_can_create_notes(self):
        # Совершаем запрос через авторизованный клиент.
        self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к разделу с записью.
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)

# Проверяе, не дублируется ли slug (2) -- пачка
    def test_not_unique_slug3(self):
        url = reverse('notes:add')
        self.form_data['slug'] = 'slug'
        response = self.auth_client.post(url, data=self.form_data)
        # Проверяем, что в ответе есть ошибка формы для поля slug
        #self.assertFormError(response, 'form', 'slug', errors=('slug' + WARNING))  ИСПРАВИТЬ ПАЧКА
        # Проверяем, что количество заметок в базе данных осталось равным 1
        self.assertEqual(Note.objects.count(), 1)

#Если при создании заметки не заполнен slug, ГОТОВ
#  то он формируется автоматически, с помощью функции pytils.translit.slugify (3)
    def test_auto_generate_slug(self):
        url = reverse('notes:add')
        form_data = {
            'title': 'New Note',
            'slug' : 'sl',
            'text' : 'text',
        }
        form_data.pop('slug')
        response = self.auth_client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        # Создаем заметку без заполнения slug
        # Получаем ожидаемое значение slug из заголовка заметки
        expected_slug = slugify(form_data['title'])
        # Проверяем, что автоматически сгенерированный slug совпадает с ожидаемым значением
        self.assertEqual(new_note.slug, expected_slug)

# Редактирование и удаление (4)
class TestNoteEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать 
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls, 
    # поэтому их можно перечислить просто в атрибутах класса.
    COMMENT_TEXT = 'Запись'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя - автора комментария.
        cls.author = User.objects.create(username='Автор записи')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='slug', author=cls.author)
        note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_to_note = note_url
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаём объект комментария.
        # URL для редактирования записи.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления записи.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

    def test_author_can_delete_note(self):  # готово
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    

    def test_other_user_cant_delete_note(self): #готово
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что комментарий по-прежнему на месте.
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


    def test_author_can_edit_note(self):
        form_data = {
            'title': 'title',
            'text': 'text',
            'slug': 'slug',
        }
        response = self.author_client.post(self.edit_url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, form_data['title'])
        self.assertEqual(self.note.text, form_data['text'])
        self.assertEqual(self.note.slug, form_data['slug'])

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note_from_db = Note.objects.get(slug=self.note.slug)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)






