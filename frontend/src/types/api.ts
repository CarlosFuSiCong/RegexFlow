// 1. CSRF Token Response
export interface CsrfTokenResponse {
  message: string; // e.g. "CSRF cookie set"
}


// 2. Upload File
export interface UploadResponse {
  columns: string[];               // e.g. ["Name", "Email", ...]
  preview: Record<string, any>[];  // first page (page_size rows) of data
  page: number;                    // always 1 for upload
  page_size: number;               // e.g. 50
  total_rows: number;              // e.g. 250
  total_pages: number;             // e.g. 5
  message: string;                 // e.g. "File uploaded successfully."
}


// 3. Preview Data (Pagination)
export interface PreviewDataResponse {
  data: Record<string, any>[];  // exactly `page_size` rows (or fewer on last page)
  page: number;                 // current page (1-based)
  page_size: number;            // number of rows per page
  total_rows: number;           // total number of rows in working_df
  total_pages: number;          // computed as Math.ceil(total_rows / page_size)
}


// 4. Generate & Expand Regex Tasks
// 4.1 Request
export interface GenerateTasksRequest {
  description: string;  // natural‐language instruction, e.g. "Replace all emails in column Email with [hidden]"
}

// 4.2 Individual Task returned by backend
export interface BackendRegexTask {
  target: string;      // e.g. "cell 0,2" or "column Email"
  regex: string;       // double‐escaped regex string, e.g. "\\b\\d{3}-\\d{3}-\\d{4}\\b"
  replacement: string; // e.g. "[redacted]"
}

// 4.3 Response
export interface GenerateTasksResponse {
  tasks: BackendRegexTask[];  // one entry per cell‐level task
  message?: string;           // optional, if added in future
}


// 5. Preview Replace Tasks
// 5.1 Request
export interface PreviewReplaceRequest {
  tasks: BackendRegexTask[];  // array of { target, regex, replacement }
}

// 5.2 One preview entry
export interface PreviewReplaceEntry {
  row: number;       // 1‐based row index
  column: string;    // column name, e.g. "Email"
  original: string;  // original cell value (stringified)
  modified: string;  // modified cell value (stringified)
}

// 5.3 Response
export interface PreviewReplaceResponse {
  message: string;                // "Preview completed."
  total_matches: number;          // total cells that would be changed
  preview: PreviewReplaceEntry[]; // up to 20 diffs
}


// 6. Apply Replace Tasks
// 6.1 Request
export interface ReplaceTasksRequest {
  tasks: BackendRegexTask[]; // same shape as PreviewReplaceRequest
}

// 6.2 One replace preview entry
export interface ReplacePreviewEntry {
  row: number;       // 0‐based row index
  column: string;    // column name, e.g. "Email"
  from: string;      // original cell value
  to: string;        // new cell value
}

// 6.3 Response
export interface ReplaceTasksResponse {
  message: string;                // "Tasks applied successfully."
  total_replacements: number;     // total cells actually changed
  preview: ReplacePreviewEntry[]; // up to 10 diffs
}
