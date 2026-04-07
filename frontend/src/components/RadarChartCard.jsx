import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

function CustomTooltip({ active, payload, tooltipData }) {
  if (!active || !payload || !payload.length) return null;

  const subject = payload?.[0]?.payload?.subject;
  const info = tooltipData?.[subject];

  return (
    <div className="radar-tooltip">
      <p className="radar-tooltip-title">{subject}</p>
      <p className="radar-tooltip-score">
        나의 점수: {info?.user_score ?? payload?.[0]?.value ?? 0}
      </p>
      <p className="radar-tooltip-message">{info?.message ?? ""}</p>
    </div>
  );
}

function RadarChartCard({
  title,
  labels = [],
  datasets = [],
  tooltipData = {},
  chipLabel = "",
}) {
  const chartData = labels.map((label, index) => {
    const row = { subject: label };

    datasets.forEach((dataset) => {
      row[dataset.name] = dataset.values[index] ?? 0;
    });

    return row;
  });

  return (
    <div className="radar-card">
      <div className="radar-card-header">
        <h3>{title}</h3>
      </div>

      <div className="radar-card-body">
        <ResponsiveContainer width="100%" height={290}>
          <RadarChart data={chartData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis domain={[0, 1]} />
            <Tooltip content={<CustomTooltip tooltipData={tooltipData} />} />
            {datasets.map((dataset, index) => (
              <Radar
                key={dataset.name}
                name={dataset.name}
                dataKey={dataset.name}
                stroke={index === 0 ? "#51d6e3" : "#8f9bff"}
                fill={index === 0 ? "#51d6e3" : "#8f9bff"}
                fillOpacity={0.28}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {chipLabel && <div className="radar-bottom-chip">{chipLabel}</div>}
    </div>
  );
}

export default RadarChartCard;