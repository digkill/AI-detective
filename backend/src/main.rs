use axum::{
    routing::post,
    Router,
    extract::Multipart,
    response::Json,
    http::StatusCode,
};
use serde_json::Value;
use std::{fs::File, io::Write, path::PathBuf, process::Command};
use uuid::Uuid;

#[tokio::main]
async fn main() {
    let app = Router::new().route("/api/analyze", post(analyze));
    println!("🚀 AI-Detective backend running on http://localhost:8000");
    axum::Server::bind(&"0.0.0.0:8000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn analyze(mut multipart: Multipart) -> Result<Json<Value>, StatusCode> {
    // 1. Сохраняем загруженный файл во временную папку
    let temp_dir = std::env::temp_dir();
    let mut filepath = PathBuf::from(&temp_dir);
    let mut found = false;

    while let Some(field) = multipart.next_field().await.unwrap() {
        let name = field.name().unwrap_or("").to_string();
        if name == "file" {
            let data = field.bytes().await.unwrap();
            let ext = field.file_name()
                .and_then(|f| PathBuf::from(f).extension().map(|e| e.to_string_lossy().to_string()))
                .unwrap_or("bin".to_string());
            let unique = format!("{}_upload.{}", Uuid::new_v4(), ext);
            filepath.push(unique);
            let mut f = File::create(&filepath).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            f.write_all(&data).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            found = true;
            break;
        }
    }

    if !found {
        return Err(StatusCode::BAD_REQUEST);
    }

    // 2. Запускаем Python-детектор
    let output = Command::new("python3")
        .arg("ai-detector/detector.py")
        .arg(filepath.to_string_lossy().to_string())
        .output()
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    // 3. Парсим stdout — JSON-ответ от детектора
    let out_str = String::from_utf8_lossy(&output.stdout);
    let res_json: Value = match serde_json::from_str(&out_str) {
        Ok(val) => val,
        Err(_) => {
            eprintln!("Ошибка парсинга ответа: {out_str}");
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 4. Удаляем файл после анализа
    let _ = std::fs::remove_file(&filepath);

    Ok(Json(res_json))
}
