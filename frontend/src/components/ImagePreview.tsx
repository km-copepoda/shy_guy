interface ImagePreviewProps {
  originalUrl: string | null;
  processedUrl: string | null;
  facesDetected: number | null;
}

export default function ImagePreview({
  originalUrl,
  processedUrl,
  facesDetected,
}: ImagePreviewProps) {
  if (!originalUrl) return null;

  return (
    <div className="preview-container">
      <div className="preview-card">
        <h3>元画像</h3>
        <img src={originalUrl} alt="元画像" />
      </div>

      {processedUrl && (
        <div className="preview-card">
          <h3>モザイク処理済み</h3>
          <img src={processedUrl} alt="モザイク済み画像" />

          {facesDetected !== null && (
            <p className="faces-info">
              {facesDetected === 0
                ? "顔が検出されませんでした"
                : `${facesDetected} 個の顔が検出されました`}
            </p>
          )}

          <a
            className="download-btn"
            href={processedUrl}
            download="mosaic_result.png"
          >
            ダウンロード
          </a>
        </div>
      )}
    </div>
  );
}
