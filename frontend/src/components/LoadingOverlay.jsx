import logoImg from "../assets/logo.png";
import "../styles/loadingOverlay.css";

export default function LoadingOverlay({
  title = "분석 중입니다",
  message = "잠시만 기다려주세요.",
}) {
  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <img
          src={logoImg}
          alt="ILLO 로고"
          className="loading-logo"
        />

        <div className="loading-spinner" />

        <h3>{title}</h3>
        <p>{message}</p>
      </div>
    </div>
  );
}