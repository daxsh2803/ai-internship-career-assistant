"use client";

import React, { useRef, useState } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { ResumeUploadResponse } from "@/lib/types";

interface DropzoneProps {
  onUploadSuccess: (data: ResumeUploadResponse) => void;
  onUploadError?: (errorMsg: string) => void;
}

export const Dropzone: React.FC<DropzoneProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndUpload = async (file: File) => {
    setErrorMessage(null);

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      const err = "Please upload a valid PDF document (.pdf format only).";
      setErrorMessage(err);
      onUploadError?.(err);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      const err = "File exceeds the 10MB maximum upload limit.";
      setErrorMessage(err);
      onUploadError?.(err);
      return;
    }

    setSelectedFile(file);
    setIsUploading(true);

    try {
      const res = await apiClient.uploadResume(file);
      onUploadSuccess(res);
    } catch (err: any) {
      const errText = err.message || "Failed to process resume PDF.";
      setErrorMessage(errText);
      onUploadError?.(errText);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20 scale-[1.01]"
            : "border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/50 dark:hover:bg-slate-800/50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              validateAndUpload(e.target.files[0]);
            }
          }}
        />

        <div className="w-14 h-14 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4 shadow-sm">
          {isUploading ? (
            <svg
              className="animate-spin h-7 w-7 text-indigo-600 dark:text-indigo-400"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            <UploadCloud className="w-7 h-7" />
          )}
        </div>

        <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-1">
          {isUploading
            ? "Extracting & Indexing Resume..."
            : "Drop your PDF Resume here, or browse"}
        </h4>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mb-3">
          PyMuPDF layout-aware coordinate extraction with automated ESCO skill taxonomy indexing (PDF up to 10MB).
        </p>

        {selectedFile && !isUploading && (
          <div className="inline-flex items-center gap-2 text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-3 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
            <FileText className="w-3.5 h-3.5" />
            <span>{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
            <CheckCircle2 className="w-3.5 h-3.5" />
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="mt-3 flex items-center gap-2 text-xs text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 p-2.5 rounded-lg border border-rose-200 dark:border-rose-800">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
