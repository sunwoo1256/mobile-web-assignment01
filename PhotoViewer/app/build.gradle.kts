import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
}

// 서버 주소·토큰 기본값은 local.properties(git 제외)에서 읽는다. 앱 실행 중에는 ApiConfig로 변경 가능
val localProperties = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.exists()) file.inputStream().use { load(it) }
}
fun localProperty(key: String, default: String) = localProperties.getProperty(key, default)

android {
    namespace = "com.example.imageviewdemo"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.imageviewdemo"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        buildConfigField("String", "DEFAULT_BASE_URL",
            "\"${localProperty("photoblog.baseUrl", "http://10.0.2.2:8000")}\"")
        buildConfigField("String", "DEFAULT_TOKEN",
            "\"${localProperty("photoblog.token", "")}\"")
    }

    buildFeatures {
        buildConfig = true
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {

    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.activity)
    implementation(libs.constraintlayout)
    implementation(libs.recyclerview)
    implementation(libs.swiperefreshlayout)
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}
