"use client";

import { useChat } from "@/hooks/useChat";
import { MessageBubble } from "@/components/MessageBubble";
import { ChatInput } from "@/components/ChatInput";

// Main chat page that composes the header, message list, suggested questions, and input
const ChatPage = () => {
  const {
    messages,
    input,
    setInput,
    loading,
    send,
    bottomRef,
    suggestedQuestions,
  } = useChat();

  return (
    <div className="flex h-screen w-full flex-col">
      <header className="border-b border-black/10 px-6 py-4">
        <h1 className="text-lg font-semibold">Sunnystep Support</h1>
      </header>
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-2xl space-y-4">
          {messages.length === 0 && (
            <div className="rounded-lg border border-black/10 p-4 text-sm text-black/70">
              Ask about returns, shipping, products, or your order.
            </div>
          )}
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} />
          ))}
          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question) => (
                <button
                  key={question}
                  onClick={() => send(question)}
                  className="rounded-full border border-black/10 px-3 py-1.5 text-xs text-black/70 hover:bg-black/5 disabled:opacity-50"
                  disabled={loading}
                >
                  {question}
                </button>
              ))}
            </div>
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-black/5 px-4 py-3 text-sm">…</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </main>
      <div className="border-t border-black/10 px-4 py-3">
        <ChatInput
          value={input}
          onChange={setInput}
          onSubmit={() => send(input)}
          disabled={loading}
        />
      </div>
    </div>
  );
};
export default ChatPage;
