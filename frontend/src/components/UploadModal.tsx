"use client";

import { useRef, useState } from "react";
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
import { UploadCloud, Loader2 } from "lucide-react";

interface UploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpload: (data: (string | number | null)[][]) => void;
}

export default function UploadModal({ open, onOpenChange, onUpload }: UploadModalProps) {
  const [fileName, setFileName] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg">Upload Excel or CSV File</DialogTitle>
          <DialogDescription>
            Select a file to upload. Only Excel or CSV formats are supported.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileChange}
            hidden
          />

          <Button
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
            onClick={triggerFileInput}
            disabled={uploading}
          >
            <UploadCloud className="w-4 h-4" />
            {uploading ? "Uploading..." : "Select File"}
          </Button>

          {fileName && (
            <p className="text-sm text-muted-foreground">
              Selected file: <span className="font-medium">{fileName}</span>
            </p>
          )}

          {uploading && (
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <Loader2 className="animate-spin h-4 w-4" />
              Uploading file, please wait...
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
