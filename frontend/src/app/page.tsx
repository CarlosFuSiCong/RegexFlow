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
    <div className="min-h-screen flex flex-col">
      <Navbar onUpload={handleUpload} />

      <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
        {/* Left: Excel Table */}
        <main className="flex-1 p-6 overflow-auto">
          <DatasetTable data={data} />
        </main>

        {/* Right: ChatBot */}
        <aside className="w-full md:w-80 border-t md:border-t-0 md:border-l shadow-inner p-4 overflow-y-auto">
          <ChatBot />
        </aside>
      </div>
    </div>
  );
}
