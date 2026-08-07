import { useCallback, useState } from "react";

async function getFileHash(file) {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);

  const hashArray = Array.from(new Uint8Array(hashBuffer));

  return hashArray
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export default function useImageUpload() {
  const [images, setImages] = useState([]);
  const [duplicateCount, setDuplicateCount] = useState(0);
  const [isCheckingDuplicates, setIsCheckingDuplicates] = useState(false);

  const addImages = useCallback(
    async (files) => {
      const imageFiles = Array.from(files).filter((file) =>
        file.type.startsWith("image/")
      );

      if (!imageFiles.length) return;

      setIsCheckingDuplicates(true);

      try {
        const existingHashes = new Set(
          images.map((image) => image.hash)
        );

        const newImages = [];
        let duplicatesFound = 0;

        for (const file of imageFiles) {
          const hash = await getFileHash(file);

          if (existingHashes.has(hash)) {
            duplicatesFound += 1;
            continue;
          }

          existingHashes.add(hash);

          newImages.push({
            id: crypto.randomUUID(),
            file,
            hash,
            name: file.name,
            size: file.size,
            preview: URL.createObjectURL(file),
          });
        }

        setImages((current) => [...current, ...newImages]);

        if (duplicatesFound > 0) {
          setDuplicateCount(
            (current) => current + duplicatesFound
          );
        }
      } finally {
        setIsCheckingDuplicates(false);
      }
    },
    [images]
  );

  const removeImage = useCallback((id) => {
    setImages((current) => {
      const selectedImage = current.find(
        (image) => image.id === id
      );

      if (selectedImage) {
        URL.revokeObjectURL(selectedImage.preview);
      }

      return current.filter((image) => image.id !== id);
    });
  }, []);

  const clearImages = useCallback(() => {
    setImages((current) => {
      current.forEach((image) => {
        URL.revokeObjectURL(image.preview);
      });

      return [];
    });

    setDuplicateCount(0);
  }, []);

  return {
    images,
    addImages,
    removeImage,
    clearImages,
    imageCount: images.length,
    duplicateCount,
    isCheckingDuplicates,
  };
}