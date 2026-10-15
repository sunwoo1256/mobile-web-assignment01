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

안드로이드 앱이 보내는 것과 같은 HTTP 요청을 telnet으로 직접 보내 응답을 확인한다. 요청 원문은 [`PhotoBlogServer/tools/telnet_request.txt`](PhotoBlogServer/tools/telnet_request.txt)에 있다 (`<TOKEN>`을 실제 토큰으로 바꿔 사용).

```
GET /api_root/Post/ HTTP/1.1
Authorization: Token <TOKEN>
User-Agent: Dalvik/2.1.0 (Linux; U; Android 13; sdk_gphone64_arm64 Build/TPB4.220624.004)
Host: 10.0.2.2:8000
Connection: Keep-Alive
Accept-Encoding: gzip

```

- 헤더 끝을 알리는 **빈 줄(Enter 한 번 더)이 반드시 있어야** 서버가 응답한다.
- `Host`는 `ALLOWED_HOSTS`에 있는 값이어야 한다(아니면 400). `10.0.2.2:8000`으로 보내면 응답의 `image` URL도 `http://10.0.2.2:8000/...`로 만들어진다.
- `Accept-Encoding: gzip`이 있어도 Django 개발 서버는 압축하지 않으므로(GZipMiddleware 미사용) 응답 본문은 평문 JSON이다. 응답이 깨진 바이너리로 보이면 이 줄을 빼고 보낸다.

### Windows에서 Telnet Client 활성화

- 방법 1: 제어판 → 프로그램 → **Windows 기능 켜기/끄기** → **텔넷 클라이언트(Telnet Client)** 체크 → 확인
- 방법 2: **관리자 권한** PowerShell에서
  ```powershell
  Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient
  ```
- macOS: `brew install telnet`

### 요청 보내기 (Windows)

```powershell
chcp 65001          # 응답의 한글(UTF-8)이 깨지지 않도록 콘솔 코드페이지 변경
telnet
```

telnet 프롬프트(`Microsoft Telnet>`)에서:

```
set localecho       # 입력한 내용이 화면에 보이도록 (기본은 안 보임)
open 127.0.0.1 8000
```

연결되면 화면이 지워진다. 이 상태에서 요청 원문(토큰 치환본)을 붙여넣고(Windows Terminal: `Ctrl+V` 또는 마우스 오른쪽 클릭) 마지막에 **Enter를 한 번 더** 눌러 빈 줄을 보낸다.
> **주의: telnet은 누른 키를 즉시 서버로 보낸다.** 방향키(↑)·백스페이스로 수정하면 그 제어 코드(`\u001b[A` 등)까지 전송되어 `405 Method Not Allowed`(메서드 `"\u001b[A...GET"`)가 나고 연결이 끊긴다. 연결 후에는 다른 키를 누르지 말고 붙여넣기만 하고, 잘못 입력했으면 `Ctrl + ]` → `quit` 후 다시 `open`한다.

`HTTP/1.1 200 OK` 헤더와 JSON 배열 본문이 출력된다. 토큰을 빼거나 틀리게 보내면 `401 Unauthorized`가 나온다.
종료: `Ctrl + ]` → `quit`

> `chcp 65001`을 해도 한글이 깨져 보이면 콘솔 표시 문제일 뿐 서버 응답은 정상(UTF-8)이다. 다음 단계의 JSON Viewer에서는 정상 표시된다.

### JSON Viewer로 응답 확인

1. telnet 응답에서 본문(`[` ~ `]`)만 복사
2. https://codebeautify.org/jsonviewer 왼쪽 입력창에 붙여넣기
3. **Beautify** / **Tree View**로 구조 확인

## API 검증 엔진 · 자동 테스트 · Coverage

강의자료 ch04(TDD) 방식으로 **엔진(실제 코드) ↔ 테스트 코드**를 짝으로 만들었다. 테스트는 표준 라이브러리 `unittest`만 사용한다.

| 파일 | 역할 |
|---|---|
| [`api_test_engine/photoblog_api.py`](PhotoBlogServer/api_test_engine/photoblog_api.py) | 엔진. 포토 블로그 REST API 호출·검증 클래스 `PhotoBlogApi` (`urllib`만 사용) |
| [`api_test_engine/test_photoblog_api.py`](PhotoBlogServer/api_test_engine/test_photoblog_api.py) | 엔진 테스트. 단위 37개(서버 없이 `FakeServer`로 HTTP 대체) + 통합 9개(실제 서버) |
| [`blog/tests.py`](PhotoBlogServer/blog/tests.py) | Django 서버 측 테스트 29개 (API·토큰·웹 뷰·모델) |

### 엔진 `PhotoBlogApi`

