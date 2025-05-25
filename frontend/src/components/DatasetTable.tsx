"use client";

interface DatasetTableProps {
  data: (string | number | null)[][];
}

export default function DatasetTable({ data }: DatasetTableProps) {
  if (!Array.isArray(data) || data.length === 0) {
    return <p className="text-muted-foreground text-sm">No data uploaded yet.</p>;
  }

  const headers = data[0];
  const rows = data.slice(1);

  return (
    <div className="w-full max-h-[70vh] overflow-auto border rounded-lg shadow-sm">
        <table className="min-w-full text-sm text-left border-collapse">
        <thead className="bg-gray-100 dark:bg-gray-800 sticky top-0 z-10">
            <tr>
            {headers.map((cell, idx) => (
                <th
                key={idx}
                className="px-4 py-2 border font-semibold text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-800"
                >
                {cell ?? ""}
                </th>
            ))}
            </tr>
        </thead>
        <tbody>
            {rows.map((row, i) => (
            <tr key={i} className="border-t hover:bg-muted/50">
                {headers.map((_, j) => (
                <td
                    key={j}
                    className="px-4 py-2 border text-gray-700 dark:text-gray-100"
                >
                    {row[j] ?? ""}
                </td>
                ))}
            </tr>
            ))}
        </tbody>
        </table>
    </div>
    );
}
