import { useState } from "react";
import { uploadImage } from "../services/upload";

export default function ImagePreview({
  images,
  onRemove,
  onClear,
}) {
  const [uploadResult, setUploadResult] = useState(null);
  const [uploading, setUploading] = useState(false);

  if (!images.length) {
    return null;
  }

  const testUpload = async () => {
    try {
      setUploading(true);
      setUploadResult(null);

      const result = await uploadImage(images[0].file);

      setUploadResult(result);
    } catch (error) {
      console.error(error);

      setUploadResult({
        success: false,
        message: error.message,
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <section
      style={{
        marginTop: "18px",
        background: "#1e293b",
        border: "1px solid #334155",
        borderRadius: "12px",
        padding: "20px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "18px",
          gap: "12px",
        }}
      >
        <h3 style={{ margin: 0 }}>
          Selected Images ({images.length})
        </h3>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="button"
            onClick={testUpload}
            disabled={uploading}
            style={{
              background: "#2563eb",
              color: "white",
              border: 0,
              borderRadius: "8px",
              padding: "9px 14px",
              cursor: "pointer",
            }}
          >
            {uploading ? "Uploading..." : "Test Backend Upload"}
          </button>

          <button
            type="button"
            onClick={onClear}
            style={{
              background: "#7f1d1d",
              color: "white",
              border: 0,
              borderRadius: "8px",
              padding: "9px 14px",
              cursor: "pointer",
            }}
          >
            Clear All
          </button>
        </div>
      </div>

      {uploadResult && (
        <div
          style={{
            background: uploadResult.success
              ? "#14532d"
              : "#7f1d1d",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "16px",
          }}
        >
          <strong>
            {uploadResult.success
              ? "Backend connected ✅"
              : "Upload failed ❌"}
          </strong>

          <pre
            style={{
              whiteSpace: "pre-wrap",
              marginBottom: 0,
            }}
          >
            {JSON.stringify(uploadResult, null, 2)}
          </pre>
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fill, minmax(150px, 1fr))",
          gap: "15px",
        }}
      >
        {images.map((image) => (
          <div
            key={image.id}
            style={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "10px",
              overflow: "hidden",
            }}
          >
            <img
              src={image.preview}
              alt={image.name}
              style={{
                width: "100%",
                height: "120px",
                objectFit: "cover",
              }}
            />

            <div style={{ padding: "10px" }}>
              <div
                title={image.name}
                style={{
                  fontSize: "12px",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                  textOverflow: "ellipsis",
                }}
              >
                {image.name}
              </div>

              <button
                type="button"
                onClick={() => onRemove(image.id)}
                style={{
                  width: "100%",
                  marginTop: "8px",
                  border: 0,
                  borderRadius: "6px",
                  padding: "7px",
                  background: "#991b1b",
                  color: "white",
                  cursor: "pointer",
                }}
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}