| 메서드 | 설명 |
|---|---|
| `get_token(username, password)` | `/api-token-auth/`로 토큰 발급 후 저장 |
| `get_posts()` | `GET /api_root/Post/` → JSON 배열 |
| `create_post(title, text, image_path, author=None, published_date=None)` | multipart/form-data 업로드 (바디 직접 구성, 텍스트 UTF-8) |
| `delete_post(post_id)` | `DELETE /api_root/Post/<id>/` (204 기대) |
| `validate_post(post)` / `validate_post_list(posts)` | 필수 키·타입·image URL 검사 → 문제 목록 (빈 리스트면 정상) |
| `run_scenario(...)` | 토큰 → 목록 → 업로드 → 반영 확인 → 삭제 → 인증 없는 요청 거부(401) 6단계 실행 |

기대한 상태코드가 아니면 `ApiError(status, message)`를 던진다(연결 실패 시 `status=None`).

CLI로 서버 하나를 통째로 검증할 수 있다 (로컬/PythonAnywhere 공용, 실패 시 exit code 1):

```powershell
cd PhotoBlogServer\api_test_engine
..\venv\Scripts\python photoblog_api.py --base-url http://127.0.0.1:8000 --user <id> --password <pw> --author <user id>
```
```
대상 서버: http://127.0.0.1:8000
[PASS] 1. 토큰 발급 - token=52ce898a...
[PASS] 2. 목록 조회 및 스키마 검증 - 0건, 스키마 정상
[PASS] 3. 게시물 업로드 - id=5, title=scenario-79bdc8a8
[PASS] 4. 목록 반영 확인 - id=5 목록에 있음
[PASS] 5. 게시물 삭제 - id=5 삭제(204)
[PASS] 6. 인증 없는 요청 거부 - 401 Unauthorized
결과: 6/6 통과
```

> `--author`는 현재 서버가 `author`를 필수로 받기 때문에 필요하다(관리자 계정은 보통 `1`). 업로드한 글은 시나리오 끝에 삭제하지만, 서버의 `media/`에 이미지 파일은 남는다(Django는 행 삭제 시 파일을 지우지 않음).

### 테스트 실행

```powershell
cd PhotoBlogServer
pip install -r requirements-dev.txt          # coverage 설치

# 1) 엔진 테스트 — 서버 없이도 실행 가능 (통합 테스트는 skip)
cd api_test_engine
..\venv\Scripts\python test_photoblog_api.py

# 통합 테스트까지 실행하려면 runserver를 켠 상태에서 환경변수 지정
$env:PHOTOBLOG_BASE_URL = "http://127.0.0.1:8000"
$env:PHOTOBLOG_USER = "<id>"
$env:PHOTOBLOG_PASSWORD = "<pw>"
$env:PHOTOBLOG_AUTHOR = "1"                  # 선택, 기본 1
..\venv\Scripts\python test_photoblog_api.py

# 2) 서버 측 테스트 (임시 DB·임시 media 사용, 실제 데이터에 영향 없음)
cd ..
python manage.py test blog -v 2
```

### Code Coverage

```powershell
# 엔진 커버리지 (보고서 ID 6 메인)
cd PhotoBlogServer\api_test_engine
..\venv\Scripts\python -m coverage run test_photoblog_api.py
..\venv\Scripts\python -m coverage report -m
..\venv\Scripts\python -m coverage html      # → api_test_engine\htmlcov\index.html

# 서버 측 커버리지 (보조)
cd ..
python -m coverage run --source=blog manage.py test blog
python -m coverage report -m
python -m coverage html                      # → PhotoBlogServer\htmlcov\index.html
```

측정 결과:

| 대상 | 결과 |
|---|---|
| `photoblog_api.py` (엔진) | **100%** — 구문 203 / 분기 52, Miss 0 (`.coveragerc`에서 branch 측정) |
| `test_photoblog_api.py` | 서버 실행 시 98%, 미실행 시 87% (차이는 skip된 통합 테스트) |
| `blog` 앱 | **100%** — 290 구문, Miss 0 |

`api_test_engine/.coveragerc`는 분기 커버리지를 켜고, CLI 진입점(`if __name__ == '__main__':`) 한 줄만 측정에서 제외한다(`main()`은 테스트에서 직접 호출해 검증).

### TDD 진행 기록

git 이력으로 확인할 수 있다.

1. `7bb57d2 test(engine): ...` — 테스트 먼저 작성, 엔진은 인터페이스만 → `FAILED (failures=9, errors=37, skipped=1)`
2. `15f2658 feat(engine): ...` — 엔진 구현 → `OK (skipped=1)`, 커버리지 100%

빨강 단계를 다시 보려면: `git stash; git checkout 7bb57d2 -- PhotoBlogServer/api_test_engine` → 실행 → `git checkout HEAD -- PhotoBlogServer/api_test_engine; git stash pop`

## Socket Server

앱이 보내는 HTTP 요청 원문(헤더 + multipart 바디)을 파일로 저장하는 소켓 서버. 자세한 내용은 [`PhotoBlogServer/socket_server/README.md`](PhotoBlogServer/socket_server/README.md).

```powershell
# Django 서버를 끈 뒤 같은 포트(8000)로 실행
cd PhotoBlogServer\socket_server
..\venv\Scripts\python socket_server.py
```

