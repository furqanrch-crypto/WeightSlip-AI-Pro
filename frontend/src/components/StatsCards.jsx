export default function StatsCards({
  imageCount = 0,
  ocrCompleted = 0,
  netWeight = 0,
  duplicates = 0,
}) {
  const stats = [
    [imageCount, "Images Found"],
    [ocrCompleted, "OCR Completed"],
    [`${netWeight.toLocaleString()} Kg`, "Net Weight"],
    [duplicates, "Duplicates"],
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