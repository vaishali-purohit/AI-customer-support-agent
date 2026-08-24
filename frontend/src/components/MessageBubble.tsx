import { StateBadge } from "@/components/StateBadge";
import { EvidencePanel } from "@/components/EvidencePanel";
import type { Message } from "@/lib/types";

type MessageBubbleProps = {
  message: Message;
};

// Renders a single chat bubble, user messages on the right and assistant messages on the left
export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser ? "bg-black text-white" : "bg-black/5"
        }`}
      >
        {!isUser && message.state && message.state !== "ready_to_answer" && (
          <StateBadge state={message.state} />
        )}
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.evidence && (
          <details className="mt-3">
            <summary className="cursor-pointer text-xs font-medium opacity-80">
              Evidence
            </summary>
            <EvidencePanel
              source_id={message.evidence.source_id}
              snippet={message.evidence.snippet}
            />
          </details>
        )}
      </div>
    </div>
  );
};
