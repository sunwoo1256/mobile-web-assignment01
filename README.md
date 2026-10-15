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

> 작성 예정 (Task 1) — Python 3.12 이상 필요 (Django 6.1)

## 토큰 생성

> 작성 예정 (Task 1)

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

슬라이드 코드와 다르게 구현한 부분과 그 이유를 기록한다.

- Android 프로젝트는 Groovy `build.gradle`이 아닌 Kotlin DSL(`build.gradle.kts`) + 버전 카탈로그(`gradle/libs.versions.toml`)를 사용한다. 의존성은 이 두 파일에 추가한다.
