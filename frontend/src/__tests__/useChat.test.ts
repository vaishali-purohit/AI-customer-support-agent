import { renderHook, act, waitFor } from "@testing-library/react";
import { useChat } from "@/hooks/useChat";

jest.mock("@/lib/api", () => ({
  postChat: jest.fn(),
  getSuggestedQuestions: jest.fn(),
}));

import { postChat, getSuggestedQuestions } from "@/lib/api";

const mockedPostChat = postChat as jest.MockedFunction<typeof postChat>;
const mockedGetSuggestedQuestions =
  getSuggestedQuestions as jest.MockedFunction<typeof getSuggestedQuestions>;

describe("useChat", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedGetSuggestedQuestions.mockResolvedValue({
      data: ["Question 1", "Question 2"],
      error: null,
    });
  });

  it("initializes with empty messages and input", async () => {
    const { result } = renderHook(() => useChat());

    expect(result.current.messages).toEqual([]);
    expect(result.current.input).toBe("");
    expect(result.current.loading).toBe(false);

    await waitFor(() => {
      expect(result.current.suggestedQuestions).toEqual([
        "Question 1",
        "Question 2",
      ]);
    });
  });

  it("updates input via setInput", () => {
    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.setInput("hello");
    });

    expect(result.current.input).toBe("hello");
  });

  it("skips sending empty or whitespace-only content", async () => {
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.send("   ");
    });

    expect(mockedPostChat).not.toHaveBeenCalled();
    expect(result.current.messages).toEqual([]);
  });

  it("sends a message and appends assistant response", async () => {
    mockedPostChat.mockResolvedValue({
      data: {
        session_id: "session-123",
        message: { role: "assistant", content: "Here is the answer" },
        state: "ready_to_answer",
        evidence: null,
        tool_calls: [],
        suggested_questions: ["Follow-up 1"],
      },
      error: null,
    });

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.send("What is the return policy?");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].content).toBe(
      "What is the return policy?",
    );
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[1].content).toBe("Here is the answer");
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.sessionId).toBe("session-123");
    expect(result.current.suggestedQuestions).toEqual(["Follow-up 1"]);
  });

  it("appends error message when API call fails", async () => {
    mockedPostChat.mockResolvedValue({
      data: null,
      error: "API error 500: Server error",
    });

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.send("Hello");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].content).toBe(
      "Something went wrong. Please try again later.",
    );
    expect(result.current.error).toBe("API error 500: Server error");
  });

  it("appends error message when API throws", async () => {
    mockedPostChat.mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.send("Hello");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].content).toBe(
      "Something went wrong. Please try again later.",
    );
    expect(result.current.error).toBe("Network error");
  });

  it("resets all state", async () => {
    mockedPostChat.mockResolvedValue({
      data: {
        session_id: "session-123",
        message: { role: "assistant", content: "Answer" },
        state: "ready_to_answer",
        evidence: null,
        tool_calls: [],
        suggested_questions: [],
      },
      error: null,
    });

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.send("Hello");
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.input).toBe("");
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.suggestedQuestions).toEqual([]);
  });
});
