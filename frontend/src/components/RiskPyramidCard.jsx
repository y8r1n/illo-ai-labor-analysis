function getRiskStepIndex(riskLevel) {
  const levels = ["양호", "보통", "주의", "위험", "과로 위험"];
  return levels.indexOf(riskLevel);
}

function RiskPyramidCard({ risk }) {
  const levels = ["과로 위험", "위험", "주의", "보통", "양호"];
  const activeIndex = risk?.risk_level
    ? 4 - getRiskStepIndex(risk.risk_level)
    : -1;

  return (
    <div className="risk-card">
      <div className="risk-card-header">
        <h2 className="section-title">위험지수</h2>
      </div>

      <div className="risk-card-body">
        <div className="risk-level-stack">
          {levels.map((label, index) => {
            const widths = ["30%", "44%", "60%", "76%", "92%"];
            const isActive = activeIndex === index;

            return (
              <div
                key={label}
                className={`risk-level-step ${isActive ? "active" : ""}`}
                style={{ width: widths[index] }}
              >
                <span>{label}</span>
                {isActive && <div className="risk-level-dot" />}
              </div>
            );
          })}
        </div>

        <div className="risk-summary-box">
          <div className="risk-summary-item">
            <span className="risk-summary-label">위험지수</span>
            <span className="risk-summary-value">{risk?.risk_percent}%</span>
          </div>

          <div className="risk-summary-item">
            <span className="risk-summary-label">위험레벨</span>
            <span className="risk-summary-highlight">{risk?.risk_level}</span>
          </div>

          <div className="risk-summary-item risk-message-block">
            <span className="risk-summary-label">해석</span>
            <p>{risk?.risk_message}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RiskPyramidCard;