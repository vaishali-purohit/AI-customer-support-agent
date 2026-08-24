import { render, screen } from "@testing-library/react";
import { StateBadge } from "@/components/StateBadge";

describe("StateBadge", () => {
  it("renders uppercase text with spaces instead of underscores", () => {
    render(<StateBadge state="needs_verification" />);

    expect(screen.getByText("NEEDS VERIFICATION")).toBeInTheDocument();
  });

  it("applies correct styles for known states", () => {
    const { rerender } = render(<StateBadge state="escalated" />);
    expect(screen.getByText("ESCALATED")).toHaveClass(
      "bg-red-100",
      "text-red-700",
    );

    rerender(<StateBadge state="verified" />);
    expect(screen.getByText("VERIFIED")).toHaveClass(
      "bg-green-100",
      "text-green-700",
    );

    rerender(<StateBadge state="needs_verification" />);
    expect(screen.getByText("NEEDS VERIFICATION")).toHaveClass(
      "bg-yellow-100",
      "text-yellow-700",
    );

    rerender(<StateBadge state="failed_safe" />);
    expect(screen.getByText("FAILED SAFE")).toHaveClass(
      "bg-orange-100",
      "text-orange-700",
    );
  });

  it("applies fallback styles for unknown states", () => {
    render(<StateBadge state="unknown_state" />);

    expect(screen.getByText("UNKNOWN STATE")).toHaveClass(
      "bg-black/10",
      "text-black/70",
    );
  });
});
