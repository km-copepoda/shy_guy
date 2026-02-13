import { useCallback, useState } from "react";
import ImageUploader from "./components/ImageUploader";
import ImagePreview from "./components/ImagePreview";
import { useMosaicApi } from "./hooks/useMosaicApi";
import "./App.css";

export default function App() {
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [scoreThreshold, setScoreThreshold] = useState(0.5);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const { result, isLoading, error, processImage, reset } = useMosaicApi();

  const handleFileSelect = useCallback(
    (file: File) => {
      setCurrentFile(file);
      // Revoke previous original URL
      setOriginalUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return URL.createObjectURL(file);
      });
      processImage(file, 20, scoreThreshold);
    },
    [processImage, scoreThreshold]
  );

  const handleThresholdChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseFloat(e.target.value);
      setScoreThreshold(value);
      if (currentFile) {
        processImage(currentFile, 20, value);
      }
    },
    [processImage, currentFile]
  );

  const handleReset = useCallback(() => {
    setOriginalUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    setCurrentFile(null);
    setScoreThreshold(0.5);
    reset();
  }, [reset]);

  return (
    <div className="app">
      <h1 className="title">Shy Guy</h1>
      <p className="subtitle">
        画像をアップロードすると、自動で顔を検出してモザイク処理します
      </p>

      <ImageUploader onFileSelect={handleFileSelect} disabled={isLoading} />

      <div className="threshold-control">
        <label htmlFor="score-threshold">
          検出しきい値: <strong>{scoreThreshold.toFixed(1)}</strong>
        </label>
        <input
          id="score-threshold"
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={scoreThreshold}
          onChange={handleThresholdChange}
          disabled={isLoading}
        />
        <span className="threshold-labels">
          <span>0.0（緩い）</span>
          <span>1.0（厳しい）</span>
        </span>
      </div>

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
