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

function ComparisonRadarChart({
  title,
  labels = [],
  datasets = [],
  isPdf = false,
}) {
  const chartData = labels.map((label, index) => {
    const row = { subject: label };

    datasets.forEach((dataset) => {
      row[dataset.name] = dataset.values[index];
    });

    return row;
  });

  const chartHeight = isPdf ? 210 : 340;
  const chartWidth = isPdf ? 250 : undefined;

  const chart = (
    <RadarChart
      width={isPdf ? chartWidth : undefined}
      height={isPdf ? chartHeight : undefined}
      data={chartData}
      margin={
        isPdf
          ? { top: 10, right: 20, bottom: 10, left: 20 }
          : { top: 10, right: 30, bottom: 10, left: 30 }
      }
    >
      <PolarGrid stroke="#d9d9d9" />
      <PolarAngleAxis
        dataKey="subject"
        tick={{ fontSize: isPdf ? 11 : 13 }}
      />
      <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />

      {!isPdf && <Tooltip />}
      {!isPdf && <Legend />}

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
            strokeWidth={isPdf ? 2 : 2}
            dot={
              isPdf
                ? false
                : {
                    r: 4,
                    strokeWidth: 2,
                    fill: colors[index]?.fill || "#999",
                  }
            }
          />
        );
      })}
    </RadarChart>
  );

  return (
    <div
      style={{
        border: "1px solid #d9f7f7",
        borderRadius: "16px",
        padding: isPdf ? "8px" : "20px",
        backgroundColor: "#fff",
        width: "100%",
        minHeight: isPdf ? "auto" : "420px",
        boxSizing: "border-box",
      }}
    >
      <h3 style={{ marginBottom: isPdf ? "10px" : "16px" }}>{title}</h3>

      {isPdf ? (
        <div
          style={{
            width: chartWidth,
            height: chartHeight,
            margin: "0 auto",
          }}
        >
          {chart}
        </div>
      ) : (
        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>{chart}</ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default ComparisonRadarChart;