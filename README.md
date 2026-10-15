# PhotoBlog

모바일/웹서비스 프로젝트 공통평가 01 — Chapter 05. 모바일 앱으로 사용하는 기본 포토 블로그

- **Server**: Django + Django REST Framework 포토 블로그 (게시물 = 제목/본문/이미지) — [kiokahn/web_blog](https://github.com/kiokahn/web_blog) 기반
- **Client**: Android(Java) 앱 — 서버 게시물 이미지를 동기화해 RecyclerView로 표시하고, 새 게시물을 업로드

## 폴더 구조

```
ROOT/
├── PhotoBlogServer/            # Django 서버 (manage.py 위치)
│   ├── mysite/  blog/  media/images/default_error.png
│   ├── requirements.txt        # + requirements-dev.txt (coverage)
│   ├── socket_server/          # 요청 메시지 검증용 소켓 서버
│   └── api_test_engine/        # API 검증 엔진 + unittest 자동 테스트
├── PhotoViewer/                # Android Studio 프로젝트 (package: com.example.imageviewdemo)
├── 모바일/웹서비스 프로젝트 공통평가 01_수행 결과 보고서.docx
├── .gitignore
└── README.md
```

## 서버 실행 (로컬)

Python **3.12 이상** 필요 (Django 6.1). 모든 명령은 `PhotoBlogServer/`에서 실행한다.

```powershell
cd PhotoBlogServer

# 1. 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate          # macOS / Linux

# 2. 라이브러리 설치
pip install -r requirements.txt

# 3. DB 마이그레이션
python manage.py migrate

# 4. 관리자 계정 생성
python manage.py createsuperuser

# 5. 앱/telnet에서 사용할 토큰 생성 (아래 "토큰 생성" 참고)
python manage.py drf_create_token <username>

# 6. 서버 실행 (에뮬레이터에서 접속하려면 0.0.0.0으로 실행)
python manage.py runserver 0.0.0.0:8000
```

> PowerShell에서 `Activate.ps1` 실행이 막히면: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

| 주소 | 설명 |
|---|---|
| http://127.0.0.1:8000/ | 웹 블로그 목록 (로그인 시 우상단 `+`로 글쓰기, 이미지 첨부 가능) |
| http://127.0.0.1:8000/admin/ | 관리자 |
| http://127.0.0.1:8000/api_root/ | DRF API Root |
| http://127.0.0.1:8000/api_root/Post/ | 게시물 목록(GET) / 작성(POST) |
| http://127.0.0.1:8000/api-auth/login/ | 브라우저블 API 로그인 (우상단 "Log in"과 동일) |
| http://127.0.0.1:8000/api-token-auth/ | 아이디/비밀번호 → 토큰 발급(POST) |

안드로이드 에뮬레이터에서는 `127.0.0.1` 대신 `10.0.2.2`로 접속한다.

## API

모든 API는 **인증 필요**. 인증 없이 요청하면 `401 Unauthorized`.

- 앱/telnet: 헤더 `Authorization: Token <TOKEN>`
- 브라우저: `/api-auth/login/`에서 로그인(세션)

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api_root/Post/` | 게시물 목록 (JSON 배열, `image`는 절대 URL) |
| POST | `/api_root/Post/` | 게시물 작성 (multipart/form-data: `author`, `title`, `text`, `image`, 선택 `published_date`) |
| GET | `/api_root/Post/<id>/` | 게시물 단건 조회 |
| PUT/PATCH | `/api_root/Post/<id>/` | 게시물 수정 |
| DELETE | `/api_root/Post/<id>/` | 게시물 삭제 |

`published_date`를 보내지 않으면 서버가 현재 시각으로 채워, 웹 목록에도 바로 표시된다.

응답 예시:

```json
[
  {
    "id": 1,
    "author": 1,
    "title": "첫 번째 사진",
    "text": "본문",
    "created_date": "2026-10-16T00:02:42.982694+09:00",
    "published_date": "2026-10-16T00:02:42.982554+09:00",
    "image": "http://127.0.0.1:8000/media/images/2026/10/16/a.jpg"
  }
]
```

### 브라우저에서 API로 게시물 작성 (보고서 ID 3)

1. `runserver` 실행 후 http://127.0.0.1:8000/api_root/Post/ 접속 → 우상단 **Log in**으로 로그인
2. 페이지 하단 **HTML form** 탭에서 Author 선택, Title/Text 입력, Image 파일 선택 → **POST**
3. `HTTP 201 Created` 응답 화면 확인 → http://127.0.0.1:8000/ 웹 목록에도 표시됨

## 토큰 생성

방법 1 — 관리 명령 (토큰이 이미 있으면 기존 토큰 출력):

```powershell
python manage.py drf_create_token <username>
# Generated token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b for user admin
```

방법 2 — API (아이디/비밀번호로 발급):

```powershell
curl.exe -X POST -d "username=<id>&password=<pw>" http://127.0.0.1:8000/api-token-auth/
# {"token":"9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

방법 3 — 관리자 화면: http://127.0.0.1:8000/admin/ → **인증 토큰 > 토큰(들)**

토큰 재발급이 필요하면 `python manage.py drf_create_token -r <username>`.

## telnet / JSON Viewer 검증

> 작성 예정 (Task 2)

## API 검증 엔진 · 자동 테스트 · Coverage

> 작성 예정 (Task 3)

## Socket Server

> 작성 예정 (Task 4)

## Android 앱 실행

> 작성 예정 (Task 5~6)

## PythonAnywhere 배포

> 작성 예정 (Task 7)

## Client 편의 기능

> 작성 예정 (Task 8)

## 구현 노트

교수님 코드(`kiokahn/web_blog` main, `cfd84c0`)·슬라이드와 다르게 구현한 부분과 그 이유를 기록한다.

### 서버 (교수님 코드 수정 사항)

1. **모델/마이그레이션 불일치 정리** — 모델은 `upload_to='images/%Y/%m/%d/'`, `default='images/default_error.png'`인데 마지막 마이그레이션(0003)은 `intruder_image/...`로 남아 있었다. `makemigrations`로 `0004_alter_post_image.py`를 생성해 일치시켰다.
2. **API로 올린 글이 웹 목록에 보이도록** — 웹 `post_list`는 `published_date <= now`인 글만 보여주는데 API POST는 `published_date`가 null로 저장됐다. `BlogImages.perform_create`에서 값이 없으면 `timezone.now()`로 채운다. (값을 보내면 그대로 사용)
3. **토큰 인증 적용** — `REST_FRAMEWORK`에 인증 클래스가 없어 `Authorization: Token ...` 헤더가 무시됐다. `TokenAuthentication`, `SessionAuthentication` + `IsAuthenticated`를 기본값으로 지정했다.
   - **Token을 Session보다 앞에 둔다.** DRF는 첫 번째 인증 클래스로 401/403을 결정하므로, Session이 먼저면 인증 없는 요청이 403이 된다. Token을 먼저 두어 401 + `WWW-Authenticate: Token` 헤더로 응답하게 했다.
   - 브라우저블 API 로그인을 위해 `api-auth/`(`rest_framework.urls`)를 추가했다.
4. **`PAGE_SIZE: 10` 제거** — 페이지네이션 클래스가 없어 실제로는 무시되던 값이고 `manage.py check` 경고(W001)만 냈다. 페이지네이션을 켜면 응답이 JSON 배열이 아니게 되어 앱 파싱이 깨지므로 켜지 않고 제거했다.
5. **ViewSet 이름 변경** — `IntruderImage` → 슬라이드와 같은 `BlogImages`.
6. **serializer에 `id` 추가** — 앱의 삭제·상세 기능에서 게시물을 식별하기 위함. 기존 필드 순서는 유지했다.
7. **웹 글쓰기 폼 이미지 업로드 지원** — 웹 `+` 버튼으로도 이미지 포함 게시물을 쓸 수 있게 했다.
   - `PostForm`에 `image` 추가. 이미지 미선택 시 새 글은 모델 기본값(`default_error.png`), 수정은 기존 이미지 유지. "지우기" 체크박스(ClearableFileInput)는 image가 빈 값이 되어 목록의 `post.image.url`에서 오류가 나므로 `FileInput`을 사용했다.
   - `post_edit.html` 폼에 `enctype="multipart/form-data"`, 뷰에서 `request.FILES` 전달.
   - `post_new`/`post_edit`에 `@login_required` 적용 — 기존에는 비로그인 상태로 저장하면 `author=AnonymousUser`로 오류가 났다. 로그인 화면은 `LOGIN_URL = 'rest_framework:login'`(DRF 로그인 화면)을 재사용한다.
   - `post_detail.html`에 이미지 표시 추가 (목록 화면은 슬라이드 25와 같게 유지).
   - 보고서 ID 14(Client 편의 기능)에는 포함하지 않는다.

> 알려진 동작(미수정): 교수님 코드의 `post_edit`은 수정할 때마다 `author`를 수정한 사용자로, `published_date`를 수정 시각으로 덮어쓴다. 과제 범위 밖이라 그대로 둔다.

### 클라이언트

- Android 프로젝트는 Groovy `build.gradle`이 아닌 Kotlin DSL(`build.gradle.kts`) + 버전 카탈로그(`gradle/libs.versions.toml`)를 사용한다. 의존성은 이 두 파일에 추가한다.
