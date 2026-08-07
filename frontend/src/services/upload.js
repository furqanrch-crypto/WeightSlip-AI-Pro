import api from "./api";

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/api/upload", formData);
  return response.data;
}

export async function getRecord(recordId) {
  const response = await api.get(`/api/records/${recordId}`);
  return response.data.record;
}
