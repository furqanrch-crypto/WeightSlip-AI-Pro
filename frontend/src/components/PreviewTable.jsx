export default function PreviewTable({ records = [] }) {
  const columns = [
    "Slip No",
    "Vehicle",
    "Party",
    "Product",
    "1st Weight",
    "2nd Weight",
    "Net Weight",
    "Status",
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
              records.map((record) => (
                <tr key={record.id} style={{ borderBottom: "1px solid #334155" }}>
                  <td style={{ padding: "12px" }}>{record.slip_no || "—"}</td>
                  <td style={{ padding: "12px" }}>{record.vehicle_no || "—"}</td>
                  <td style={{ padding: "12px" }}>{record.party || "—"}</td>
                  <td style={{ padding: "12px" }}>{record.product || "—"}</td>
                  <td style={{ padding: "12px" }}>{record.first_weight?.toLocaleString?.() || record.first_weight || "—"}</td>
                  <td style={{ padding: "12px" }}>{record.second_weight?.toLocaleString?.() || record.second_weight || "—"}</td>
                  <td style={{ padding: "12px", fontWeight: 700 }}>{record.net_weight?.toLocaleString?.() || record.net_weight || "—"}</td>
                  <td style={{ padding: "12px" }}>
                    {record.duplicate ? "Duplicate" : record.processing_status}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
