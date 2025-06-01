"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import UploadModal from "@/components/UploadModal";
import { Download, Upload, RefreshCw } from "lucide-react";

interface NavbarProps {
  onUpload: (data: (string | number | null)[][]) => void;
  onDownload?: () => void;
  onRefresh?: () => void;
}

export default function Navbar({ onUpload, onDownload, onRefresh }: NavbarProps) {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-white shadow-sm">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        {/* Left: Logo */}
        <Link href="/" className="text-xl font-bold text-primary hover:opacity-80">
          RegexFlow
        </Link>

        {/* Middle: spacer */}
        <div className="flex-1"></div>

        {/* Right: Upload / Download / Refresh */}
        <div className="flex items-center gap-2">
          <Button onClick={() => setModalOpen(true)} variant="outline">
            <Upload className="mr-2 h-4 w-4" />
            Upload
          </Button>

          <Button onClick={onDownload} variant="default" disabled={!onDownload}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>

          <Button onClick={onRefresh} variant="secondary" disabled={!onRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>

        {/* Upload modal */}
        <UploadModal open={modalOpen} onOpenChange={setModalOpen} onUpload={onUpload} />
      </nav>
      <Separator />
    </header>
  );
}
