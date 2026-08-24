// Maps agent states to Tailwind classes so status badges are visually distinct
const STATE_STYLES: Record<string, string> = {
  escalated: "bg-red-100 text-red-700",
  verified: "bg-green-100 text-green-700",
  needs_verification: "bg-yellow-100 text-yellow-700",
  failed_safe: "bg-orange-100 text-orange-700",
};

type StateBadgeProps = {
  state: string;
};

// Renders a small colored badge showing the current agent state above assistant messages
export const StateBadge = ({ state }: StateBadgeProps) => {
  const style = STATE_STYLES[state] || "bg-black/10 text-black/70";

  return (
    <span
      className={`mb-2 inline-block rounded px-2 py-0.5 text-xs font-medium ${style}`}
    >
      {state.replace(/_/g, " ").toUpperCase()}
    </span>
  );
};
