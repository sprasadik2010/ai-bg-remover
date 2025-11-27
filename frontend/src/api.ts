// const API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = "https://ai-bg-remover-tbyy.onrender.com";

export const removeBG = async (file: File): Promise<string> => {
  const formData = new FormData();
  formData.append("image", file);

  const response = await fetch(`${API_BASE_URL}/remove-bg/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to remove background");
  }

  // Convert the blob to a data URL
  const blob = await response.blob();
  return URL.createObjectURL(blob);
};

export const replaceBG = async (foreground: File, background: File): Promise<string> => {
  const formData = new FormData();
  formData.append("foreground", foreground);
  formData.append("background", background);

  const response = await fetch(`${API_BASE_URL}/replace-bg/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to replace background");
  }

  // Convert the blob to a data URL
  const blob = await response.blob();
  return URL.createObjectURL(blob);
};