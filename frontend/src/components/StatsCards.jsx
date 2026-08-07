export default function StatsCards() {
  const stats = [
    ["0", "Images Found"],
    ["0", "OCR Completed"],
    ["0 Kg", "Net Weight"],
    ["0", "Duplicates"],
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
        gap: "16px",
        marginTop: "18px",
      }}
    >
      {stats.map(([value, label]) => (
        <div
          key={label}
          style={{
            background: "#1e293b",
            padding: "22px",
            borderRadius: "12px",
            border: "1px solid #334155",
          }}
        >
          <div style={{ fontSize: "28px", fontWeight: 700 }}>{value}</div>
          <div style={{ color: "#94a3b8", marginTop: "5px" }}>{label}</div>
        </div>
      ))}
    </div>
  );
}