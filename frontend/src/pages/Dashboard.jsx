import { useState } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import UploadPanel from "../components/UploadPanel";
import StatsCards from "../components/StatsCards";
import ProgressBar from "../components/ProgressBar";
import PreviewTable from "../components/PreviewTable";
import ImagePreview from "../components/ImagePreview";
import useImageUpload from "../hooks/useImageUpload";
import { downloadExcelReport } from "../services/export";

export default function Dashboard() {
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  const {
    images,
    records,
    addImages,
    removeImage,
    clearImages,
    imageCount,
    ocrCompleted,
    duplicateCount,
    netWeight,
    overallProgress,
  } = useImageUpload();

  const exportableRecords = records.filter(
    (record) => record?.id && !["queued", "preprocessing", "ocr", "ocr_retry", "parsing"].includes(record.processing_status)
  );

  const handleExcelDownload = async () => {
    if (!exportableRecords.length) return;

    try {
      setExporting(true);
      setExportError("");
      await downloadExcelReport(exportableRecords.map((record) => record.id));
    } catch (error) {
      setExportError(
        error.response?.data?.detail || error.message || "Unable to download Excel report."
      );
    } finally {
      setExporting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f172a",
        color: "white",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <Header />

      <div style={{ display: "flex" }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: "28px",
            minWidth: 0,
          }}
        >
          <UploadPanel onImagesSelected={addImages} />

          <StatsCards
            imageCount={imageCount}
            ocrCompleted={ocrCompleted}
            netWeight={netWeight}
            duplicates={duplicateCount}
          />

          <ImagePreview
            images={images}
            onRemove={removeImage}
            onClear={clearImages}
          />

          <ProgressBar progress={overallProgress} />

          <div
            style={{
              marginTop: "18px",
              display: "flex",
              justifyContent: "flex-end",
              alignItems: "center",
              gap: "12px",
            }}
          >
            {exportError && (
              <span style={{ color: "#fca5a5", fontSize: "14px" }}>
                {exportError}
              </span>
            )}

            <button
              type="button"
              onClick={handleExcelDownload}
              disabled={!exportableRecords.length || exporting}
              style={{
                background: exportableRecords.length ? "#16a34a" : "#475569",
                color: "white",
                border: 0,
                borderRadius: "8px",
                padding: "11px 18px",
                fontSize: "15px",
                fontWeight: 700,
                cursor: exportableRecords.length && !exporting ? "pointer" : "not-allowed",
              }}
            >
              {exporting
                ? "Preparing Excel..."
                : `Download Excel (${exportableRecords.length})`}
            </button>
          </div>

          <PreviewTable records={records} />
        </main>
      </div>
    </div>
  );
}
