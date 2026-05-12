import { useEffect, useState } from "react";
import Step1Page from "./pages/Step1Page.jsx";
import Step2Page from "./pages/Step2Page.jsx";
import ResultPage from "./pages/resultpage.jsx";
import IntroSection from "./components/IntroSection.jsx";

function App() {

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL;

    // 백엔드 서버 
    fetch(`${apiUrl}/api/health`)
      .catch(() => {});

    // AI 엔드포인트
    fetch(`${apiUrl}/api/ai/interpret`, {
      method: "OPTIONS",
    }).catch(() => {});

    fetch(`${apiUrl}/api/ai/rag`, {
      method: "OPTIONS",
    }).catch(() => {});
  }, []);

  const [step, setStep] = useState(1);
  const [result, setResult] = useState(null);

  const [formData, setFormData] = useState({
    age_group: "",
    gender: "",
    industry: "",
    employment_type: "",
    work_hours: "",
    wage: "",
    stress_level: "",
    physical_level: "",
  });

  const handleChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleAnalysisComplete = (data) => {
    setResult(data);
    setStep(3);
  };

  const handleGoToResult = () => {
    setStep(4);
  };

  const handleReset = () => {
    setResult(null);
    setStep(1);
  };

  return (
    <>
      {step === 1 && (
        <Step1Page
          formData={formData}
          onChange={handleChange}
          onNext={() => setStep(2)}
        />
      )}

      {step === 2 && (
        <Step2Page
          formData={formData}
          onChange={handleChange}
          onPrev={() => setStep(1)}
          onComplete={handleAnalysisComplete}
        />
      )}

      {step === 3 && <IntroSection onStart={handleGoToResult} />}

      {step === 4 && (
        <ResultPage
          result={result}
          formData={formData}
          onRestart={handleReset}
        />
      )}
    </>
  );
}

export default App;