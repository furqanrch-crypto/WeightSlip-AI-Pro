import { useCallback, useMemo, useState } from "react";
import { getRecord, uploadImage } from "../services/upload";

const TERMINAL_STATUSES = new Set([
  "completed",
  "duplicate",
  "review_required",
  "failed",
]);

const STATUS_PROGRESS = {
  pending: 0,
  uploading: 5,
  queued: 10,
  preprocessing: 25,
  ocr: 55,
  ocr_retry: 65,
  parsing: 80,
  completed: 100,
  duplicate: 100,
  review_required: 100,
  failed: 100,
};

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function useImageUpload() {
  const [images, setImages] = useState([]);

  const updateImage = useCallback((localId, patch) => {
    setImages((current) =>
      current.map((image) =>
        image.id === localId ? { ...image, ...patch } : image
      )
    );
  }, []);

  const pollRecord = useCallback(
    async (localId, recordId) => {
      for (let attempt = 0; attempt < 180; attempt += 1) {
        await wait(1500);

        try {
          const record = await getRecord(recordId);
          updateImage(localId, {
            record,
            processingStatus: record.processing_status,
            progress: STATUS_PROGRESS[record.processing_status] ?? 10,
          });

          if (TERMINAL_STATUSES.has(record.processing_status)) {
            return;
          }
        } catch (error) {
          // A temporary gateway hiccup while OCR is CPU-heavy should not kill the
          // local card immediately. Retry polling a few times instead.
          if (attempt < 5) continue;

          updateImage(localId, {
            processingStatus: "failed",
            progress: 100,
            error: error.message,
          });
          return;
        }
      }

      updateImage(localId, {
        processingStatus: "failed",
        progress: 100,
        error: "OCR processing timed out.",
      });
    },
    [updateImage]
  );

  const uploadOnly = useCallback(
    async (image) => {
      try {
        updateImage(image.id, {
          processingStatus: "uploading",
          progress: 5,
          error: null,
        });

        const result = await uploadImage(image.file);

        updateImage(image.id, {
          databaseId: result.database_id,
          uploadResult: result,
          processingStatus: result.processing_status || "queued",
          progress: STATUS_PROGRESS[result.processing_status] ?? 10,
        });

        return { localId: image.id, recordId: result.database_id };
      } catch (error) {
        updateImage(image.id, {
          processingStatus: "failed",
          progress: 100,
          error: error.response?.data?.detail || error.message,
        });
        return null;
      }
    },
    [updateImage]
  );

  const addImages = useCallback(
    async (files) => {
      const imageFiles = Array.from(files).filter((file) =>
        file.type.startsWith("image/")
      );

      if (!imageFiles.length) return;

      const newImages = imageFiles.map((file) => ({
        id: crypto.randomUUID(),
        file,
        name: file.name,
        size: file.size,
        preview: URL.createObjectURL(file),
        processingStatus: "pending",
        progress: 0,
        record: null,
        error: null,
      }));

      setImages((current) => [...current, ...newImages]);

      // Queue all files first. Small pauses keep HTTP uploads gentle while the OCR
      // worker processes independently in the backend.
      const queued = [];
      for (const image of newImages) {
        const item = await uploadOnly(image);
        if (item) queued.push(item);
        await wait(150);
      }

      // Once every accepted file is safely queued, poll all records concurrently.
      await Promise.all(
        queued.map(({ localId, recordId }) => pollRecord(localId, recordId))
      );
    },
    [pollRecord, uploadOnly]
  );

  const removeImage = useCallback((id) => {
    setImages((current) => {
      const selectedImage = current.find((image) => image.id === id);
      if (selectedImage) URL.revokeObjectURL(selectedImage.preview);
      return current.filter((image) => image.id !== id);
    });
  }, []);

  const clearImages = useCallback(() => {
    setImages((current) => {
      current.forEach((image) => URL.revokeObjectURL(image.preview));
      return [];
    });
  }, []);

  const records = useMemo(
    () => images.map((image) => image.record).filter(Boolean),
    [images]
  );

  const completedCount = records.filter((record) =>
    TERMINAL_STATUSES.has(record.processing_status)
  ).length;

  const duplicateCount = records.filter((record) => record.duplicate).length;

  const netWeight = records
    .filter((record) => !record.duplicate && record.net_weight)
    .reduce((total, record) => total + Number(record.net_weight || 0), 0);

  const overallProgress = images.length
    ? Math.round(
        images.reduce((total, image) => total + (image.progress || 0), 0) /
          images.length
      )
    : 0;

  return {
    images,
    records,
    addImages,
    removeImage,
    clearImages,
    imageCount: images.length,
    ocrCompleted: completedCount,
    duplicateCount,
    netWeight,
    overallProgress,
  };
}
