import { render, screen } from "@testing-library/react";
import { MessageBubble } from "@/components/MessageBubble";

describe("MessageBubble", () => {
  it("renders message content", () => {
    render(
      <MessageBubble message={{ id: "1", role: "user", content: "Hello!" }} />,
    );

    expect(screen.getByText("Hello!")).toBeInTheDocument();
  });

  it("aligns user messages to the right", () => {
    const { container } = render(
      <MessageBubble message={{ id: "1", role: "user", content: "Hello!" }} />,
    );

    expect(container.firstChild).toHaveClass("justify-end");
  });

  it("aligns assistant messages to the left", () => {
    const { container } = render(
      <MessageBubble
        message={{ id: "2", role: "assistant", content: "Hi there!" }}
      />,
    );

    expect(container.firstChild).toHaveClass("justify-start");
  });

  it("applies black background and white text for user messages", () => {
    const { container } = render(
      <MessageBubble message={{ id: "1", role: "user", content: "Hello!" }} />,
    );

    expect(container.firstChild?.firstChild).toHaveClass(
      "bg-black",
      "text-white",
    );
  });

  it("shows state badge for assistant messages when state is not ready_to_answer", () => {
    render(
      <MessageBubble
        message={{
          id: "2",
          role: "assistant",
          content: "Answer",
          state: "needs_verification",
        }}
      />,
    );

    expect(screen.getByText("NEEDS VERIFICATION")).toBeInTheDocument();
  });

  it("does not show state badge when assistant state is ready_to_answer", () => {
    render(
      <MessageBubble
        message={{
          id: "2",
          role: "assistant",
          content: "Answer",
          state: "ready_to_answer",
        }}
      />,
    );

    expect(screen.queryByText("READY TO ANSWER")).not.toBeInTheDocument();
  });

  it("shows evidence for assistant messages when evidence exists", () => {
    render(
      <MessageBubble
        message={{
          id: "2",
          role: "assistant",
          content: "Answer",
          evidence: { source_id: "KB-1", snippet: "Snippet", score: 0.9 },
        }}
      />,
    );

    expect(screen.getByText("Source: KB-1")).toBeInTheDocument();
    expect(screen.getByText("Snippet")).toBeInTheDocument();
  });

  it("does not show evidence for user messages", () => {
    render(
      <MessageBubble
        message={{
          id: "1",
          role: "user",
          content: "Question?",
          evidence: { source_id: "KB-1", snippet: "Snippet", score: 0.9 },
        }}
      />,
    );

    expect(screen.queryByText("Source: KB-1")).not.toBeInTheDocument();
  });
});
