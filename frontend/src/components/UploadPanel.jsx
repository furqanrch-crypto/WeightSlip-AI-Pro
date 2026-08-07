import { useRef } from "react";
import { useDropzone } from "react-dropzone";

export default function UploadPanel({ onImagesSelected }) {
  const folderInputRef = useRef(null);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    accept: {
      "image/*": [".jpg", ".jpeg", ".png", ".webp", ".bmp"],
    },
    multiple: true,
    noClick: true,
    onDrop: onImagesSelected,
  });

  const handleFolderSelect = (event) => {
    onImagesSelected(event.target.files);
    event.target.value = "";
  };

  return (
    <section
      style={{
        background: "#1e293b",
        borderRadius: "14px",
        padding: "28px",
        border: "1px solid #334155",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Upload Weight Slips</h3>

      <div
        {...getRootProps()}
        style={{
          border: isDragActive
            ? "2px dashed #3b82f6"
            : "2px dashed #475569",
          borderRadius: "12px",
          padding: "45px 20px",
          textAlign: "center",
          background: isDragActive ? "#172554" : "transparent",
          color: "#cbd5e1",
          transition: "0.2s",
        }}
      >
        <input {...getInputProps()} />

        <input
          ref={folderInputRef}
          type="file"
          accept="image/*"
          multiple
          webkitdirectory=""
          directory=""
          onChange={handleFolderSelect}
          style={{ display: "none" }}
        />

        <div style={{ fontSize: "42px" }}>📤</div>

        <h3>
          {isDragActive
            ? "Drop images now"
            : "Drop weight slip images here"}
        </h3>

        <p>JPG, PNG, WEBP or BMP</p>

        <div
          style={{
            display: "flex",
            gap: "12px",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <button
            className="upload-btn"
            type="button"
            onClick={open}
          >
            📂 Select Images
          </button>

          <button
            className="upload-btn"
            type="button"
            onClick={() => folderInputRef.current?.click()}
          >
            📁 Select Folder
          </button>
        </div>
      </div>
    </section>
  );
}