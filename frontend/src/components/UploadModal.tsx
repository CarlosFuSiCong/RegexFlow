"use client";

import { useState } from "react";
import { uploadFile } from "@/services/fileApi";
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
  onUpload: (data: (string | number | null)[][]) => void;
}

export default function UploadModal({ open, onOpenChange, onUpload }: UploadModalProps) {
  const [fileName, setFileName] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setUploading(true);

    try {
      const response = await uploadFile(file);
      const headers = response.columns;
      const preview = response.preview;

      const tableData: (string | number | null)[][] = [
        headers,
        ...preview.map((row) => headers.map((col) => row[col] ?? null)),
      ];

      onUpload(tableData);
      onOpenChange(false);
    } catch (err) {
      alert("Upload failed. Please try again.");
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload Excel or CSV File</DialogTitle>
          <DialogDescription>
            Select a file to upload. Only Excel or CSV formats are supported.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileChange}
            disabled={uploading}
          />
          {fileName && (
            <p className="text-sm text-muted-foreground">
              Uploaded: <span className="font-medium">{fileName}</span>
            </p>
          )}
          {uploading && (
            <p className="text-sm text-blue-500 animate-pulse">Uploading...</p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
