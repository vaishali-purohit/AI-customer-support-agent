import { render, screen, fireEvent } from "@testing-library/react";
import { ChatInput } from "@/components/ChatInput";

describe("ChatInput", () => {
  it("renders input and submit button", () => {
    render(
      <ChatInput
        value=""
        onChange={() => {}}
        onSubmit={() => {}}
        disabled={false}
      />,
    );

    expect(screen.getByPlaceholderText("Type a message…")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
  });

  it("calls onChange when typing", () => {
    const onChange = jest.fn();
    render(
      <ChatInput
        value=""
        onChange={onChange}
        onSubmit={() => {}}
        disabled={false}
      />,
    );

    fireEvent.change(screen.getByPlaceholderText("Type a message…"), {
      target: { value: "hello" },
    });

    expect(onChange).toHaveBeenCalledWith("hello");
  });

  it("calls onSubmit when form is submitted", () => {
    const onSubmit = jest.fn();
    render(
      <ChatInput
        value="hello"
        onChange={() => {}}
        onSubmit={onSubmit}
        disabled={false}
      />,
    );

    fireEvent.submit(
      screen.getByRole("button", { name: "Send" }).closest("form")!,
    );

    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it("disables input and button when disabled is true", () => {
    render(
      <ChatInput
        value="hello"
        onChange={() => {}}
        onSubmit={() => {}}
        disabled={true}
      />,
    );

    expect(screen.getByPlaceholderText("Type a message…")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  it("disables send button when value is empty", () => {
    render(
      <ChatInput
        value=""
        onChange={() => {}}
        onSubmit={() => {}}
        disabled={false}
      />,
    );

    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });
});
