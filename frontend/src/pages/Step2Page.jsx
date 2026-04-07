import axios from "axios";
import logoImg from "../assets/logo.png";
import "../styles/step.css";

function Step2Page({ formData, onChange, onPrev, onComplete }) {
  const isValid =
    formData.work_hours &&
    formData.wage &&
    formData.stress_level &&
    formData.physical_level;

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/api/analyze", {
        age_group: formData.age_group,
        industry: formData.industry,
        employment_type: formData.employment_type,
        work_hours: Number(formData.work_hours),
        wage: Number(formData.wage),
        stress_level: formData.stress_level,
        physical_level: formData.physical_level,
      });

      onComplete(res.data.data);
    } catch (err) {
      console.error("분석 요청 실패:", err);
      alert("분석 요청 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="step-page">
      <div className="step-shell">
        <div className="step-card">
          <div className="step-left">
            <img src={logoImg} alt="ILLO 로고" className="step-logo-image" />
            <p className="step-logo-subtext">
              AI 기반 노동환경 점수 분석 및 과로 위험 판단 보조 시스템
            </p>
          </div>

          <div className="step-right">
            <h1 className="step-title">추가 정보를 입력해 주세요!</h1>
            <p className="step-subtitle">
              근로시간, 급여, 스트레스와 체력 정보를 입력하면 분석을 시작합니다.
            </p>

            <div className="step-form-grid">
              <div className="step-field">
                <label className="step-label">월 근로시간</label>
                <input
                  className="step-input"
                  type="number"
                  value={formData.work_hours}
                  onChange={(e) => onChange("work_hours", e.target.value)}
                  placeholder="예: 160"
                />
              </div>

              <div className="step-field">
                <label className="step-label">월 급여액</label>
                <input
                  className="step-input"
                  type="number"
                  value={formData.wage}
                  onChange={(e) => onChange("wage", e.target.value)}
                  placeholder="예: 3000000 (세후 금액)"
                />
              </div>

              <div className="step-field">
                <label className="step-label">평소 스트레스 지수</label>
                <select
                  className="step-select"
                  value={formData.stress_level}
                  onChange={(e) => onChange("stress_level", e.target.value)}
                >
                  <option value="">선택하세요</option>
                  <option value="낮음">낮음</option>
                  <option value="보통">보통</option>
                  <option value="높음">높음</option>
                </select>
              </div>

              <div className="step-field">
                <label className="step-label">평소 체력 수준</label>
                <select
                  className="step-select"
                  value={formData.physical_level}
                  onChange={(e) => onChange("physical_level", e.target.value)}
                >
                  <option value="">선택하세요</option>
                  <option value="낮음">낮음</option>
                  <option value="보통">보통</option>
                  <option value="높음">높음</option>
                </select>
              </div>
            </div>

            <div className="step-button-row">
              <button className="step-secondary-button" onClick={onPrev}>
                이전
              </button>

              <button
                className="step-primary-button"
                onClick={handleSubmit}
                disabled={!isValid}
              >
                분석하기
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Step2Page;