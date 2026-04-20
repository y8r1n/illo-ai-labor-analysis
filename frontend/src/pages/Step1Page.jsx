import logoImg from "../assets/logo.png";
import "../styles/step.css";

function Step1Page({ formData, onChange, onNext }) {
  const isValid =
    formData.age_group &&
    formData.gender &&
    formData.industry &&
    formData.employment_type;

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
            <h1 className="step-title">정보를 입력해 주세요!</h1>
            <p className="step-subtitle">
              기본 정보를 먼저 입력한 뒤 다음 단계로 이동합니다.
            </p>

            <div className="step-form-grid">
              <div className="step-field">
                <label className="step-label">나이</label>
                <select
                  className="step-select"
                  value={formData.age_group}
                  onChange={(e) => onChange("age_group", e.target.value)}
                >
                  <option value="">선택하세요</option>
                  <option value="20대">20대</option>
                  <option value="30대">30대</option>
                  <option value="40대">40대</option>
                  <option value="50대">50대</option>
                  <option value="60대">60대</option>
                </select>
              </div>

              <div className="step-field">
                <label className="step-label">성별</label>
                <select
                  className="step-select"
                  value={formData.gender}
                  onChange={(e) => onChange("gender", e.target.value)}
                >
                  <option value="">선택하세요</option>
                  <option value="남성">남성</option>
                  <option value="여성">여성</option>
                </select>
              </div>

              <div className="step-field">
                <label className="step-label">업종</label>
                <select
                  className="step-select"
                  value={formData.industry}
                  onChange={(e) => onChange("industry", e.target.value)}
                >
                  <option value="">선택하세요</option>
                  <option value="서비스업">서비스업</option>
                  <option value="금융및보험업">금융·보험</option>
                  <option value="광업">광업</option>
                  <option value="제조업">제조업</option>
                  <option value="전기.가스.증기.수도사업">전기·가스·수도</option>
                  <option value="건설업">건설업</option>
                  <option value="운수창고.통신업">운수·창고·통신</option>
                  <option value="임업">임업</option>
                  <option value="어업">어업</option>
                  <option value="농업">농업</option>
                  <option value="기타의사업">기타</option>
                </select>
              </div>

              <div className="step-field">
                <label className="step-label">고용형태</label>
                <select
                  className="step-select"
                  value={formData.employment_type}
                  onChange={(e) => onChange("employment_type", e.target.value)}
                >
                  <option value="">선택하세요</option>
                  <option value="정규근로자">정규근로자</option>
                  <option value="비정규근로자">비정규근로자</option>
                </select>
              </div>
            </div>

            <div className="step-button-right">
              <button
                className="step-primary-button"
                onClick={onNext}
                disabled={!isValid}
              >
                다음
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Step1Page;