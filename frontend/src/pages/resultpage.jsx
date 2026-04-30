import { useRef, useState } from "react";
import html2pdf from "html2pdf.js/dist/html2pdf.bundle";
import RadarChartCard from "../components/RadarChartCard.jsx";
import ComparisonRadarChart from "../components/ComparisonRadarChart.jsx";
import RiskPyramidCard from "../components/RiskPyramidCard.jsx";
import ComparisonSummaryCard from "../components/ComparisonSummaryCard.jsx";
import logoImg from "../assets/logo.png";
import "../styles/result.css";
import { fetchAIInterpretation, fetchRagAI } from "../api/ai";
import AIReportCard from "../components/ai/AIReportCard.jsx";
import SimulationSection from "../components/ai/AISimulationCard.jsx";  
import AIPolicyCard from "../components/ai/AIPolicyCard.jsx";


function ResultPage({ result, formData, onRestart }) {
  const reportRef = useRef(null);
  const [pdfLoading, setPdfLoading] = useState(false);

  const [openNegative, setOpenNegative] = useState(false);
  const [openPositive, setOpenPositive] = useState(false);
  
  const genderData = result?.comparisons?.gender_average;

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


 const formatDiffText = (diff, direction) => {
  if (typeof diff !== "number" || !direction) return "비교 가능한 차이 정보가 없습니다.";

  const absDiff = Math.abs(diff).toFixed(2);

  if (direction === "higher") {
    return `현재 사용자의 점수는 평균보다 ${absDiff} 높게 나타났습니다.`;
  }
  if (direction === "lower") {
    return `현재 사용자의 점수는 평균보다 ${absDiff} 낮게 나타났습니다.`;
  }
  return "현재 사용자의 점수는 평균과 동일한 수준입니다.";
};

const jobAvg = result?.comparisons?.job_average;
const ageAvg = result?.comparisons?.age_average;


 const buildAnalysisSummary = (data) => {
  if (!data) return [];

  const messages = [];

  const group = data?.summary?.score_group;
  const stress = data?.weights?.stress_weight ?? data?.stress_weight ?? 1;
  const industry = data?.weights?.industry_weight ?? data?.industry_weight ?? 1;
  const recovery = data?.summary?.recovery_score ?? data?.recovery_score ?? 1;
  const burden =
  data?.summary?.workload_burden_score ?? data?.workload_burden_score ?? 1;

  // 1. 전체 상태 + 원인
 if (group === "양호") {
  messages.push("현재 노동환경은 전반적으로 비교적 안정적인 편입니다.");
} else if (group === "보통") {
  messages.push("현재 노동환경은 전반적으로 보통 수준이며, 일부 요인이 점수 상승을 제한하고 있습니다.");
} else if (group === "주의 필요") {
  messages.push("현재 노동환경은 주의가 필요한 수준이며, 일부 항목의 개선이 필요합니다.");
} else if (group === "위험" || group === "과로 위험") {
  messages.push("현재 노동환경은 위험 신호가 비교적 큰 상태로, 우선적인 점검이 필요합니다.");
}

  // 2. 스트레스 + 패턴 연결
  if (stress < 0.95) {
    messages.push(
      "스트레스 수준이 높고 업무 부담 요인이 반영되어 전체 점수 하락에 영향을 주고 있습니다."
    );
  }

  // 3. 업종 영향
  if (industry >= 1.08) {
    messages.push(
      "현재 업종은 산업재해 위험도가 높은 편으로, 기본 위험 수준이 상대적으로 높게 반영되었습니다."
    );
  } else {
    messages.push(
      "현재 업종의 물리적 위험도는 상대적으로 낮지만, 다른 요인이 점수에 더 큰 영향을 주고 있습니다."
    );
  }

  // 4. 회복 vs 부담 비교
  if (recovery >= 1.0 && burden < 0.95) {
    messages.push(
      "회복 여건은 양호하지만, 업무 부담 요인이 더 크게 작용하여 전체 점수 상승이 제한되고 있습니다."
    );
  }

  // 5. 핵심 요인 강조
  const topNegative = data?.factors?.negative?.[0]?.title;
  if (topNegative) {
    messages.push(`가장 우선적으로 개선이 필요한 항목은 ${topNegative}입니다.`);
  }

  return messages.slice(0, 4);
};

const getScoreLabel = (score) => {
  if (typeof score !== "number") return "판단불가";
  if (score < 0.4) return "개선 필요";
  if (score < 0.7) return "주의";
  return "양호";
};

const [aiResult, setAiResult] = useState(null);
const [aiLoading, setAiLoading] = useState(false);
const [aiError, setAiError] = useState("");

const [ragAIResult, setRagAIResult] = useState(null);
const [ragAILoading, setRagAILoading] = useState(false);
const [ragAIError, setRagAIError] = useState("");

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

const handleLoadRagAI = async () => {
  if (!result?.rag) return;

  try {
    setRagAILoading(true);
    setRagAIError("");
    setRagAIResult(null);

  const data = await fetchRagAI({
  rag: result?.rag,
  viewer_role: formData?.viewer_role || "employee",
  user_selected_contexts: formData?.user_selected_contexts ?? [],
  risk_factors: result?.risk_factors ?? [],
  related_factors: result?.related_factors ?? [],
  negative_factors: result?.factors?.negative ?? [],

  user_input: {
    work_hours: formData?.work_hours,
    stress_level: formData?.stress_level,
    wage: formData?.wage,
    employment_type: formData?.employment_type,
    industry: formData?.industry,
    age_group: formData?.age_group,
  },
});

    setRagAIResult(data);
  } catch (error) {
    console.error(error);
    setRagAIError("정책 AI 설명을 불러오지 못했습니다.");
  } finally {
    setRagAILoading(false);
  }
};

const ensureAIResultsForPDF = async () => {
  let nextAiResult = aiResult;
  let nextRagAIResult = ragAIResult;

  if (!nextAiResult && result) {
    setAiLoading(true);
    setAiError("");

    const data = await fetchAIInterpretation(result);
    setAiResult(data);
    nextAiResult = data;

    setAiLoading(false);
  }

  if (!nextRagAIResult && result?.rag) {
    setRagAILoading(true);
    setRagAIError("");

  

    const data = await fetchRagAI({
      rag: result?.rag,
      viewer_role: formData?.viewer_role || "employee",
      user_selected_contexts: formData?.user_selected_contexts ?? [],
      risk_factors: result?.risk_factors ?? [],
      related_factors: result?.related_factors ?? [],
      negative_factors: result?.factors?.negative ?? [],
      user_input: {
        work_hours: formData?.work_hours,
        stress_level: formData?.stress_level,
        wage: formData?.wage,
        employment_type: formData?.employment_type,
        industry: formData?.industry,
        age_group: formData?.age_group,
      },
    });

    setRagAIResult(data);
    nextRagAIResult = data;

    setRagAILoading(false);
  }

  return {
    ai: nextAiResult,
    ragAI: nextRagAIResult,
  };
};

const handleDownloadPDF = async () => {
  let clonedElement = null;

  try {
    setPdfLoading(true);

    await ensureAIResultsForPDF();

    await new Promise((resolve) => {
      requestAnimationFrame(() => {
        requestAnimationFrame(resolve);
      });
    });

    const element = reportRef.current;
    if (!element) throw new Error("PDF 대상 요소 없음");

    clonedElement = element.cloneNode(true);

    clonedElement.style.position = "static";
    clonedElement.style.left = "auto";
    clonedElement.style.top = "auto";
    clonedElement.style.display = "block";
    clonedElement.style.visibility = "visible";
    clonedElement.style.opacity = "1";
    clonedElement.style.width = "760px";
    clonedElement.style.maxWidth = "760px";
    clonedElement.style.height = "auto";
    clonedElement.style.overflow = "visible";
    clonedElement.style.background = "#ffffff";

    document.body.appendChild(clonedElement);

    const opt = {
      margin: [8, 8, 8, 8],
      filename: "ILLO_report.pdf",
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        backgroundColor: "#ffffff",
        windowWidth: 760,
        scrollX: 0,
        scrollY: 0,
      },
      jsPDF: {
        unit: "mm",
        format: "a4",
        orientation: "portrait",
      },
      pagebreak: {
        mode: ["css", "legacy"],
        before: ".pdf-page-break",
        avoid: [
          ".factor-highlight-card",
          ".compare-row",
          ".analysis-summary-item",
          ".score-summary-row"
          ],
      },
    };

    await html2pdf().set(opt).from(clonedElement).save();
  } catch (error) {
    console.error(error);
    alert("PDF 생성 중 오류가 발생했습니다.");
  } finally {
    if (clonedElement) {
      document.body.removeChild(clonedElement);
    }
    setPdfLoading(false);
  }
};

