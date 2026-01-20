import React, { useState, useEffect, useRef } from "react";
import { Brain, Send, Loader2, ChevronRight } from "lucide-react";
import { DecisionAPI } from "./api/decision";

const DecisionCopilot = () => {
  const [stage, setStage] = useState("welcome");
  const [decision, setDecision] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const conversationIdRef = useRef(crypto.randomUUID());
  const questionIndexRef = useRef(0);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // ================= START DECISION =================
  const startDecision = async () => {
    if (!decision.trim()) return;

    setIsLoading(true);
    setStage("clarifying");

    try {
      const res = await DecisionAPI.startDecision(
        decision,
        conversationIdRef.current
      );

      setMessages([
        {
          role: "assistant",
          content: res.question,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error(err);
      alert("Failed to start decision");
    } finally {
      setIsLoading(false);
    }
  };

  // ================= SEND ANSWER =================
  const handleSend = async () => {
    if (!input.trim()) return;

    const userAnswer = input;
    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userAnswer,
        timestamp: new Date().toISOString(),
      },
    ]);

    setIsLoading(true);

    try {
      const res = await DecisionAPI.submitAnswer(
        conversationIdRef.current,
        userAnswer,
        questionIndexRef.current
      );

      questionIndexRef.current += 1;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.question,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // ================= UI =================
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
      {stage === "welcome" && (
        <div className="bg-white max-w-xl w-full p-10 rounded-2xl shadow-xl border border-gray-200 text-center">
          <div className="w-14 h-14 bg-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Brain className="w-7 h-7 text-white" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            Decision Copilot
          </h1>

          <p className="text-gray-600 mb-6">
            An AI assistant to help you make confident, structured decisions.
          </p>

          <textarea
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            placeholder="Describe your decision here..."
            className="w-full h-32 p-4 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 resize-none mb-6"
          />

          <button
            onClick={startDecision}
            className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2"
          >
            Start Analysis
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}

      {stage === "clarifying" && (
        <div className="bg-white max-w-2xl w-full rounded-2xl shadow-xl border border-gray-200 flex flex-col h-[80vh]">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 text-white font-bold">
            Decision Conversation
          </div>

          <div className="flex-1 p-6 overflow-y-auto bg-gray-50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-4 ${
                  msg.role === "user" ? "text-right" : "text-left"
                }`}
              >
                <div
                  className={`inline-block max-w-[80%] px-5 py-3 rounded-2xl ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-white border border-gray-200 text-gray-900"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                Thinking...
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-200 p-4 flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type your answer..."
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl"
            />
            <button
              onClick={handleSend}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DecisionCopilot;
