import api from "./api";

export async function downloadExcelReport(recordIds) {
  const response = await api.post(
    "/api/export/excel",
    { record_ids: recordIds },
    { responseType: "blob" }
  );

  const disposition = response.headers["content-disposition"] || "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  const filename = match?.[1] || "WeightSlip_Report.xlsx";

  const url = URL.createObjectURL(response.data);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
