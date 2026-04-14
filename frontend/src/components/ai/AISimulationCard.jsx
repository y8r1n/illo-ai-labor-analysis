import { useEffect, useState } from "react";
import "../../styles/SimulationSection.css";

function CircularProgress({ before = 0, after = 0 }) {
  const safeBefore = Math.max(0, Math.min(100, before));
  const safeAfter = Math.max(0, Math.min(100, after));

  const [animatedBefore, setAnimatedBefore] = useState(0);
  const [animatedAfter, setAnimatedAfter] = useState(0);
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      setAnimatedBefore(safeBefore);
      setAnimatedAfter(safeAfter);
    });
    return () => cancelAnimationFrame(frame);
  }, [safeBefore, safeAfter]);

  useEffect(() => {
    let start = 0;
    const end = safeAfter;
    const duration = 900;
    let animationFrameId;

    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const value = progress * end;
      setDisplayScore(value);

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [safeAfter]);

  const radius = 78;
  const stroke = 12;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;

  const beforeOffset =
    circumference - (animatedBefore / 100) * circumference;
  const afterOffset =
    circumference - (animatedAfter / 100) * circumference;

  return (
    <div className="sim-circle-wrap">
      <svg
        className="sim-circle-svg"
        width={radius * 2}
        height={radius * 2}
      >
        <circle
          className="sim-circle-track"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          fill="transparent"
        />
        <circle
          className="sim-circle-before"
          strokeWidth={stroke}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={beforeOffset}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          fill="transparent"
        />
        <circle
          className="sim-circle-after"
          strokeWidth={stroke}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={afterOffset}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          fill="transparent"
        />
      </svg>

      <div className="sim-circle-center">
        <div className="sim-circle-after-score">{displayScore.toFixed(1)}</div>
        <div className="sim-circle-center-label">개선 후 점수</div>
      </div>
    </div>
  );
}

function SubSimulationBar({ item, maxDiff }) {
  const widthPercent =
    maxDiff > 0 ? Math.max(12, (item.score_diff / maxDiff) * 100) : 12;

 const labelMap = {
  rest_work_pattern: "휴식·근무패턴",
  employment_stability: "고용안정성",
};

  const typeLabel = labelMap[item.type] || item.title;

  return (
    <div className="sim-sub-card">
      <div className="sim-sub-top">
        <div className="sim-sub-title">{typeLabel}</div>
        <div className="sim-sub-diff">+{(item.score_diff * 100).toFixed(1)}</div>
      </div>

      <div className="sim-sub-change">
        {item.before} → {item.after}
      </div>

      <div className="sim-sub-bar-track">
        <div
          className="sim-sub-bar-fill"
          style={{ width: `${widthPercent}%` }}
        />
      </div>

      <div className="sim-sub-message">{item.message}</div>
    </div>
  );
}

export default function SimulationSection({ simulation, activeSimulationId }) {
  if (!simulation) return null;

  const main = simulation.main;
  const sub = [...(simulation.sub || [])].sort(
    (a, b) => (b.score_diff || 0) - (a.score_diff || 0)
  );

   const beforePercent = (main?.current_score || 0) * 100;
  const afterPercent = (main?.improved_score || 0) * 100;
  const diffPercent = (main?.score_diff || 0) * 100;

  const diffLabel =
    Math.abs(diffPercent) < 0.05
      ? "변화 없음"
      : `+${diffPercent.toFixed(1)} 개선`;

  const mainReason =
    Number(main?.before) === Number(main?.after)
      ? "현재 근로시간이 기준값과 동일하여 추가 개선 효과가 없습니다."
      : "현재 근로시간을 기준 근로시간에 가깝게 조정할 경우 점수 개선 효과를 기대할 수 있습니다.";

  const maxDiff = Math.max(...sub.map((item) => item.score_diff || 0), 0);

  return (
    <section className="simulation-section">
      <div className="simulation-header">
        <h2 className="simulation-title">노동 환경 개선 시뮬레이션</h2>
        <p className="simulation-subtitle">
          현재 입력값을 기준으로, 조건 변화 시 점수가 어떻게 달라지는지 보여주는 참고 시나리오입니다.
        </p>
      </div>

      <div
  id="simulation-worktime"
  className={`simulation-main-card ${
    activeSimulationId === "simulation-worktime" ? "simulation-highlight" : ""
  }`}
>
        <div className="simulation-main-left">
          <div className="simulation-badge">근로 시간 시뮬레이션</div>
          <h3 className="simulation-main-title">{main?.title || "근로시간 조정"}</h3>
          <p className="simulation-main-desc">{main?.message}</p>

          <div className="simulation-hours-box">
            <div className="simulation-hours-item">
              <span className="simulation-hours-label">현재 근로시간</span>
              <strong className="simulation-hours-value">{main?.before}시간</strong>
            </div>

            <div className="simulation-reason-box">
  {mainReason}
</div>

            <div className="simulation-hours-arrow">→</div>

            <div className="simulation-hours-item">
              <span className="simulation-hours-label">조정 근로시간</span>
              <strong className="simulation-hours-value">{main?.after}시간</strong>
            </div>
          </div>

          <div className="simulation-score-row">
            <div className="simulation-score-box">
              <span className="simulation-score-label">현재 점수</span>
              <strong>{beforePercent.toFixed(1)}</strong>
            </div>

            <div className="simulation-score-arrow">→</div>

            <div className="simulation-score-box simulation-score-box-highlight">
              <span className="simulation-score-label">개선 후 점수</span>
              <strong>{afterPercent.toFixed(1)}</strong>
            </div>

            <div
  className={`simulation-score-diff ${
    Math.abs(diffPercent) < 0.05 ? "is-neutral" : "is-improved"
  }`}
>
  {diffLabel}
</div>
          </div>
        </div>

        <div className="simulation-main-right">
          <CircularProgress before={beforePercent} after={afterPercent} />
        </div>
      </div>

      <div className="simulation-sub-wrapper">
        <div className="simulation-sub-header">
        <div className="simulation-badge">환경 시뮬레이션</div>
          <h3 className="simulation-sub-title">보조 조건 </h3>
          <p className="simulation-sub-desc">
            아래 항목은 자기보고형 상태 또는 조건 변화에 따른 참고 시뮬레이션입니다.
          </p>
        </div>

        <div className="simulation-sub-grid">
         {sub.length > 0 ? (
  sub.map((item, index) => {
    const targetId =
      item.type === "rest_work_pattern"
        ? "simulation-rest"
        : item.type === "employment_stability"
        ? "simulation-employment"
        : undefined;

    return (
      <div
        key={`${item.type}-${index}`}
        id={targetId}
        className={targetId && activeSimulationId === targetId ? "simulation-highlight" : ""}
      >
        <SubSimulationBar item={item} maxDiff={maxDiff} />
      </div>
    );
  })
) : (
  <div className="simulation-empty">
    현재 표시할 보조 시뮬레이션 항목이 없습니다.
  </div>
)}
        </div>
      </div>
    </section>
  );
}