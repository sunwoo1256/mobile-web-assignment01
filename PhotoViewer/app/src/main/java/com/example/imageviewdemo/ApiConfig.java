package com.example.imageviewdemo;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * 서버 주소·토큰을 한 곳에서 관리한다.
 * SharedPreferences에 저장된 값을 우선 사용하고, 없으면 BuildConfig 기본값(local.properties)을 사용한다.
 */
public final class ApiConfig {
    public static final String POSTS_PATH = "/api_root/Post/";

    private static final String PREFS = "photoblog";
    private static final String KEY_BASE_URL = "base_url";
    private static final String KEY_TOKEN = "token";

    private ApiConfig() {
    }

    private static SharedPreferences prefs(Context context) {
        return context.getApplicationContext().getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static String getBaseUrl(Context context) {
        String url = prefs(context).getString(KEY_BASE_URL, BuildConfig.DEFAULT_BASE_URL);
        // 끝의 '/'를 제거해 경로를 붙일 때 '//'가 되지 않게 한다
        return url.endsWith("/") ? url.substring(0, url.length() - 1) : url;
    }

    public static void setBaseUrl(Context context, String baseUrl) {
        prefs(context).edit().putString(KEY_BASE_URL, baseUrl.trim()).apply();
    }

    public static String getToken(Context context) {
        return prefs(context).getString(KEY_TOKEN, BuildConfig.DEFAULT_TOKEN);
    }

    public static void setToken(Context context, String token) {
        prefs(context).edit().putString(KEY_TOKEN, token.trim()).apply();
    }

    public static String getPostsUrl(Context context) {
        return getBaseUrl(context) + POSTS_PATH;
    }
}