const [activeSimulationId, setActiveSimulationId] = useState("");

const factorToSimulation = {
  "근로시간": "simulation-worktime",
  "업무부담": "simulation-worktime",
  "회복여건": "simulation-rest",
  "고용안정성": "simulation-employment",
  "임금수준": "simulation-worktime",
};

const handleMoveSimulation = (factor) => {
  const targetId = factorToSimulation[factor];
  if (!targetId) return;

  setActiveSimulationId(targetId);

  document.getElementById(targetId)?.scrollIntoView({
    behavior: "smooth",
    block: "center",
  });

  setTimeout(() => {
    setActiveSimulationId("");
  }, 1600);
};
const analysisSummary = buildAnalysisSummary(result);



  return (
      <div className="result-page">
      <div className="result-shell">
        <div className="result-header">
          <div className="result-header-left">
            <h1 className="result-main-title">종합 결과</h1>
          </div>

          <div className="result-header-right">
            <button
            className="result-outline-button"
            onClick={handleDownloadPDF}
            disabled={pdfLoading || aiLoading || ragAILoading}
            >
           {pdfLoading ? "PDF 준비 중..." : "종합 결과서 PDF 다운로드"}
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
                  <span className="input-summary-label">성별</span>
                  <span className="input-summary-value">
                    {formData?.gender || "-"}
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
                    <div className="factor-meta">
                    <strong>{formatScore(item.value)}</strong>
                    <span className={`factor-score-label ${getScoreLabel(item.value)}`}>
                    {getScoreLabel(item.value)}
                    </span>
                    </div>
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
                    <div className="factor-meta">
                    <strong>{formatScore(item.value)}</strong>
                  <span className={`factor-score-label ${getScoreLabel(item.value)}`}>
                    {getScoreLabel(item.value)}
                    </span>
                    </div>
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

          <section className="analysis-summary-section">
  <div className="analysis-summary-card">
    <div className="analysis-summary-header">
      <h2 className="section-title">종합 해석 요약</h2>
      <p className="section-description">
        현재 입력값과 계산 결과를 바탕으로 주요 위험 요인을 정리한 요약입니다.
      </p>
    </div>

    <div className="analysis-summary-list">
      {analysisSummary.length > 0 ? (
        analysisSummary.map((message, index) => (
          <div key={index} className="analysis-summary-item">
            <span className="analysis-summary-dot">•</span>
            <p>{message}</p>
          </div>
        ))
      ) : (
        <div className="analysis-summary-empty">
          현재 표시할 분석 요약이 없습니다.
        </div>
      )}
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
  {formatDiffText(jobAvg?.difference_from_user, jobAvg?.direction)}
</p>
<p>
  직종환경이 비슷한 평균과 비교해 고용안정성, 근로시간, 임금수준 항목의 상대적 위치를 확인할 수 있습니다.
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
  {formatDiffText(ageAvg?.difference_from_user, ageAvg?.direction)}
</p>
<p>
  동일 연령대 평균과 비교해 현재 노동환경 상태를 직관적으로 확인할 수 있습니다.
</p>
                </div>
              </div>
            </div>
    <ComparisonSummaryCard comparisons={result?.comparisons} />
            
            
            {genderData && (
  <div className="gender-compare-card">
    <h3 className="section-subtitle">참고 비교 정보</h3>

    <div className="gender-card">
      <div className="gender-title">
       {genderData.group_name}
      </div>

      <div className="gender-info">
        <div>평균 근로시간: {genderData.avg_work_hours}시간</div>
        <div>평균 임금: {genderData.avg_wage?.toLocaleString()}원</div>
      </div>

      <p className="gender-note">
        * 동일 성별 평균 기준 참고 정보입니다.
      </p>
    </div>
  </div>
)}
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
  <AIReportCard
  aiResult={aiResult}
  onMoveSimulation={handleMoveSimulation}
/>
)}

<SimulationSection
  simulation={result?.simulation}
  activeSimulationId={activeSimulationId}
/>
<AIPolicyCard
  rag={result?.rag}
  ragAIResult={ragAIResult}
  ragAILoading={ragAILoading}
  ragAIError={ragAIError}
  onLoadRagAI={handleLoadRagAI}
/>

          <div className="result-footer-note">
            ※ 본 결과는 참고용 분석 자료이며, 법적 판단을 대체하지 않습니다.
          </div>
        </div>
      </div>


      {/* pdf 영역 */}
<div className="pdf-only-report" ref={reportRef}>
  <div className="pdf-report-inner result-shell pdf-result-shell">
    <div className="pdf-report-header">
      <img src={logoImg} alt="ILLO 로고" className="pdf-logo" />
      <h1>ILLO 노동환경 분석 결과서</h1>
      <p>AI 기반 노동환경 점수 분석 및 과로 위험 판단 보조 리포트</p>
    </div>

    <div className="result-body-layout pdf-body-layout">
      <section className="result-overview-card pdf-section">

        <div className="overview-section">
          <h2 className="section-title">입력 정보</h2>

          <div className="input-summary-grid">
            {[
              ["나이", formData?.age_group],
              ["성별", formData?.gender],
              ["월 근로시간", formData?.work_hours],
              ["고용형태", formData?.employment_type],
              ["스트레스 지수", formData?.stress_level],
              ["업종", formData?.industry],
              ["월 급여액", formData?.wage],
              ["체력 수준", formData?.physical_level],
            ].map(([label, value]) => (
              <div className="input-summary-item" key={label}>
                <span className="input-summary-label">{label}</span>
                <span className="input-summary-value">{value || "-"}</span>
              </div>
            ))}
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
            isPdf
            title="나의 점수 레이더"
            chipLabel="나의 평균 점수"
            labels={result?.radar_charts?.user_full?.labels ?? []}
            datasets={result?.radar_charts?.user_full?.datasets ?? []}
            tooltipData={result?.tooltip_data}
            />
        </div>
      </section>

      <section className="result-risk-section pdf-section">
        <div className="result-bottom-row">
          <div className="result-risk-column">
            <RiskPyramidCard risk={result?.risk} />
          </div>

          <div className="result-factor-column pdf-page-break-before">
            <div className="factor-highlight-wrap">
              <div className="factor-highlight-card negative-highlight">
                <div className="factor-badge negative-badge">주요 하락 요인</div>

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
                        <div className="factor-meta">
                          <strong>{formatScore(item.value)}</strong>
                          <span className={`factor-score-label ${getScoreLabel(item.value)}`}>
                            {getScoreLabel(item.value)}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="factor-empty-text">
                      현재 표시할 하락 요인이 없습니다.
                    </div>
                  )}
                </div>

                <div className="factor-list-block pdf-factor-detail">
                  <ul>
                    {(result?.factors?.negative ?? []).map((item, index) => (
                      <li key={index}>{item.message}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="factor-highlight-card positive-highlight">
                <div className="factor-badge positive-badge">상대적으로 양호한 요인</div>

                <div className="factor-head">
                  <div className="factor-circle positive-circle">양호</div>
                </div>

                <div className="factor-box">
                  {(result?.factors?.positive ?? []).length > 0 ? (
                    (result?.factors?.positive ?? []).slice(0, 3).map((item, index) => (
                      <div key={index} className="factor-box-line">
                        <span>{item.title}</span>
                        <div className="factor-meta">
                          <strong>{formatScore(item.value)}</strong>
                          <span className={`factor-score-label ${getScoreLabel(item.value)}`}>
                            {getScoreLabel(item.value)}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="factor-empty-text">
                      현재 표시할 양호 요인이 없습니다.
                    </div>
                  )}
                </div>

                <div className="factor-list-block pdf-factor-detail">
                  <ul>
                    {(result?.factors?.positive ?? []).map((item, index) => (
                      <li key={index}>{item.message}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="analysis-summary-section pdf-section pdf-keep-together">
        <div className="analysis-summary-card">
          <div className="analysis-summary-header">
            <h2 className="section-title">종합 해석 요약</h2>
            <p className="section-description">
              현재 입력값과 계산 결과를 바탕으로 주요 위험 요인을 정리한 요약입니다.
            </p>
          </div>

          <div className="analysis-summary-list">
            {analysisSummary.length > 0 ? (
              analysisSummary.map((message, index) => (
                <div key={index} className="analysis-summary-item">
                  <span className="analysis-summary-dot">•</span>
                  <p>{message}</p>
                </div>
              ))
            ) : (
              <div className="analysis-summary-empty">
                현재 표시할 분석 요약이 없습니다.
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="compare-section pdf-section">
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
              <p>{formatDiffText(jobAvg?.difference_from_user, jobAvg?.direction)}</p>
              <p>
                직종환경이 비슷한 평균과 비교해 고용안정성, 근로시간,
                임금수준 항목의 상대적 위치를 확인할 수 있습니다.
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
              <p>{formatDiffText(ageAvg?.difference_from_user, ageAvg?.direction)}</p>
              <p>
                동일 연령대 평균과 비교해 현재 노동환경 상태를 직관적으로 확인할 수 있습니다.
              </p>
            </div>
          </div>
        </div>

        <ComparisonSummaryCard comparisons={result?.comparisons} />

        {genderData && (
          <div className="gender-compare-card">
            <h3 className="section-subtitle">참고 비교 정보</h3>

            <div className="gender-card">
              <div className="gender-title">{genderData.group_name}</div>

              <div className="gender-info">
                <div>평균 근로시간: {genderData.avg_work_hours}시간</div>
                <div>평균 임금: {genderData.avg_wage?.toLocaleString()}원</div>
              </div>

              <p className="gender-note">* 동일 성별 평균 기준 참고 정보입니다.</p>
            </div>
          </div>
        )}
      </section>

      {aiResult && (
        <section className="pdf-section">
          <AIReportCard
            aiResult={aiResult}
            onMoveSimulation={() => {}}
          />
        </section>
      )}

      <section className="pdf-section">
        <SimulationSection
          simulation={result?.simulation}
          activeSimulationId=""
        />
      </section>

      <section className="pdf-section">
        <AIPolicyCard
          rag={result?.rag}
          ragAIResult={ragAIResult}
          ragAILoading={false}
          ragAIError={ragAIError}
          onLoadRagAI={() => {}}
        />
      </section>

      <div className="result-footer-note pdf-footer">
        ※ 본 결과는 참고용 분석 자료이며, 법적 판단을 대체하지 않습니다.
      </div>
    </div>
  </div>
</div>
    </div>
  );
}

export default ResultPage;