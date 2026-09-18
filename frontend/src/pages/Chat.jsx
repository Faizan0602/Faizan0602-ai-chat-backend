import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { logout, refreshAccessToken } from "../api";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || fallback;

export default function Chat() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);
  const abortRef = useRef(null);
  const assistantTextRef = useRef("");
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    const loadConversations = async () => {
      try {
        const response = await api.get("/chat/conversations");
        if (!isMounted) return;
        setConversations(response.data);
        if (response.data.length > 0) {
          setIsLoadingMessages(true);
          setActiveId(response.data[0].id);
        }
      } catch (requestError) {
        if (isMounted) setError(getErrorMessage(requestError, "Could not load conversations."));
      } finally {
        if (isMounted) setIsLoadingConversations(false);
      }
    };

    loadConversations();
    return () => {
      isMounted = false;
      abortRef.current?.abort();
    };
  }, []);

  useEffect(() => {
    if (!activeId) {
      return undefined;
    }

    let isMounted = true;

    api.get(`/chat/conversations/${activeId}/messages`)
      .then((response) => {
        if (isMounted) setMessages(response.data);
      })
      .catch((requestError) => {
        if (isMounted) setError(getErrorMessage(requestError, "Could not load this conversation."));
      })
      .finally(() => {
        if (isMounted) setIsLoadingMessages(false);
      });

    return () => {
      isMounted = false;
    };
  }, [activeId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const createConversation = async () => {
    setError("");
    try {
      const response = await api.post("/chat/conversations", { title: "New Conversation" });
      setConversations((current) => [response.data, ...current]);
      setIsLoadingMessages(true);
      setActiveId(response.data.id);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not create a conversation."));
    }
  };

  const streamResponse = async (conversationId, content, retry = true) => {
    const controller = new AbortController();
    abortRef.current = controller;
    const response = await fetch(`${api.defaults.baseURL}/chat/conversations/${conversationId}/messages`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ content }),
      signal: controller.signal,
    });

    if (response.status === 401 && retry) {
      try {
        await refreshAccessToken();
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.assign("/login");
        throw refreshError;
      }
      return streamResponse(conversationId, content, false);
    }
    if (!response.ok) {
      throw new Error(response.status === 401 ? "Your session has expired." : "The assistant could not respond.");
    }
    if (!response.body) throw new Error("The assistant returned an empty response.");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let bufferedText = "";
    assistantTextRef.current = "";

    while (true) {
      const { done, value } = await reader.read();
      bufferedText += decoder.decode(value || new Uint8Array(), { stream: !done });

      const events = bufferedText.split("\n\n");
      bufferedText = events.pop() || "";
      for (const event of events) {
        const data = event
          .split("\n")
          .filter((line) => line.startsWith("data:"))
          .map((line) => line.slice(5).trimStart())
          .join("\n");

        if (!data || data === "[DONE]") continue;
        assistantTextRef.current += JSON.parse(data);
        setMessages((current) => current.map((message) =>
          message.id === "streaming" ? { ...message, content: assistantTextRef.current } : message,
        ));
      }

      if (done) break;
    }
    setMessages((current) => current.map((message) =>
      message.id === "streaming" ? { ...message, content: assistantTextRef.current, id: `assistant-${Date.now()}` } : message,
    ));
  };

  const sendMessage = async (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content || !activeId || isStreaming) return;

    setDraft("");
    setError("");
    setIsStreaming(true);
    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", content },
      { id: "streaming", role: "assistant", content: "" },
    ]);

    try {
      await streamResponse(activeId, content);
    } catch (requestError) {
      if (requestError.name !== "AbortError") {
        setError(requestError.message || "The assistant could not respond.");
        setMessages((current) => current.filter((message) => message.id !== "streaming"));
      }
    } finally {
      abortRef.current = null;
      setIsStreaming(false);
    }
  };

  const handleLogout = async () => {
    abortRef.current?.abort();
    await logout();
    navigate("/login");
  };

  const selectConversation = (conversationId) => {
    setMessages([]);
    setIsLoadingMessages(true);
    setError("");
    setActiveId(conversationId);
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-white text-slate-800">
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 font-['Space_Grotesk'] font-bold text-white">O</div>
          <span className="font-['Space_Grotesk'] text-lg font-bold tracking-tight text-slate-900">Orbit Chat</span>
        </div>
        <button onClick={handleLogout} className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-900">Log out</button>
      </header>
      <div className="flex min-h-0 flex-1">
        <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-slate-50/80 p-3 max-sm:w-20 max-sm:px-2">
          <button onClick={createConversation} disabled={isLoadingConversations} className="mb-4 flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-60 max-sm:px-2"><span className="text-lg leading-none">+</span><span className="max-sm:hidden">New Chat</span></button>
          <p className="mb-2 px-2 text-xs font-bold uppercase tracking-wider text-slate-400 max-sm:hidden">Conversations</p>
          <div className="space-y-1 overflow-y-auto">
            {isLoadingConversations && <p className="px-2 py-3 text-sm text-slate-400 max-sm:hidden">Loading...</p>}
            {!isLoadingConversations && conversations.length === 0 && <p className="px-2 py-3 text-sm text-slate-400 max-sm:hidden">No chats yet.</p>}
            {conversations.map((conversation) => (
              <button key={conversation.id} onClick={() => selectConversation(conversation.id)} className={`w-full truncate rounded-lg px-3 py-2.5 text-left text-sm transition max-sm:px-2 ${activeId === conversation.id ? "bg-indigo-100 font-semibold text-indigo-800" : "text-slate-600 hover:bg-slate-200/80"}`} title={conversation.title}>{conversation.title}</button>
            ))}
          </div>
        </aside>
        <main className="flex min-w-0 flex-1 flex-col bg-white">
          <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-10">
            <div className="mx-auto flex max-w-3xl flex-col gap-5">
              {!activeId && !isLoadingConversations && <div className="flex flex-1 flex-col items-center justify-center py-32 text-center"><h1 className="font-['Space_Grotesk'] text-3xl font-bold text-slate-900">Start a new conversation</h1><p className="mt-2 text-slate-500">Create a chat from the sidebar and ask anything.</p></div>}
              {isLoadingMessages && <p className="text-center text-sm text-slate-400">Loading messages...</p>}
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 sm:max-w-[72%] ${message.role === "user" ? "rounded-br-md bg-indigo-600 text-white" : "rounded-bl-md bg-slate-100 text-slate-700"}`}>
                    {message.content || (isStreaming && message.id === "streaming" ? <span className="inline-flex gap-1 py-1"><i className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" /><i className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:120ms]" /><i className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:240ms]" /></span> : "")}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
          <div className="border-t border-slate-200 bg-white p-4 sm:px-10">
            <div className="mx-auto max-w-3xl">
              {error && <p role="alert" className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
              <form onSubmit={sendMessage} className="flex items-end gap-2 rounded-xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-100">
                <textarea value={draft} onChange={(event) => setDraft(event.target.value)} disabled={!activeId || isStreaming} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(event); } }} rows={1} placeholder={activeId ? "Message Orbit..." : "Create a chat to begin"} className="max-h-32 min-h-10 flex-1 resize-none border-0 bg-transparent px-2 py-2 text-sm outline-none placeholder:text-slate-400 disabled:cursor-not-allowed" />
                <button disabled={!draft.trim() || !activeId || isStreaming} type="submit" className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50">{isStreaming ? "..." : "Send"}</button>
              </form>
              <p className="mt-2 text-center text-xs text-slate-400">Orbit can make mistakes. Check important information.</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
