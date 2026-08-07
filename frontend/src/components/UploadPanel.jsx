export default function UploadPanel() {
  return (
    <section
      style={{
        background: "#1e293b",
        borderRadius: "14px",
        padding: "28px",
        border: "1px solid #334155",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Upload Weight Slips</h3>

      <div
        style={{
          border: "2px dashed #475569",
          borderRadius: "12px",
          padding: "45px 20px",
          textAlign: "center",
          color: "#cbd5e1",
        }}
      >
        <div style={{ fontSize: "42px" }}>📤</div>
        <h3>Drop weight slips here</h3>
        <p>Images, WhatsApp ZIP or PDF</p>

        <div
          style={{
            display: "flex",
            gap: "12px",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <button className="upload-btn">📂 Images</button>
          <button className="upload-btn">📦 WhatsApp ZIP</button>
          <button className="upload-btn">📄 PDF</button>
        </div>
      </div>
    </section>
  );
}