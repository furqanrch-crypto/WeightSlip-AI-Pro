export default function Sidebar() {
  const items = [
    "📊 Dashboard",
    "🧾 OCR Queue",
    "🕘 History",
    "⚙ Settings",
    "ℹ About",
  ];

  return (
    <aside
      style={{
        width: "220px",
        background: "#111827",
        minHeight: "calc(100vh - 70px)",
        padding: "25px 15px",
        borderRight: "1px solid #263244",
      }}
    >
      {items.map((item, index) => (
        <div
          key={item}
          style={{
            padding: "13px 15px",
            marginBottom: "8px",
            borderRadius: "8px",
            background: index === 0 ? "#2563eb" : "transparent",
            cursor: "pointer",
          }}
        >
          {item}
        </div>
      ))}
    </aside>
  );
}