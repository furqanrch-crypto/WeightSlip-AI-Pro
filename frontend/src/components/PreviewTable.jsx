export default function PreviewTable() {
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
          </tbody>
        </table>
      </div>
    </section>
  );
}