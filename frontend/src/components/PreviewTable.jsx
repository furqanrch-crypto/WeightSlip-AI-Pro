function displayDate(record) {
  const value = record.first_datetime || record.second_datetime;
  if (!value) return "—";

  const match = String(value).match(/\b\d{1,2}[-/]?[A-Za-z]{3}[-/]?\d{2,4}\b/);
  return match ? match[0] : value;
}

function formatWeight(value) {
  if (value === null || value === undefined || value === "") return "—";
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric.toLocaleString() : value;
}

export default function PreviewTable({ records = [] }) {
  const columns = [
    "Slip No",
    "Party Name",
    "Vehicle No",
    "Product",
    "1st Weight",
    "2nd Weight",
    "Net Weight",
    "Date",
  ];

  return (
    <section
      style={{
        marginTop: "18px",
        background: "#1e293b",
        borderRadius: "12px",
        border: "1px solid #334155",
        overflow: "hidden",
      }}
    >
      <div style={{ padding: "18px 20px" }}>
        <h3 style={{ margin: 0 }}>Extracted Data Preview</h3>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            minWidth: "950px",
          }}
        >
          <thead>
            <tr style={{ background: "#172033" }}>
              {columns.map((column) => (
                <th
                  key={column}
                  style={{
                    padding: "14px",
                    textAlign: "left",
                    borderTop: "1px solid #334155",
                    borderBottom: "1px solid #334155",
                  }}
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {!records.length ? (
              <tr>
                <td
                  colSpan={columns.length}
                  style={{
                    textAlign: "center",
                    padding: "35px",
                    color: "#94a3b8",
                  }}
                >
                  No weight slips processed yet.
                </td>
              </tr>
            ) : (
              records.map((record) => {
                const duplicateStyle = record.duplicate
                  ? { background: "rgba(245, 158, 11, 0.18)" }
                  : {};

                return (
                  <tr
                    key={record.id}
                    style={{ borderBottom: "1px solid #334155", ...duplicateStyle }}
                  >
                    <td
                      style={{
                        padding: "12px",
                        fontWeight: record.duplicate ? 800 : 400,
                        color: record.duplicate ? "#fbbf24" : "inherit",
                      }}
                      title={record.duplicate ? "Repeated weight slip number" : undefined}
                    >
                      {record.slip_no || "—"}
                      {record.duplicate ? "  ⚠" : ""}
                    </td>
                    <td style={{ padding: "12px" }}>{record.party || "—"}</td>
                    <td style={{ padding: "12px" }}>{record.vehicle_no || "—"}</td>
                    <td style={{ padding: "12px" }}>{record.product || "—"}</td>
                    <td style={{ padding: "12px" }}>{formatWeight(record.first_weight)}</td>
                    <td style={{ padding: "12px" }}>{formatWeight(record.second_weight)}</td>
                    <td style={{ padding: "12px", fontWeight: 700 }}>{formatWeight(record.net_weight)}</td>
                    <td style={{ padding: "12px" }}>{displayDate(record)}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
