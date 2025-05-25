"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import UploadModal from "@/components/UploadModal";

interface NavbarProps {
  onUpload: (data: any[][]) => void;
}

export default function Navbar({ onUpload }: NavbarProps) {
  const [open, setOpen] = useState(false);

  return (
    <header className="w-full bg-white shadow-sm sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto flex items-center justify-between px-4 py-3">
        {/* Left: Logo */}
        <Link href="/" className="text-xl font-bold text-primary hover:opacity-80">
          RegexFlow
        </Link>

        {/* Right: Upload Button */}
        <UploadModal open={open} onOpenChange={setOpen} onUpload={onUpload} />
        <Button variant="default" onClick={() => setOpen(true)}>
          Upload
        </Button>
      </nav>
      <Separator />
    </header>
  );
}
