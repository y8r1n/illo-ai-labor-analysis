import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

function ComparisonRadarChart({ title, labels = [], datasets = [] }) {
  const chartData = labels.map((label, index) => {
    const row = { subject: label };

    datasets.forEach((dataset) => {
      row[dataset.name] = dataset.values[index];
    });

    return row;
  });

  return (
    <div
      style={{
        border: "1px solid #d9f7f7",
        borderRadius: "16px",
        padding: "20px",
        backgroundColor: "#fff",
        width: "100%",
        minHeight: "420px",
        boxSizing: "border-box",
      }}
    >
      <h3 style={{ marginBottom: "16px" }}>{title}</h3>

      <div style={{ width: "100%", height: 340 }}>
        <ResponsiveContainer>
          <RadarChart data={chartData}>
            <PolarGrid stroke="#d9d9d9" />
            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 13 }} />
            <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
            <Tooltip />
            <Legend />

            {datasets.map((dataset, index) => {
              const colors = [
                { stroke: "#55dbe6", fill: "#55dbe6" },
                { stroke: "#8f9bff", fill: "#8f9bff" },
              ];

              return (
                <Radar
                  key={dataset.name}
                  name={dataset.name}
                  dataKey={dataset.name}
                  stroke={colors[index]?.stroke || "#999"}
                  fill={colors[index]?.fill || "#999"}
                  fillOpacity={0.22}
                  strokeWidth={2}
                  dot={{
                    r: 4,
                    strokeWidth: 2,
                    fill: colors[index]?.fill || "#999",
                  }}
                />
              );
            })}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ComparisonRadarChart;