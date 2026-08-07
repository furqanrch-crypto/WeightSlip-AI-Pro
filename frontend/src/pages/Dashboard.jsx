import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import UploadPanel from "../components/UploadPanel";
import StatsCards from "../components/StatsCards";
import ProgressBar from "../components/ProgressBar";
import PreviewTable from "../components/PreviewTable";
import ImagePreview from "../components/ImagePreview";
import useImageUpload from "../hooks/useImageUpload";

export default function Dashboard() {
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

          <PreviewTable records={records} />
        </main>
      </div>
    </div>
  );
}
