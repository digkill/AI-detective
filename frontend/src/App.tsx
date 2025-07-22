import React, { useState } from "react";

type ResultType = {
    verdict: string;
    confidence: number;
    explanation: string;
    heatmap?: string | null;
};

const App: React.FC = () => {
    const [result, setResult] = useState<ResultType | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleUpload(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setLoading(true);
        setResult(null);

        const target = e.target as HTMLFormElement;
        const fileInput = target.elements.namedItem("file") as HTMLInputElement;
        if (!fileInput.files?.[0]) return;

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const res = await fetch("/api/analyze", {
            method: "POST",
            body: formData,
        });

        setLoading(false);

        if (res.ok) {
            setResult(await res.json());
        } else {
            setResult({
                verdict: "Ошибка",
                confidence: 0,
                explanation: "Ошибка сервера",
            });
        }
    }

    return (
        <div style={{ maxWidth: 600, margin: "0 auto", padding: 40 }}>
            <h1>AI-Detective</h1>
            <form onSubmit={handleUpload}>
                <input type="file" name="file" accept="image/*,video/*" required />
                <button type="submit" disabled={loading}>
                    {loading ? "Анализируем..." : "Анализировать"}
                </button>
            </form>
            {result && (
                <div style={{ marginTop: 32 }}>
                    <h2>Результат:</h2>
                    <p>
                        <b>Вердикт:</b> {result.verdict}
                        <br />
                        <b>Уверенность:</b> {(result.confidence * 100).toFixed(1)}%
                        <br />
                        <b>Комментарий:</b> {result.explanation}
                    </p>
                    {result.heatmap && (
                        <>
                            <h3>Heatmap:</h3>
                            <img
                                src={`data:image/png;base64,${result.heatmap}`}
                                alt="heatmap"
                                style={{ maxWidth: "100%" }}
                            />
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default App;
