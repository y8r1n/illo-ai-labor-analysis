function getDirectionText(direction) {
  if (direction === "higher") return "평균보다 높음";
  if (direction === "lower") return "평균보다 낮음";
  return "평균과 유사";
}

function getDirectionColor(direction) {
  if (direction === "higher") return "#22c55e";
  if (direction === "lower") return "#ef4444";
  return "#6b7280";
}

function formatScore(value) {
  if (value === null || value === undefined) return "-";
  return Number(value).toFixed(2);
}

function formatDiff(value) {
  if (value === null || value === undefined) return "-";
  const num = Number(value);
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(2)}`;
}

function ComparisonItem({ title, data }) {
  if (!data) return null;

  const color = getDirectionColor(data.direction);
  const directionText = getDirectionText(data.direction);

  return (
    <div
      style={{
        border: "1px solid #d9f7f7",
        borderRadius: "14px",
        padding: "18px",
        backgroundColor: "#fcffff",
      }}
    >
      <div
        style={{
          fontSize: "15px",
          fontWeight: 700,
          marginBottom: "12px",
          color: "#111827",
        }}
      >
        {title}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr auto",
          gap: "10px",
          alignItems: "center",
        }}
      >
        <div>
          <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "4px" }}>
            비교 평균 점수
          </div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "#1f2937" }}>
            {formatScore(data.overall_score)}
          </div>
        </div>

        <div
          style={{
            padding: "8px 12px",
            borderRadius: "999px",
            backgroundColor: `${color}15`,
            color,
            fontSize: "13px",
            fontWeight: 700,
            whiteSpace: "nowrap",
          }}
        >
          {directionText}
        </div>
      </div>

      <div
        style={{
          marginTop: "14px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "14px",
        }}
      >
        <span style={{ color: "#6b7280" }}>나와의 차이</span>
        <span style={{ fontWeight: 700, color }}>{formatDiff(data.difference_from_user)}</span>
      </div>
    </div>
  );
}

function ComparisonSummaryCard({ comparisons }) {
  if (!comparisons) return null;

  return (
    <div
      style={{
        backgroundColor: "#fff",
        padding: "24px",
        borderRadius: "16px",
        border: "1px solid #d9f7f7",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: "18px" }}>비교 분석</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
        }}
      >
        <ComparisonItem
          title="직종환경이 비슷한 평균"
          data={comparisons.job_average}
        />

        <ComparisonItem
          title="나의 연령대 평균"
          data={comparisons.age_average}
        />
      </div>
    </div>
  );
}

export default ComparisonSummaryCard;