import sys
import json
from PIL import Image
from transformers import pipeline
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch16")

def generate_demo_heatmap(image_path):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img).astype(float)
    h, w, _ = arr.shape
    heatmap = np.random.rand(h, w)
    heatmap = (heatmap * 255).astype(np.uint8)

    plt.figure(figsize=(6,6))
    plt.imshow(img)
    plt.imshow(heatmap, cmap="jet", alpha=0.4)
    plt.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return encoded

def analyze_image(path):
    candidate_labels = [
        "AI-generated",
        "real photo",
        "deepfake",
        "CGI",
        "drawing",
        "cartoon",
        "photo of a real person"
    ]
    try:
        img = Image.open(path).convert("RGB")
        result = classifier(img, candidate_labels=candidate_labels)
        best = result[0]
        label = best['label']
        score = float(best['score'])
    except Exception as e:
        return {
            "verdict": "Error",
            "confidence": 0.0,
            "explanation": f"Ошибка модели: {e}",
            "heatmap": None
        }
    verdict = "AI" if "ai" in label.lower() or "deepfake" in label.lower() or "cgi" in label.lower() else "Human"
    explanation = f"Best label: {label} ({score:.2%})"
    heatmap = generate_demo_heatmap(path)
    return {
        "verdict": verdict,
        "confidence": score,
        "explanation": explanation,
        "heatmap": heatmap
    }

if __name__ == "__main__":
    result = analyze_image(sys.argv[1])
    print(json.dumps(result))
