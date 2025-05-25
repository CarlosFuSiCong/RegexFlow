"use client";

import { useState } from "react";
import * as XLSX from "xlsx";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

interface UploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpload: (data: any[][]) => void;
}

export default function UploadModal({ open, onOpenChange, onUpload }: UploadModalProps) {
  const [fileName, setFileName] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      const binaryStr = event.target?.result;
      if (typeof binaryStr === "string" || binaryStr instanceof ArrayBuffer) {
        const workbook = XLSX.read(binaryStr, { type: "binary" });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const parsedData: any[][] = XLSX.utils.sheet_to_json(sheet, { header: 1 });
        onUpload(parsedData);
        onOpenChange(false); // close after upload
      }
    };
    reader.readAsBinaryString(file);
  };

  return (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Upload Excel/CSV File</DialogTitle>
        <DialogDescription>
          Select a file to upload. Only Excel or CSV formats are supported.
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-4">
        <Input type="file" accept=".xlsx, .xls, .csv" onChange={handleFileChange} />
        {fileName && <p className="text-sm text-muted-foreground">Uploaded: {fileName}</p>}
      </div>
    </DialogContent>
  </Dialog>
);
}