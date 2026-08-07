export default function ImagePreview({ images, onRemove, onClear }) {
  if (!images.length) return null;

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
        <h3 style={{ margin: 0 }}>Selected Images ({images.length})</h3>

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

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))",
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
              style={{ width: "100%", height: "120px", objectFit: "cover" }}
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

              <div style={{ marginTop: "8px", fontSize: "12px", color: "#93c5fd" }}>
                {image.processingStatus || "pending"} · {image.progress || 0}%
              </div>

              {image.record?.slip_no && (
                <div style={{ marginTop: "5px", fontSize: "12px" }}>
                  Slip: <strong>{image.record.slip_no}</strong>
                </div>
              )}

              {image.error && (
                <div style={{ marginTop: "5px", fontSize: "11px", color: "#fca5a5" }}>
                  {image.error}
                </div>
              )}

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
