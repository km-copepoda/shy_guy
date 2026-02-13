import { useCallback, useState } from "react";
import ImageUploader from "./components/ImageUploader";
import ImagePreview from "./components/ImagePreview";
import { useMosaicApi } from "./hooks/useMosaicApi";
import "./App.css";

export default function App() {
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const { result, isLoading, error, processImage, reset } = useMosaicApi();

  const handleFileSelect = useCallback(
    (file: File) => {
      // Revoke previous original URL
      setOriginalUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return URL.createObjectURL(file);
      });
      processImage(file);
    },
    [processImage]
  );

  const handleReset = useCallback(() => {
    setOriginalUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    reset();
  }, [reset]);

  return (
    <div className="app">
      <h1 className="title">Shy Guy</h1>
      <p className="subtitle">
        画像をアップロードすると、自動で顔を検出してモザイク処理します
      </p>

      <ImageUploader onFileSelect={handleFileSelect} disabled={isLoading} />

      {isLoading && <p className="loading">処理中...</p>}

      {error && (
        <div className="error">
          <p>{error}</p>
        </div>
      )}

      <ImagePreview
        originalUrl={originalUrl}
        processedUrl={result?.imageUrl ?? null}
        facesDetected={result?.facesDetected ?? null}
      />

      {(originalUrl || result) && (
        <button className="reset-btn" onClick={handleReset}>
          リセット
        </button>
      )}
    </div>
  );
}
