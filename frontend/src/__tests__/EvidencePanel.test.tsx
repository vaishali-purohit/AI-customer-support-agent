import { render, screen } from "@testing-library/react";
import { EvidencePanel } from "@/components/EvidencePanel";

describe("EvidencePanel", () => {
  it("renders source id and snippet", () => {
    render(<EvidencePanel source_id="KB-42" snippet="Sample snippet text" />);

    expect(screen.getByText("Source: KB-42")).toBeInTheDocument();
    expect(screen.getByText("Sample snippet text")).toBeInTheDocument();
  });

  it("truncates snippet to 300 characters", () => {
    const longSnippet = "a".repeat(500);
    render(<EvidencePanel source_id="KB-1" snippet={longSnippet} />);

    expect(screen.getByText("a".repeat(300))).toBeInTheDocument();
    expect(screen.queryByText("a".repeat(301))).not.toBeInTheDocument();
  });
});
