import "../../styles/ai-report.css";

function AIReportCard({ aiResult }) {
  if (!aiResult) return null;

  return (
    <section className="ai-report-card">
      <h2 className="section-title">AI 해석 리포트</h2>

      <div className="ai-report-section">
        <h3 className="ai-report-subtitle">현재 상태 요약</h3>
        <p className="ai-report-text">{aiResult.summary_text}</p>
      </div>

      <div className="ai-report-section">
        <h3 className="ai-report-subtitle">위험 수준 해석</h3>
        <p className="ai-report-text">{aiResult.risk_analysis}</p>
      </div>

      <div className="ai-report-section">
        <h3 className="ai-report-subtitle">개선 우선순위</h3>
        <div className="ai-priority-list">
          {aiResult.improvement_priorities?.map((item, index) => (
            <div key={index} className="ai-priority-item">
              <div className="ai-priority-top">
                <span className="ai-priority-factor">{item.factor}</span>
                <span className={`ai-difficulty-chip difficulty-${item.difficulty}`}>
                  {item.difficulty}
                </span>
              </div>
              <p className="ai-priority-reason">{item.reason}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default AIReportCard;