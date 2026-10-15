"""포토 블로그 REST API 검증 엔진 (TDD 빨강 단계: 인터페이스만 정의)"""
import collections

POSTS_PATH = '/api_root/Post/'
TOKEN_PATH = '/api-token-auth/'
REQUIRED_POST_KEYS = ('author', 'title', 'text', 'created_date', 'published_date', 'image')

StepResult = collections.namedtuple('StepResult', 'name passed detail')


class ApiError(Exception):
    """API가 기대한 상태코드로 응답하지 않았을 때 발생. status는 HTTP 상태코드(연결 실패 시 None)"""

    def __init__(self, status, message=''):
        super().__init__(f'HTTP {status}: {message}')
        self.status = status
        self.message = message


def minimal_png():
    pass


def encode_multipart(fields, files, boundary=None):
    pass


class PhotoBlogApi:
    def __init__(self, base_url, token=None, timeout=10):
        pass

    def get_token(self, username, password):
        pass

    def get_posts(self):
        pass

    def create_post(self, title, text, image_path, author=None, published_date=None):
        pass

    def delete_post(self, post_id):
        pass

    def validate_post(self, post):
        pass

    def validate_post_list(self, posts):
        pass

    def run_scenario(self, username, password, image_path=None, author=None):
        pass


def format_results(results):
    pass


def main(argv=None):
    pass
