"use client";

import { useState, useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  generateRegexTasks,
  previewReplace,
  replaceTasks,
} from "@/services/regexApi";

import type {
  BackendRegexTask,
  GenerateTasksRequest,
  GenerateTasksResponse,
  PreviewReplaceRequest,
  PreviewReplaceResponse,
  ReplaceTasksRequest,
  ReplaceTasksResponse,
} from "@/types/api";

type ChatMessage = {
  role: "user" | "bot";
  text: string;
};

interface PreviewEntry {
  row: number;
  column: string;
  original: string;
  modified: string;
}

interface ChatBotProps {
  onDataChanged?: () => Promise<void>;
  onPreviewFull?: (entries: PreviewEntry[]) => void;
}

export default function ChatBot({ onDataChanged, onPreviewFull }: ChatBotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pendingTasks, setPendingTasks] = useState<BackendRegexTask[] | null>(null);
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    setMessages([{ role: "bot", text: "Hi! How can I help you today?" }]);
  }, []);

  const appendMessage = (msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleSend = async () => {
    const userInput = input.trim();
    if (!userInput) return;

    appendMessage({ role: "user", text: userInput });
    setInput("");

    // Handle confirmation step
    if (awaitingConfirmation && pendingTasks) {
      const confirm = userInput.toLowerCase();
      if (confirm === "yes" || confirm === "确认") {
        appendMessage({ role: "bot", text: "Proceeding with replacement…" });
        try {
          const replaceReq: ReplaceTasksRequest = { tasks: pendingTasks };
          const replaceRes: ReplaceTasksResponse = await replaceTasks(replaceReq);

          appendMessage({
            role: "bot",
            text: `✅ Replaced ${replaceRes.total_replacements} items successfully.`,
          });

          replaceRes.preview.slice(0, 10).forEach((entry) => {
            appendMessage({
              role: "bot",
              text: `Row ${entry.row}, Column ${entry.column}: "${entry.from}" → "${entry.to}"`,
            });
          });
          if (replaceRes.preview.length > 10) {
            appendMessage({
              role: "bot",
              text: `…and ${replaceRes.preview.length - 10} more updates not shown.`,
            });
          }

          appendMessage({ role: "bot", text: "Data has been updated. Refreshing table…" });

          onPreviewFull?.([]);
          if (onDataChanged) {
            await onDataChanged();
            appendMessage({ role: "bot", text: "Table refreshed. Let me know if you need anything else." });
          } else {
            appendMessage({ role: "bot", text: "If you want to see changes, please refresh the page." });
          }
        } catch (error) {
          appendMessage({ role: "bot", text: `⚠️ Replacement error: ${String(error)}` });
        }
      } else {
        appendMessage({ role: "bot", text: "Operation canceled. No changes were made." });
        onPreviewFull?.([]);
      }

      setPendingTasks(null);
      setAwaitingConfirmation(false);
      return;
    }

    // Normal flow: generate → preview → ask for confirmation
    appendMessage({ role: "bot", text: "Generating regex tasks…" });
    try {
      const genReq: GenerateTasksRequest = { description: userInput };
      const genRes: GenerateTasksResponse = await generateRegexTasks(genReq);

      if (!genRes.tasks?.length) {
        appendMessage({ role: "bot", text: "❌ Could not generate any tasks for that description." });
        return;
      }

      appendMessage({ role: "bot", text: "Previewing replacements…" });
      const previewReq: PreviewReplaceRequest = { tasks: genRes.tasks };
      const previewRes: PreviewReplaceResponse = await previewReplace(previewReq);

      appendMessage({
        role: "bot",
        text: `Found ${previewRes.total_matches} matches. Showing up to 10 previews:`,
      });

      previewRes.preview.slice(0, 10).forEach((entry) => {
        appendMessage({
          role: "bot",
          text: `Row ${entry.row}, Column ${entry.column}: "${entry.original}" → "${entry.modified}"`,
        });
      });
      if (previewRes.preview.length > 10) {
        appendMessage({
          role: "bot",
          text: `…and ${previewRes.preview.length - 10} more matches not shown.`,
        });
      }

      onPreviewFull?.(previewRes.preview);
      appendMessage({ role: "bot", text: "Do you want to apply these changes? (Yes/No)" });

      setPendingTasks(genRes.tasks);
      setAwaitingConfirmation(true);
    } catch (e) {
      appendMessage({ role: "bot", text: `⚠️ Error: ${String(e)}` });
    }
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-lg font-semibold mb-2">RegexFlow Assistant</h2>

      <ScrollArea className="flex-1 mb-3 pr-2">
        <div className="space-y-2 text-sm">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
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
          placeholder={
            awaitingConfirmation
              ? "Type Yes/No to confirm or cancel"
              : "Describe your regex replace request…"
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <Button onClick={handleSend}>Send</Button>
      </div>
    </div>
  );
}
