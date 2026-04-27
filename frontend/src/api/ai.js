export async function fetchAIInterpretation(resultData) {
  const response = await fetch("http://127.0.0.1:5000/api/ai/interpret", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(resultData),
  });

  if (!response.ok) {
    throw new Error("AI 해석 요청 실패");
  }

  const json = await response.json();
  return json.data;
}


export async function fetchRagAI(ragData) {
  const response = await fetch("http://127.0.0.1:5000/api/ai/rag", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ragData),
  });

  if (!response.ok) {
    throw new Error("RAG AI 요청 실패");
  }

  const json = await response.json();
  return json.data;
}