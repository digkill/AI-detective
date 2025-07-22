import sys
import json
import cv2
import os
from detector import analyze_image

def extract_keyframes(video_path, num_frames=1):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idxs = [total_frames // (num_frames + 1) * (i + 1) for i in range(num_frames)]

    for idx in frame_idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            img_path = f"frame_{idx}.jpg"
            cv2.imwrite(img_path, frame)
            frames.append(img_path)
    cap.release()
    return frames

def analyze_video(video_path):
    # 1. Вытаскиваем кадры
    frame_files = extract_keyframes(video_path, num_frames=3)
    results = []
    for frame_file in frame_files:
        result = analyze_image(frame_file)
        results.append(result)
        # Удаляем временные файлы
        try:
            os.remove(frame_file)
        except Exception:
            pass

    if not results:
        return {
            "verdict": "Error",
            "confidence": 0.0,
            "explanation": "Не удалось получить кадры из видео.",
            "heatmaps": []
        }
    # 2. Аггрегируем результаты по кадрам
    ai_scores = [r["confidence"] for r in results if r["verdict"] == "AI"]
    human_scores = [r["confidence"] for r in results if r["verdict"] == "Human"]

    if ai_scores and (not human_scores or max(ai_scores) > max(human_scores)):
        verdict = "AI"
        confidence = max(ai_scores)
    else:
        verdict = "Human"
        confidence = max(human_scores) if human_scores else 0.0

    explanation = "; ".join([f"{i+1}-й кадр: {r['explanation']}" for i, r in enumerate(results)])
    heatmaps = [r["heatmap"] for r in results]

    return {
        "verdict": verdict,
        "confidence": confidence,
        "explanation": explanation,
        "heatmaps": heatmaps
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "verdict": "Error",
            "confidence": 0.0,
            "explanation": "No video path provided.",
            "heatmaps": []
        }))
        sys.exit(1)

    result = analyze_video(sys.argv[1])
    print(json.dumps(result))
