package com.example.imageviewdemo;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "PhotoViewer";
    private static final int CONNECT_TIMEOUT_MS = 10000;
    private static final int READ_TIMEOUT_MS = 15000;

    TextView textView;
    RecyclerView recyclerView;
    CloadImage taskDownload;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        View root = findViewById(R.id.main);
        // 레이아웃의 기본 여백(8dp)에 시스템 바 영역을 더한다 (그대로 덮어쓰면 여백이 사라짐)
        int basePadding = root.getPaddingLeft();
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(basePadding + systemBars.left, basePadding + systemBars.top,
                    basePadding + systemBars.right, basePadding + systemBars.bottom);
            return insets;
        });

        textView = findViewById(R.id.textView);
        recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
    }

    public void onClickDownload(View v) {
        if (taskDownload != null && taskDownload.getStatus() == AsyncTask.Status.RUNNING) {
            taskDownload.cancel(true);
        }
        taskDownload = new CloadImage(ApiConfig.getToken(this), getResources().getDisplayMetrics().widthPixels);
        taskDownload.execute(ApiConfig.getPostsUrl(this));
        textView.setText("동기화 중...");
        Toast.makeText(getApplicationContext(), "Download", Toast.LENGTH_SHORT).show();
    }

    public void onClickUpload(View v) {
        Toast.makeText(getApplicationContext(), "Upload", Toast.LENGTH_SHORT).show();
    }

    /** 게시물 목록(JSON)을 받아 각 게시물의 이미지를 내려받는다 */
    private class CloadImage extends AsyncTask<String, Integer, List<Bitmap>> {
        private final String token;
        private final int targetWidth;
        private String errorMessage;

        CloadImage(String token, int targetWidth) {
            this.token = token;
            this.targetWidth = targetWidth;
        }

        @Override
        protected List<Bitmap> doInBackground(String... urls) {
            List<Bitmap> bitmapList = new ArrayList<>();
            HttpURLConnection conn = null;
            try {
                conn = (HttpURLConnection) new URL(urls[0]).openConnection();
                conn.setRequestProperty("Authorization", "Token " + token);
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(CONNECT_TIMEOUT_MS);
                conn.setReadTimeout(READ_TIMEOUT_MS);

                int responseCode = conn.getResponseCode();
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    errorMessage = "서버 응답 오류: HTTP " + responseCode;
                    return bitmapList;
                }
                String json = new String(readAll(conn.getInputStream()), StandardCharsets.UTF_8);
                JSONArray posts = new JSONArray(json);
                for (int i = 0; i < posts.length() && !isCancelled(); i++) {
                    JSONObject post = posts.getJSONObject(i);
                    String imageUrl = post.optString("image", "");
                    if (imageUrl.isEmpty()) {
                        continue;
                    }
                    Bitmap bitmap = downloadBitmap(imageUrl);
                    if (bitmap != null) {
                        bitmapList.add(bitmap);
                    }
                }
            } catch (Exception e) {
                Log.e(TAG, "동기화 실패", e);
                errorMessage = "동기화 실패: " + e.getMessage();
            } finally {
                if (conn != null) {
                    conn.disconnect();
                }
            }
            return bitmapList;
        }

        /** 큰 이미지로 인한 OOM을 막기 위해 화면 너비에 맞춰 inSampleSize로 줄여서 디코딩한다 */
        private Bitmap downloadBitmap(String imageUrl) {
            HttpURLConnection conn = null;
            try {
                conn = (HttpURLConnection) new URL(imageUrl).openConnection();
                conn.setConnectTimeout(CONNECT_TIMEOUT_MS);
                conn.setReadTimeout(READ_TIMEOUT_MS);
                if (conn.getResponseCode() != HttpURLConnection.HTTP_OK) {
                    Log.w(TAG, "이미지 응답 오류 " + conn.getResponseCode() + ": " + imageUrl);
                    return null;
                }
                byte[] bytes = readAll(conn.getInputStream());

                BitmapFactory.Options options = new BitmapFactory.Options();
                options.inJustDecodeBounds = true;
                BitmapFactory.decodeByteArray(bytes, 0, bytes.length, options);
                options.inSampleSize = calculateInSampleSize(options.outWidth, targetWidth);
                options.inJustDecodeBounds = false;
                return BitmapFactory.decodeByteArray(bytes, 0, bytes.length, options);
            } catch (IOException e) {
                Log.w(TAG, "이미지 다운로드 실패: " + imageUrl, e);
                return null;
            } finally {
                if (conn != null) {
                    conn.disconnect();
                }
            }
        }

        @Override
        protected void onPostExecute(List<Bitmap> images) {
            if (errorMessage != null) {
                textView.setText(errorMessage);
            } else if (images.isEmpty()) {
                textView.setText("불러올 이미지가 없습니다.");
            } else {
                textView.setText("이미지 로드 성공!");
            }
            recyclerView.setAdapter(new ImageAdapter(images));
        }
    }

    static int calculateInSampleSize(int imageWidth, int targetWidth) {
        int inSampleSize = 1;
        if (targetWidth <= 0) {
            return inSampleSize;
        }
        while (imageWidth / (inSampleSize * 2) >= targetWidth) {
            inSampleSize *= 2;
        }
        return inSampleSize;
    }

    static byte[] readAll(InputStream in) throws IOException {
        try (InputStream input = in; ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int read;
            while ((read = input.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
            return out.toByteArray();
        }
    }
}
