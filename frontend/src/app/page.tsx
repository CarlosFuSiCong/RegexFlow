"use client";

import { useState } from "react";
import ChatBot from "@/components/ChatBot";
import Navbar from "@/components/Navbar";
import DatasetTable from "@/components/DatasetTable";

export default function DatasetPage() {
  const [data, setData] = useState<(string | number | null)[][]>([]);

  const handleUpload = async (rawData: (string | number | null)[][]) => {
    // Only display the original data
    setData(rawData);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Navbar onUpload={handleUpload} />

      <div className="flex flex-col md:flex-row flex-1 overflow-hidden max-w-[1920px] mx-auto w-full">
        {/* Left: Excel Table */}
        <main className="flex-1 p-6 overflow-auto max-w-[1200px] h-[calc(100vh-64px)]">
          <DatasetTable data={data} />
        </main>

        {/* Right: ChatBot */}
        <aside className="w-full md:w-80 border-t md:border-t-0 md:border-l shadow-inner p-4 overflow-y-auto min-w-[320px] h-[calc(100vh-64px)]">
          <ChatBot />
        </aside>
      </div>
    </div>
  );
}
