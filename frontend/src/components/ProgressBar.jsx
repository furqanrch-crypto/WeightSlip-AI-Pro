export default function ProgressBar() {
  return (
    <section
      style={{
        background: "#1e293b",
        border: "1px solid #334155",
        borderRadius: "12px",
        padding: "20px",
        marginTop: "18px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "10px",
        }}
      >
        <span>OCR Progress</span>
        <span>0%</span>
      </div>

      <div
        style={{
          background: "#334155",
          height: "12px",
          borderRadius: "20px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: "0%",
            height: "100%",
            background: "#22c55e",
          }}
        />
      </div>
    </section>
  );
}