"""blog 앱 서버 측 테스트 (Django TestCase / DRF APITestCase — 모두 unittest.TestCase 기반)

실행: python manage.py test blog -v 2
"""
import io
import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp()
POSTS_URL = '/api_root/Post/'


def make_image(name='test.jpg'):
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, 'JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class TempMediaMixin:
    """업로드한 테스트 이미지가 실제 media/ 폴더에 쌓이지 않게 임시 폴더를 쓴다"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostApiTest(TempMediaMixin, APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('sunwoo', password='pw-12345!')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.post = Post.objects.create(author=self.user, title='기존 글', text='본문',
                                        published_date=timezone.now())

    def upload(self, **overrides):
        data = {'author': self.user.id, 'title': '새 글', 'text': '본문', 'image': make_image()}
        data.update(overrides)
        return self.client.post(POSTS_URL, data, format='multipart')

    def test_get_posts_with_token_returns_json_array(self):
        response = self.client.get(POSTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)

    def test_post_fields_include_id_and_absolute_image_url(self):
        post = self.client.get(POSTS_URL).json()[0]
        self.assertEqual(list(post), ['id', 'author', 'title', 'text', 'created_date',
                                      'published_date', 'image'])
        self.assertTrue(post['image'].startswith('http://testserver/media/'))

    def test_multipart_post_creates_post_with_image(self):
        response = self.upload(title='한글 제목')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.json()['title'], '한글 제목')
        self.assertIn('/media/images/', response.json()['image'])

    def test_published_date_is_filled_when_not_given(self):
        before = timezone.now()
        response = self.upload()
        created = Post.objects.get(pk=response.json()['id'])
        self.assertIsNotNone(created.published_date)
        self.assertGreaterEqual(created.published_date, before)

    def test_published_date_is_kept_when_given(self):
        given = timezone.now() - timedelta(days=3)
        response = self.upload(published_date=given.isoformat())
        created = Post.objects.get(pk=response.json()['id'])
        self.assertEqual(created.published_date, given)

    def test_request_without_token_is_rejected_with_401(self):
        self.client.credentials()
        response = self.client.get(POSTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response['WWW-Authenticate'], 'Token')

    def test_request_with_wrong_token_is_rejected_with_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token wrong')
        self.assertEqual(self.client.get(POSTS_URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_without_required_fields_is_rejected_with_400(self):
        response = self.client.post(POSTS_URL, {'text': '제목 없음'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.json())
        self.assertIn('author', response.json())
        self.assertEqual(Post.objects.count(), 1)

    def test_get_single_post_by_id(self):
        response = self.client.get(f'{POSTS_URL}{self.post.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], '기존 글')

    def test_delete_post_returns_204_and_removes_post(self):
        response = self.client.delete(f'{POSTS_URL}{self.post.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_post_uploaded_by_api_appears_in_web_post_list(self):
        self.upload(title='API로 올린 글')
        self.assertContains(self.client.get(reverse('post_list')), 'API로 올린 글')

    def test_allow_header_contains_get_and_post(self):
        allow = self.client.get(POSTS_URL)['Allow']
        self.assertIn('GET', allow)
        self.assertIn('POST', allow)


class TokenAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('sunwoo', password='pw-12345!')

    def test_token_is_issued_with_correct_password(self):
        response = self.client.post('/api-token-auth/', {'username': 'sunwoo', 'password': 'pw-12345!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['token'], Token.objects.get(user=self.user).key)

    def test_token_is_not_issued_with_wrong_password(self):
        response = self.client.post('/api-token-auth/', {'username': 'sunwoo', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Token.objects.exists())

    def test_issued_token_can_read_post_list(self):
        token = self.client.post('/api-token-auth/', {'username': 'sunwoo', 'password': 'pw-12345!'}).json()['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(self.client.get(POSTS_URL).status_code, status.HTTP_200_OK)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class WebViewTest(TempMediaMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sunwoo', password='pw-12345!')

    def login(self):
        self.client.login(username='sunwoo', password='pw-12345!')

    def test_post_list_shows_only_published_posts(self):
        Post.objects.create(author=self.user, title='공개 글', text='t', published_date=timezone.now())
        Post.objects.create(author=self.user, title='임시 글', text='t')
        Post.objects.create(author=self.user, title='예약 글', text='t',
                            published_date=timezone.now() + timedelta(days=1))
        response = self.client.get(reverse('post_list'))
        self.assertContains(response, '공개 글')
        self.assertNotContains(response, '임시 글')
        self.assertNotContains(response, '예약 글')

    def test_post_detail_shows_title_and_image(self):
        post = Post.objects.create(author=self.user, title='상세 글', text='t', image=make_image())
        response = self.client.get(reverse('post_detail', args=[post.pk]))
        self.assertContains(response, '상세 글')
        self.assertContains(response, post.image.url)

    def test_post_detail_of_missing_post_returns_404(self):
        self.assertEqual(self.client.get(reverse('post_detail', args=[999])).status_code, 404)

    def test_anonymous_user_is_redirected_to_login_for_new_and_edit(self):
        post = Post.objects.create(author=self.user, title='t', text='t')
        for url in [reverse('post_new'), reverse('post_edit', args=[post.pk])]:
            response = self.client.get(url)
            self.assertRedirects(response, f'/api-auth/login/?next={url}', fetch_redirect_response=False)

    def test_new_post_form_is_shown_with_image_field(self):
        self.login()
        response = self.client.get(reverse('post_new'))
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'name="image"')

    def test_new_post_with_image_is_saved_and_published(self):
        self.login()
        response = self.client.post(reverse('post_new'), {'title': '웹 글', 'text': 't', 'image': make_image()})
        post = Post.objects.get(title='웹 글')
        self.assertRedirects(response, reverse('post_detail', args=[post.pk]))
        self.assertEqual(post.author, self.user)
        self.assertIsNotNone(post.published_date)
        self.assertTrue(post.image.name.startswith('images/'))

    def test_new_post_without_image_uses_default_image(self):
        self.login()
        self.client.post(reverse('post_new'), {'title': '이미지 없음', 'text': 't'})
        self.assertEqual(Post.objects.get(title='이미지 없음').image.name, 'images/default_error.png')

    def test_new_post_without_title_is_not_saved(self):
        self.login()
        response = self.client.post(reverse('post_new'), {'title': '', 'text': 't'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.exists())

    def test_edit_form_is_prefilled(self):
        self.login()
        post = Post.objects.create(author=self.user, title='원래 제목', text='t')
        self.assertContains(self.client.get(reverse('post_edit', args=[post.pk])), '원래 제목')

    def test_edit_without_new_image_keeps_existing_image(self):
        self.login()
        post = Post.objects.create(author=self.user, title='원래 제목', text='t', image=make_image())
        old_image = post.image.name
        self.client.post(reverse('post_edit', args=[post.pk]), {'title': '바뀐 제목', 'text': 't'})
        post.refresh_from_db()
        self.assertEqual(post.title, '바뀐 제목')
        self.assertEqual(post.image.name, old_image)

    def test_js_test_page_is_rendered(self):
        self.assertContains(self.client.get(reverse('js_test')), 'Number guessing game')


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sunwoo', password='pw-12345!')
        self.post = Post.objects.create(author=self.user, title='모델 글', text='t')

    def test_str_returns_title(self):
        self.assertEqual(str(self.post), '모델 글')

    def test_publish_sets_published_date(self):
        self.assertIsNone(self.post.published_date)
        self.post.publish()
        self.post.refresh_from_db()
        self.assertIsNotNone(self.post.published_date)

    def test_default_image_is_default_error_png(self):
        self.assertEqual(self.post.image.name, 'images/default_error.png')
