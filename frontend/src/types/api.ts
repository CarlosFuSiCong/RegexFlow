// API Response Interfaces
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

// Preview Data Types
export interface PreviewDataResponse {
  data: Record<string, any>[];
  page: number;
  page_size: number;
  total_rows: number;
  total_pages: number;
}

// Upload Response
export interface UploadResponse {
  columns: string[];
  preview: Record<string, any>[];
  page: number;
  page_size: number;
  total_rows: number;
  total_pages: number;
  message: string;
}

// Regex Task Types
export interface RegexTask {
  column: string;
  pattern: string;
  replacement: string;
  description?: string;
}

export interface GenerateRegexTasksRequest {
  text: string;
  columns: string[];
}

export interface GenerateRegexTasksResponse {
  tasks: RegexTask[];
  message: string;
}

// Preview Replace Types
export interface PreviewReplaceRequest {
  tasks: RegexTask[];
  preview_size?: number;
}

export interface PreviewReplaceResponse {
  preview: {
    original: Record<string, any>[];
    modified: Record<string, any>[];
  };
  changes_count: number;
  message: string;
}

// Replace Tasks Types
export interface ReplaceTasksRequest {
  tasks: RegexTask[];
}

export interface ReplaceTasksResponse {
  message: string;
  changes_count: number;
  modified_columns: string[];
} 