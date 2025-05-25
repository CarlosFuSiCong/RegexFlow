"use client";

import { useState, useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type ChatMessage = {
  role: "user" | "bot";
  text: string;
};

export default function ChatBot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    setMessages([{ role: "bot", text: "Hi! How can I help you today?" }]);
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg: ChatMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    const inputCopy = input;
    setInput("");
    setTimeout(() => {
      const botReply: ChatMessage = {
        role: "bot",
        text: `You said: "${inputCopy}"`,
      };
      setMessages((prev) => [...prev, botReply]);
    }, 500);
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-lg font-semibold mb-2">RegexFlow Assistant</h2>

      <ScrollArea className="flex-1 mb-3 pr-2">
        <div className="space-y-2 text-sm">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`inline-block px-3 py-2 rounded-md max-w-[70%] break-words ${
                  msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="flex gap-2">
        <Input
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <Button onClick={handleSend}>Send</Button>
      </div>
    </div>
  );
}
