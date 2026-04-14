import "../../styles/ai-report.css";

function AIReportCard({ aiResult, onMoveSimulation }) {
  if (!aiResult) return null;

  const factorHintMap = {
    "임금수준":
      "직접 임금 조정 시뮬레이션은 없지만, 연관된 개선 시나리오를 통해 점수 변화 방향을 참고할 수 있습니다.",
    "업무부담":
      "근로시간 조정 시뮬레이션을 통해 업무부담 완화와 연결된 개선 방향을 확인할 수 있습니다.",
    "근로시간":
      "근로시간 조정 시뮬레이션으로 바로 이동해 점수 변화를 확인할 수 있습니다.",
    "회복여건":
      "휴식·근무패턴 시나리오를 통해 회복여건 개선 가능성을 확인할 수 있습니다.",
    "고용안정성":
      "고용안정성 개선 시나리오를 통해 변화 가능성을 참고할 수 있습니다.",
  };

  const factorButtonMap = {
    "임금수준": "연관된 개선 시나리오 보기 →",
    "업무부담": "업무부담 관련 시나리오 보기 →",
    "근로시간": "근로시간 시뮬레이션 보기 →",
    "회복여건": "휴식·근무패턴 시나리오 보기 →",
    "고용안정성": "고용안정성 시나리오 보기 →",
  };

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
          {aiResult.improvement_priorities?.map((item, index) => {
            const hintText =
              factorHintMap[item.factor] ||
              "해당 항목과 연결된 개선 시나리오를 바로 확인할 수 있습니다.";

            const buttonText =
              factorButtonMap[item.factor] ||
              "연관된 개선 시나리오 보기 ";

            return (
              <div key={index} className="ai-priority-item">
                <div className="ai-priority-header">
                  <span className="ai-rank-badge">{index + 1}순위</span>
                  <span className="ai-priority-factor">{item.factor}</span>
                  <span
                    className={`ai-difficulty-chip difficulty-${item.difficulty}`}
                  >
                    {item.difficulty}
                  </span>
                </div>

                <p className="ai-priority-reason">{item.reason}</p>

                <p className="ai-priority-hint">{hintText}</p>

                <button
                  className="ai-action-button"
                  onClick={() => onMoveSimulation(item.factor)}
                >
                  {buttonText}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default AIReportCard;