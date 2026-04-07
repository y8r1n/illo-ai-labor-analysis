import { /*useEffect,*/ useState } from "react";
import RadarChartCard from "../components/RadarChartCard.jsx";
import ComparisonRadarChart from "../components/ComparisonRadarChart.jsx";
import RiskPyramidCard from "../components/RiskPyramidCard.jsx";
import ComparisonSummaryCard from "../components/ComparisonSummaryCard.jsx";
import logoImg from "../assets/logo.png";
import "../styles/result.css";
import { fetchAIInterpretation } from "../api/ai";
import AIReportCard from "../components/ai/AIReportCard.jsx";

function ResultPage({ result, formData, onRestart }) {
  const [openNegative, setOpenNegative] = useState(false);
  const [openPositive, setOpenPositive] = useState(false);
  

  const comparison = result?.radar_charts?.comparison;

  const activeIndexes = comparison
    ? comparison.labels
        .map((label, index) =>
          comparison.active_axes?.includes(label) ? index : null
        )
        .filter((index) => index !== null)
    : [];

  const activeLabels = comparison
    ? activeIndexes.map((index) => comparison.labels[index])
    : [];

  const myDataset = comparison?.datasets?.[0] ?? null;
  const jobDataset = comparison?.datasets?.[1] ?? null;
  const ageDataset = comparison?.datasets?.[2] ?? null;

  const buildFilteredDataset = (dataset) => {
    if (!dataset) return null;

    return {
      ...dataset,
      values: activeIndexes.map((index) => dataset.values[index]),
    };
  };

  const filteredMyDataset = buildFilteredDataset(myDataset);
  const filteredJobDataset = buildFilteredDataset(jobDataset);
  const filteredAgeDataset = buildFilteredDataset(ageDataset);

  const jobComparisonDatasets =
    filteredMyDataset && filteredJobDataset
      ? [filteredMyDataset, filteredJobDataset]
      : [];

  const ageComparisonDatasets =
    filteredMyDataset && filteredAgeDataset
      ? [filteredMyDataset, filteredAgeDataset]
      : [];

  const formatScore = (value) =>
    typeof value === "number" ? value.toFixed(2) : "-";

const [aiResult, setAiResult] = useState(null);
const [aiLoading, setAiLoading] = useState(false);
const [aiError, setAiError] = useState("");

/*useEffect(() => {
  async function loadAIResult() {
    if (!result) return;

    try {
      setAiLoading(true);
      setAiError("");

      const data = await fetchAIInterpretation(result);
      setAiResult(data);
    } catch (error) {
      console.error(error);
      setAiError("AI 해석 리포트를 불러오지 못했습니다.");
    } finally {
      setAiLoading(false);
    }
  }

loadAIResult();
}, [result]);*/

const handleLoadAI = async () => {
  if (!result) return;

  try {
    setAiLoading(true);
    setAiError("");
    setAiResult(null); // 이전 결과 초기화

    const data = await fetchAIInterpretation(result);
    setAiResult(data);
  } catch (error) {
    console.error(error);
    setAiError("AI 해석 리포트를 불러오지 못했습니다.");
  } finally {
    setAiLoading(false);
  }
};  

  return (
    <div className="result-page">
      <div className="result-shell">
        <div className="result-header">
          <div className="result-header-left">
            <h1 className="result-main-title">종합 결과</h1>
          </div>

          <div className="result-header-right">
            <button className="result-outline-button">
              종합 결과서 PDF 다운로드
            </button>
            <button className="result-primary-button" onClick={onRestart}>
              다시 입력하기
            </button>
          </div>
        </div>

        <div className="result-body-layout">
          {/* 상단 메인 카드 */}
          <section className="result-overview-card">
            <div className="result-logo-card">
              <img src={logoImg} alt="ILLO 로고" className="result-logo-image" />
              <p className="result-logo-subtext">
                AI 기반 노동환경 점수 분석 및 과로 위험 판단 보조 시스템
              </p>
            </div>

            <div className="overview-section">
              <h2 className="section-title">입력 정보</h2>

              <div className="input-summary-grid">
                <div className="input-summary-item">
                  <span className="input-summary-label">나이</span>
                  <span className="input-summary-value">
                    {formData?.age_group || "-"}
                  </span>
                </div>

                <div className="input-summary-item">
                  <span className="input-summary-label">월 근로시간</span>
                  <span className="input-summary-value">
                    {formData?.work_hours || "-"}
                  </span>
                </div>

                <div className="input-summary-item">
                  <span className="input-summary-label">고용형태</span>
                  <span className="input-summary-value">
                    {formData?.employment_type || "-"}
                  </span>
                </div>

                <div className="input-summary-item">
                  <span className="input-summary-label">스트레스 지수</span>
                  <span className="input-summary-value">
                    {formData?.stress_level || "-"}
                  </span>
                </div>

                <div className="input-summary-item">
                  <span className="input-summary-label">업종</span>
                  <span className="input-summary-value">
                    {formData?.industry || "-"}
                  </span>
                </div>

                <div className="input-summary-item">
                  <span className="input-summary-label">월 급여액</span>
                  <span className="input-summary-value">
                    {formData?.wage || "-"}
                  </span>
                </div>

                <div className="input-summary-item">
                  <span className="input-summary-label">체력 수준</span>
                  <span className="input-summary-value">
                    {formData?.physical_level || "-"}
                  </span>
                </div>
              </div>
            </div>

            <div className="overview-section">
              <h2 className="section-title">노동환경 점수</h2>

              <div className="score-summary-row">
                <div className="score-main-block">
                  <div className="score-main-value">
                    {result?.summary?.workload_score ?? "-"}
                  </div>
                </div>

                <div className="score-meta-list">
                  <div className="score-meta-item">
                    <span className="score-meta-label">등급</span>
                    <span className="score-meta-value">
                      {result?.summary?.score_group ?? "-"}
                    </span>
                  </div>

                  <div className="score-meta-item">
                    <span className="score-meta-label">백분율</span>
                    <span className="score-meta-value">
                      {result?.summary?.score_percent ?? "-"}%
                    </span>
                  </div>
                </div>

                <div className="score-message-block">
                  <p className="section-description">
                    {result?.summary?.summary_message ?? "-"}
                  </p>
                </div>
              </div>
            </div>

            <div className="overview-divider" />

            <div className="overview-section radar-section">
              <RadarChartCard
                title="나의 점수 레이더"
                chipLabel="나의 평균 점수"
                labels={result?.radar_charts?.user_full?.labels ?? []}
                datasets={result?.radar_charts?.user_full?.datasets ?? []}
                tooltipData={result?.tooltip_data}
              />
            </div>
          </section>

          {/* 위험지수 */}
          <section className="result-risk-section">
            <div className="result-bottom-row">
              <div className="result-risk-column">
                <RiskPyramidCard risk={result?.risk} />
              </div>

              <div className="result-factor-column">
                <div className="factor-highlight-wrap">
                  <div className="factor-highlight-card negative-highlight">
                    <div className="factor-badge negative-badge">
                      주요 하락 요인
                    </div>

                    <div className="factor-head">
                      <div className="factor-circle negative-circle">
                        {result?.risk?.risk_level || "위험"}
                      </div>
                    </div>

                   <div className="factor-box">
                    {(result?.factors?.negative ?? []).length > 0 ? (
                    (result?.factors?.negative ?? []).slice(0, 3).map((item, index) => (
                    <div key={index} className="factor-box-line">
                    <span>{item.title}</span>
                    <strong>{formatScore(item.value)}</strong>
                    </div>
                    ))
                    ) : (
                    <div className="factor-empty-text">현재 표시할 하락 요인이 없습니다.</div>
                    )}
                      </div>

                    <div className="factor-list-block">
                      <button
                        className="factor-toggle"
                        onClick={() => setOpenNegative((prev) => !prev)}
                      >
                        {openNegative ? "상세 설명 접기" : "상세 설명 보기"}
                      </button>

                      {openNegative && (
                        <ul>
                          {(result?.factors?.negative ?? []).map((item, index) => (
                            <li key={index}>{item.message}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>

                  <div className="factor-highlight-card positive-highlight">
                    <div className="factor-badge positive-badge">
                      상대적으로 양호한 요인
                    </div>

                    <div className="factor-head">
                      <div className="factor-circle positive-circle">양호</div>
                    </div>

                    <div className="factor-box">
                    {(result?.factors?.positive ?? []).length > 0 ? (
                     (result?.factors?.positive ?? []).slice(0, 3).map((item, index) => (
                    <div key={index} className="factor-box-line">
                    <span>{item.title}</span>
                    <strong>{formatScore(item.value)}</strong>
                     </div>
                  ))
                    ) : (
                  <div className="factor-empty-text">현재 표시할 양호 요인이 없습니다.</div>
                    )}
                  </div>

                    <div className="factor-list-block">
                      <button
                        className="factor-toggle"
                        onClick={() => setOpenPositive((prev) => !prev)}
                      >
                        {openPositive ? "상세 설명 접기" : "상세 설명 보기"}
                      </button>

                      {openPositive && (
                        <ul>
                          {(result?.factors?.positive ?? []).map((item, index) => (
                            <li key={index}>{item.message}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* 비교 분석 */}
          <section className="compare-section">
            <div className="compare-header">
              <h2 className="compare-title">비교 분석</h2>
            </div>

            <div className="compare-stack">
              <div className="compare-row">
                <div className="compare-chart-card">
                  {jobComparisonDatasets.length > 0 && (
                    <ComparisonRadarChart
                      title="직종환경이 비슷한 조건 비교"
                      labels={activeLabels}
                      datasets={jobComparisonDatasets}
                    />
                  )}
                  <div className="compare-tag">직종환경 기준 평균</div>
                </div>

                <div className="compare-description-card">
                  <h3>직종환경 비교</h3>
                  <p>
                    현재 사용자의 점수는 직종환경이 비슷한 평균과 비교해
                    고용형태, 근로시간, 임금수준 항목에서 상대적인 위치를
                    확인할 수 있습니다.
                  </p>
                  <p>
                    비교 차트는 실제 계산 가능한 항목만 반영해 구성되었습니다.
                  </p>
                </div>
              </div>

              <div className="compare-row">
                <div className="compare-chart-card">
                  {ageComparisonDatasets.length > 0 && (
                    <ComparisonRadarChart
                      title="연령대 평균 비교"
                      labels={activeLabels}
                      datasets={ageComparisonDatasets}
                    />
                  )}
                  <div className="compare-tag">연령대 기준 평균</div>
                </div>

                <div className="compare-description-card">
                  <h3>연령대 비교</h3>
                  <p>
                    현재 사용자의 점수는 동일 연령대 평균과 비교해 상대적인
                    노동환경 상태를 확인할 수 있습니다.
                  </p>
                  <p>
                    연령대 평균과의 차이는 현재 위치를 직관적으로 이해하는 데
                    도움을 줍니다.
                  </p>
                </div>
              </div>
            </div>

            <ComparisonSummaryCard comparisons={result?.comparisons} />
          </section>

          {/* AI 해석 리포트 */}
       {!aiResult && !aiLoading && (
 <button 
  className="ai-load-button" 
  onClick={handleLoadAI}
  disabled={aiLoading}
>
  {aiLoading ? "생성 중..." : "AI 리포트 생성하기"}
</button>
)}

{aiLoading && (
  <div className="section-card">AI 해석 리포트 생성 중...</div>
)}

{aiError && !aiResult && (
  <div className="section-card">{aiError}</div>
)}

{aiResult && (
  <AIReportCard aiResult={aiResult} />
)}

          <div className="result-footer-note">
            ※ 본 결과는 참고용 분석 자료이며, 법적 판단을 대체하지 않습니다.
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultPage;