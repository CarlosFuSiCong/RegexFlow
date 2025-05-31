"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import UploadModal from "@/components/UploadModal";

interface NavbarProps {
  onUpload: (data: (string | number | null)[][]) => void;
}

export default function Navbar({ onUpload }: NavbarProps) {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-white shadow-sm">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        {/* Logo */}
        <Link href="/" className="text-xl font-bold text-primary hover:opacity-80">
          RegexFlow
        </Link>

        {/* Upload */}
        <div className="flex items-center gap-2">
          <Button onClick={() => setModalOpen(true)}>Upload</Button>
        </div>

        {/* Upload Modal */}
        <UploadModal open={modalOpen} onOpenChange={setModalOpen} onUpload={onUpload} />
      </nav>
      <Separator />
    </header>
  );
}
