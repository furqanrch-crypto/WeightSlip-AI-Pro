import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import UploadPanel from "../components/UploadPanel";
import StatsCards from "../components/StatsCards";
import ProgressBar from "../components/ProgressBar";
import PreviewTable from "../components/PreviewTable";

export default function Dashboard() {
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
          <UploadPanel />
          <StatsCards />
          <ProgressBar />
          <PreviewTable />
        </main>
      </div>
    </div>
  );
}