import { useState, useRef, useCallback, useEffect } from "react";
import { postChat, getSuggestedQuestions } from "@/lib/api";

// Shape of a single chat message stored in the frontend state
type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  state?: string;
  evidence?: { source_id: string; snippet: string; score: number } | null;
};

// Return type of the useChat hook so pages know what state and actions are available
type UseChatReturn = {
  messages: Message[];
  input: string;
  setInput: (value: string) => void;
  sessionId: string;
  loading: boolean;
  error: string | null;
  bottomRef: React.RefObject<HTMLDivElement>;
  send: (content: string) => Promise<void>;
  reset: () => void;
  suggestedQuestions: string[];
};

// Custom hook that owns all chat state, API calls, and auto-scroll behavior
export const useChat = (initialSessionId?: string): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(
    () => initialSessionId || crypto.randomUUID(),
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getSuggestedQuestions().then(({ data, error: fetchError }) => {
      if (fetchError || !data) {
        return;
      }
      setSuggestedQuestions(data);
    });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(
    async (content: string) => {
      if (!content.trim() || loading) return;

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: content.trim(),
      };

      setMessages((m) => [...m, userMessage]);
      setInput("");
      setLoading(true);
      setError(null);

      try {
        const { data, error: apiError } = await postChat({
          messages: [{ role: "user", content: userMessage.content }],
          session_id: sessionId,
        });

        if (apiError || !data) {
          throw new Error(apiError || "Unknown API error");
        }

        setSessionId(data.session_id);
        setSuggestedQuestions(data.suggested_questions || []);
        setMessages((m) => [
          ...m,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: data.message.content,
            state: data.state,
            evidence: data.evidence,
          },
        ]);
      } catch (err) {
        const message =
          err instanceof Error ?
            err.message
          : "Something went wrong. Please try again later.";
        setError(message);
        setMessages((m) => [
          ...m,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: "Something went wrong. Please try again later.",
          },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [loading, sessionId],
  );

  const reset = useCallback(() => {
    setMessages([]);
    setInput("");
    setSessionId(crypto.randomUUID());
    setLoading(false);
    setError(null);
    setSuggestedQuestions([]);
  }, []);

  return {
    messages,
    input,
    setInput,
    sessionId,
    loading,
    error,
    bottomRef,
    send,
    reset,
    suggestedQuestions,
  };
};
