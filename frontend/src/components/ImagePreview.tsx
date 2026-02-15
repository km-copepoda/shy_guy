interface ImagePreviewProps {
  originalUrl: string | null;
  processedUrl: string | null;
  facesDetected: number | null;
  mediaType: string | null;
}

function buildDownloadFilename(mediaType: string | null): string {
  const now = new Date();
  const ts = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
    "_",
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join("");
  const ext = mediaType === "image/png" ? ".png" : ".jpg";
  return ts + ext;
}

export default function ImagePreview({
  originalUrl,
  processedUrl,
  facesDetected,
  mediaType,
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
            download={buildDownloadFilename(mediaType)}
          >
            ダウンロード
          </a>
        </div>
      )}
    </div>
  );
}
