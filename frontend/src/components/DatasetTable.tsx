"use client";

import React from "react";

interface PreviewEntry {
  row: number;       // 1-based row (excluding header)
  column: string;    // column name
  original: string;
  modified: string;
}

interface DatasetTableProps {
  data: (string | number | null)[][];
  previewEntries?: PreviewEntry[];
}

const DatasetTable: React.FC<DatasetTableProps> = ({
  data,
  previewEntries = [],
}) => {
  if (!data || data.length === 0) {
    return <p className="text-center text-gray-500">No data to display.</p>;
  }

  const headers = data[0] as (string | number | null)[];
  const rows = data.slice(1);

  // Map column name → index
  const colNameToIndex = new Map<string, number>();
  headers.forEach((h, idx) => {
    if (h !== null && h !== undefined) {
      colNameToIndex.set(String(h), idx);
    }
  });

  // Map "row-colIdx" → preview entry
  const previewMap = new Map<string, PreviewEntry>();
  previewEntries.forEach((entry) => {
    const colIdx = colNameToIndex.get(entry.column);
    if (colIdx !== undefined) {
      previewMap.set(`${entry.row}-${colIdx}`, entry);
    }
  });

  return (
    <div className="w-full overflow-x-auto">
      <table className="min-w-full border-collapse text-sm">
        <thead className="bg-gray-100">
          <tr>
            {headers.map((header, idx) => (
              <th
                key={`header-${idx}`}
                className="px-2 py-1 border text-left sticky top-0 bg-gray-100"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIdx) => {
            const rowNumber = rowIdx + 1;
            const rowBg = rowIdx % 2 === 0 ? "bg-white" : "bg-gray-50";

            return (
              <tr key={`row-${rowIdx}`} className={rowBg}>
                {row.map((cell, cellIdx) => {
                  const key = `${rowNumber}-${cellIdx}`;
                  const entry = previewMap.get(key);

                  if (!entry) {
                    return (
                      <td
                        key={`cell-${rowIdx}-${cellIdx}`}
                        className="px-2 py-1 border"
                      >
                        {cell !== null && cell !== undefined ? String(cell) : ""}
                      </td>
                    );
                  }

                  return (
                    <td
                      key={`cell-${rowIdx}-${cellIdx}`}
                      className="px-2 py-1 border bg-yellow-50"
                    >
                      <div className="line-through text-red-600">
                        {entry.original}
                      </div>
                      <div className="text-green-600">{entry.modified}</div>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default DatasetTable;
