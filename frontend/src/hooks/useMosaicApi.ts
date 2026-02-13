import { useCallback, useRef, useState } from "react";

interface MosaicResult {
  imageUrl: string;
  facesDetected: number;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

export function useMosaicApi() {
  const [result, setResult] = useState<MosaicResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const prevUrlRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const processImage = useCallback(
    async (file: File, pixelSize: number = 20, scoreThreshold: number = 0.5) => {
      // File size check (sync with backend)
      if (file.size > MAX_FILE_SIZE) {
        setError("ファイルサイズが10MBを超えています。");
        return;
      }

      // Revoke previous URL to prevent memory leak
      if (prevUrlRef.current) {
        URL.revokeObjectURL(prevUrlRef.current);
        prevUrlRef.current = null;
      }

      // Abort previous request
      if (abortRef.current) {
        abortRef.current.abort();
      }
      const controller = new AbortController();
      abortRef.current = controller;

      setIsLoading(true);
      setError(null);
      setResult(null);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
          `/api/mosaic?pixel_size=${pixelSize}&score_threshold=${scoreThreshold}`,
          {
            method: "POST",
            body: formData,
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          const text = await response.text();
          throw new Error(text || `エラーが発生しました (${response.status})`);
        }

        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        prevUrlRef.current = imageUrl;

        const facesDetected = parseInt(
          response.headers.get("X-Faces-Detected") || "0",
          10
        );

        setResult({ imageUrl, facesDetected });
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          // Normal cancellation — ignore
          return;
        }
        setError(
          err instanceof Error ? err.message : "不明なエラーが発生しました。"
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (prevUrlRef.current) {
      URL.revokeObjectURL(prevUrlRef.current);
      prevUrlRef.current = null;
    }
    setResult(null);
    setIsLoading(false);
    setError(null);
  }, []);

  return { result, isLoading, error, processImage, reset };
}
