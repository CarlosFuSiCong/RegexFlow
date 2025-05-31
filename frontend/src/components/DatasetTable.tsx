import React from "react";

// 添加 Props 类型
interface DatasetTableProps {
  data: (string | number | null)[][];
}

const DatasetTable: React.FC<DatasetTableProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return <p>No data to display.</p>;
  }

  const headers = data[0];
  const rows = data.slice(1);

  return (
    <table className="min-w-full border text-sm">
      <thead className="bg-gray-100">
        <tr>
          {headers.map((header, idx) => (
            <th key={idx} className="px-2 py-1 border">
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIdx) => (
          <tr key={rowIdx}>
            {row.map((cell, cellIdx) => (
              <td key={cellIdx} className="px-2 py-1 border">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DatasetTable;
