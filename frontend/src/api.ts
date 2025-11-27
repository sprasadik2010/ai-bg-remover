export interface ApiResponse {
  output_url: string;
}

export async function removeBG(file: File): Promise<ApiResponse> {
  const formData = new FormData();
  formData.append("image", file);

  const res = await fetch("https://ai-bg-remover-tbyy.onrender.com/remove-bg/", {
    method: "POST",
    body: formData,
  });

  return res.json();
}

export async function replaceBG(
  foreground: File,
  background: File
): Promise<ApiResponse> {
  const formData = new FormData();
  formData.append("foreground", foreground);
  formData.append("background", background);

  const res = await fetch("https://ai-bg-remover-tbyy.onrender.com/replace-bg/", {
    method: "POST",
    body: formData,
  });

  return res.json();
}
