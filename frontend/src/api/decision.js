const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class DecisionAPI {
  static async startDecision(decision, conversationId) {
    const response = await fetch(`${API_BASE}/api/decision/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, conversation_id: conversationId })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start decision');
    }
    return response.json();
  }

  static async submitAnswer(conversationId, answer, questionIndex) {
    const response = await fetch(`${API_BASE}/api/decision/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: conversationId,
        answer,
        question_index: questionIndex
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit answer');
    }
    return response.json();
  }

  static async analyzeDecision(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/decision/analyze?conversation_id=${conversationId}`,
      { method: 'POST' }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze decision');
    }
    return response.json();
  }
}