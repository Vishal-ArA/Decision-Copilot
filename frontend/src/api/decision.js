const API_BASE = import.meta.env.VITE_API_URL;

if (!API_BASE) {
  throw new Error(
    "VITE_API_URL is not defined. Please set it in your environment variables."
  );
}

export class DecisionAPI {
  // START the conversation (first message only)
  static async startDecision(decision, conversationId) {
    const response = await fetch(`${API_BASE}/api/decision/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        decision,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      let errorMessage = "Failed to start decision";
      try {
        const error = await response.json();
        errorMessage = error.detail || errorMessage;
      } catch (_) {}
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // ANSWER a follow-up question (all subsequent messages)
  static async submitAnswer(conversationId, answer, questionIndex) {
    const response = await fetch(`${API_BASE}/api/decision/answer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        answer,
        question_index: questionIndex,
      }),
    });

    if (!response.ok) {
      let errorMessage = "Failed to submit answer";
      try {
        const error = await response.json();
        errorMessage = error.detail || errorMessage;
      } catch (_) {}
      throw new Error(errorMessage);
    }

    return response.json();
  }
}
