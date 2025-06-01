"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import DatasetTable from "@/components/DatasetTable";
import ChatBot from "@/components/ChatBot";
import * as XLSX from "xlsx";
import { previewData, downloadFile } from "@/services/fileApi";
import type {
  PreviewDataResponse,
  UploadResponse,
} from "@/types/api";

interface PreviewEntry {
  row: number;
  column: string;
  original: string;
  modified: string;
}

export default function DatasetPage() {
  const [data, setData] = useState<(string | number | null)[][]>([]);
  const [previewEntries, setPreviewEntries] = useState<PreviewEntry[]>([]);
  const [currentFilename, setCurrentFilename] = useState<string | undefined>(undefined);

  // Set uploaded table data and reset preview
  const handleUpload = (tableData: (string | number | null)[][]) => {
    setData(tableData);
    setPreviewEntries([]);
  };

  // Download data from backend or export current data as Excel
  const handleDownload = async () => {
    if (!data || data.length === 0) return;

    try {
      if (currentFilename) {
        const blob = await downloadFile(currentFilename);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = currentFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        const ws = XLSX.utils.aoa_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
        XLSX.writeFile(wb, "regexflow_data.xlsx");
      }
    } catch (err) {
      console.error("Download error:", err);
      alert(`Download failed: ${(err as any).message}`);
    }
  };

  // Fetch updated data from backend
  const reloadData = async () => {
    try {
      const res: PreviewDataResponse = await previewData(1, 50);
      const rowsObj = res.data;
      if (!rowsObj || rowsObj.length === 0) {
        setData([]);
        setPreviewEntries([]);
        return;
      }
      const columns = Object.keys(rowsObj[0]);
      const onePage = rowsObj.map((row) =>
        columns.map((col) => (row[col] !== null ? row[col] : null))
      );
      setData([columns, ...onePage]);
      setPreviewEntries([]);
    } catch (err) {
      console.error("Failed to reload data:", err);
      alert(`Reload failed: ${(err as any).message}`);
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Navbar
        onUpload={handleUpload}
        onDownload={data.length > 0 ? handleDownload : undefined}
        onRefresh={data.length > 0 ? reloadData : undefined}
      />

      <div className="flex flex-col md:flex-row flex-1 overflow-hidden max-w-[1920px] mx-auto w-full">
        <main className="flex-1 p-6 overflow-auto h-[calc(100vh-64px)]">
          <DatasetTable data={data} previewEntries={previewEntries} />
        </main>

        <aside className="w-full md:w-80 border-t md:border-t-0 md:border-l shadow-inner p-4 overflow-y-auto min-w-[320px] h-[calc(100vh-64px)]">
          <ChatBot
            onDataChanged={reloadData}
            onPreviewFull={(entries) => setPreviewEntries(entries)}
          />
        </aside>
      </div>
    </div>
  );
}
