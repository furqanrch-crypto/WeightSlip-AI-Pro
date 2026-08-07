export default function Header() {
  return (
    <header
      style={{
        height: "70px",
        background: "#111827",
        borderBottom: "1px solid #263244",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 28px",
      }}
    >
      <div>
        <h2 style={{ margin: 0 }}>WeightSlip AI Pro</h2>
        <small style={{ color: "#94a3b8" }}>
          AI Powered OCR & Excel Export
        </small>
      </div>

      <button
        style={{
          background: "#1e293b",
          color: "white",
          border: "1px solid #334155",
          borderRadius: "8px",
          padding: "9px 14px",
          cursor: "pointer",
        }}
      >
        ⚙ Settings
      </button>
    </header>
  );
}