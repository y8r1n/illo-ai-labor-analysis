import logoImg from "../assets/logo.png";
import "../styles/intro.css";

function IntroSection({ onStart }) {
  return (
    <div className="intro-page">
      <div className="intro-shell">
        <div className="intro-left">
          <img src={logoImg} alt="ILLO 로고" className="intro-logo-image" />
          <p className="intro-logo-subtext">
            AI 기반 노동환경 점수 분석 및 과로 위험 판단 보조 시스템
          </p>
        </div>

        <div className="intro-divider" />

        <div className="intro-right">
          <div className="intro-block">
            <h2 className="intro-title">노동환경 점수는 이렇게 산정됩니다</h2>

            <div className="intro-item-grid">
              <div className="intro-item">
                <span className="intro-item-key">고용안정성</span>
                <span className="intro-item-value">
                  고용형태를 바탕으로 고용의 안정 수준을 반영합니다.
                </span>
              </div>

              <div className="intro-item">
                <span className="intro-item-key">업종환경</span>
                <span className="intro-item-value">
                  업종별 위험도 차이를 보정값 형태로 반영합니다.
                </span>
              </div>

              <div className="intro-item">
                <span className="intro-item-key">근로시간</span>
                <span className="intro-item-value">
                  기준 근로시간 160시간과의 차이를 기준으로 점수화합니다.
                </span>
              </div>

              <div className="intro-item">
                <span className="intro-item-key">임금수준</span>
                <span className="intro-item-value">
                  임금 수준은 전체 최대 임금 대비 상대 점수로 계산됩니다.
                </span>
              </div>

              <div className="intro-item">
                <span className="intro-item-key">회복여건</span>
                <span className="intro-item-value">
                  체력 수준과 휴게시간 확보 수준을 함께 반영하여 회복 가능성을 평가합니다.
                </span>
              </div>

              <div className="intro-item">
                <span className="intro-item-key">업무부담</span>
                <span className="intro-item-value">
                  스트레스 수준과 근무패턴을 함께 반영하여 현재 부담 정도를 평가합니다.
                </span>
              </div>
            </div>
          </div>

          <div className="intro-block">
            <h3 className="intro-subtitle">유의사항</h3>
            <p className="intro-note">
              본 결과는 참고용 분석 자료이며, 법적 판단을 대체하지 않습니다.
            </p>
            <p className="intro-note">
              점수와 위험지수는 입력 정보 및 데이터 기반 모델에 따라 산출됩니다.
            </p>
            <p className="intro-note">
              세부 결과는 노동환경 개선 방향을 탐색하기 위한 보조 자료로 활용할 수 있습니다.
            </p>
            <p className="intro-note">
              본 시스템은 과로 위험 판단을 보조하기 위한 도구이며, 최종 판단은 전문가의 평가와 법적 기준에 따라 이루어져야 합니다.
            </p>
          </div>

          <div className="intro-button-row">
            <button
              className="intro-start-button"
              onClick={() => {
                window.scrollTo(0, 0);
                onStart();
              }}
            >
              분석 시작하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default IntroSection;