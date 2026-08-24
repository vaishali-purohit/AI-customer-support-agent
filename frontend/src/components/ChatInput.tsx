type ChatInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
};

// Reusable text input and send button used at the bottom of the chat screen
export const ChatInput = ({
  value,
  onChange,
  onSubmit,
  disabled,
}: ChatInputProps) => {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="mx-auto max-w-2xl flex gap-2">
        <input
          className="flex-1 rounded-lg border border-black/10 px-3 py-2 text-sm outline-none"
          placeholder="Type a message…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          aria-label="Chat message input"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </form>
  );
};