앱에서 동기화/업로드 → `socket_server/request/YYYY-MM-DD-HH-MM-SS.bin` 생성 → VSCode로 열어 확인.

## Android 앱 실행

`PhotoViewer/`를 Android Studio로 연다 (compileSdk/targetSdk 34, minSdk 24, Java 11).

### 서버 주소·토큰 설정

토큰을 레포에 올리지 않기 위해 **`PhotoViewer/local.properties`**(git 제외)에 적는다. 빌드 시 `BuildConfig.DEFAULT_BASE_URL` / `DEFAULT_TOKEN`으로 들어가 앱의 기본값이 된다.

```properties
photoblog.baseUrl=http://10.0.2.2:8000
photoblog.token=<python manage.py drf_create_token <user> 로 만든 토큰>
```

- 에뮬레이터에서 PC의 `127.0.0.1`은 `10.0.2.2`다. Django는 `python manage.py runserver 0.0.0.0:8000`으로 실행한다.
- 값은 [`ApiConfig`](PhotoViewer/app/src/main/java/com/example/imageviewdemo/ApiConfig.java)에서 한 곳으로 관리한다. SharedPreferences에 저장된 값이 있으면 그것을, 없으면 위 기본값을 쓴다(설정 화면은 Task 8).
- `local.properties`를 바꾼 뒤에는 다시 빌드해야 반영된다.

### 빌드 (명령줄)

```powershell
cd PhotoViewer
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
.\gradlew assembleDebug        # → app\build\outputs\apk\debug\app-debug.apk
```

### 동기화

1. Django 서버 실행
2. 앱에서 **동기화** → `GET /api_root/Post/` (헤더 `Authorization: Token <토큰>`) → 각 게시물의 `image` URL에서 이미지 다운로드 → 목록 표시
3. "이미지 로드 성공!" 표시. 게시물이 없으면 "불러올 이미지가 없습니다.", 서버 오류면 상태코드/원인을 표시

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

### 테스트

- 초록 단계 구현 중 테스트용 `FakeServer`가 `json.dumps` 기본값(`ensure_ascii=True`)으로 한글을 `\uXXXX`로 내보내 실패한 테스트 2건이 있었다. 실제 DRF 서버는 UTF-8 원문을 보내므로(telnet으로 확인) 가짜 서버를 `ensure_ascii=False`로 고쳤다.
- `blog/tests.py`는 Task 0에서 이미 구현한 서버 기능을 검증하므로 빨강 단계 없이 작성했다. 이후 서버 기능(Task 8)은 테스트를 먼저 추가한다.

> 알려진 동작(미수정): 교수님 코드의 `post_edit`은 수정할 때마다 `author`를 수정한 사용자로, `published_date`를 수정 시각으로 덮어쓴다. 과제 범위 밖이라 그대로 둔다.

### 클라이언트

- Android 프로젝트는 Groovy `build.gradle`이 아닌 Kotlin DSL(`build.gradle.kts`) + 버전 카탈로그(`gradle/libs.versions.toml`)를 사용한다. 의존성은 이 두 파일에 추가한다.
- 라이브러리 버전: `appcompat 1.7.0`, `material 1.12.0`, `activity 1.9.3`(compileSdk 34 호환), `recyclerview 1.3.2`, `swiperefreshlayout 1.1.0` 추가. 템플릿 버전으로도 빌드 문제는 없었으며 `resolutionStrategy.force`는 필요하지 않았다. (`coreKtx`는 Java 템플릿에 없어 추가하지 않음)
- **서버 주소·토큰 하드코딩 제거**: 슬라이드는 `MainActivity`에 `site_url`과 토큰을 직접 적지만, `ApiConfig`(SharedPreferences) + `local.properties` → `BuildConfig` 기본값으로 관리한다. 토큰이 레포에 올라가지 않고, 로컬/PythonAnywhere 전환이 쉽다.
- 슬라이드 19의 `private class. CloadImage` 오타를 수정했다(`private class CloadImage`).
- 인증 헤더는 `Token <토큰>` 형식이다(서버가 DRF `TokenAuthentication` 사용).
- 이미지는 `BitmapFactory.Options.inJustDecodeBounds`로 크기를 먼저 읽고 화면 너비에 맞춰 `inSampleSize`로 줄여 디코딩한다(큰 사진의 OOM 방지). 이미지 요청에는 토큰을 붙이지 않는다(media는 인증 없이 제공).
- 네트워크 오류·HTTP 오류를 화면에 표시하고, 연결/읽기 타임아웃(10초/15초)을 둔다.
- 템플릿의 EdgeToEdge 코드가 루트 padding을 시스템 바 크기로 덮어써서 레이아웃 여백(8dp)이 사라지므로, 기본 여백 + 시스템 바로 계산하게 했다.
- 앱 표시 이름을 `imageviewdemo`에서 `PhotoViewer`로 바꿨다(패키지명은 그대로 `com.example.imageviewdemo`).
- AsyncTask는 deprecated지만 수업 코드와의 일관성을 위해 사용했다.
