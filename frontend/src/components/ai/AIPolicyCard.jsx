import "../../styles/AIPolicyCard.css";

function AIPolicyCard({
  rag,
  ragAIResult,
  ragAILoading,
  ragAIError,
  onLoadRagAI,
}) {
  const explanations = rag?.matched_explanations ?? [];
  const policies = rag?.recommended_policies ?? [];

  const hasRag = explanations.length > 0 || policies.length > 0;

  const aiPolicyMap = Object.fromEntries(
    (ragAIResult?.policy_cards ?? []).map((p) => [p.policy_name, p])
  );

  const defaultRiskFlow =
    (ragAIResult?.explanation_cards?.[0]?.risk_flow?.length
      ? ragAIResult.explanation_cards[0].risk_flow
      : explanations?.[0]?.risk_links) ?? [];

  return (
    <section className="rag-policy-section">
      <div className="rag-policy-card">
        <div className="rag-policy-header">
          <div>
            <span className="rag-policy-kicker">RAG 기반 매칭</span>
            <h2 className="rag-policy-title">맞춤 해석 및 정책 추천</h2>
            <p className="rag-policy-description">
              주요 위험 요인과 입력 조건을 바탕으로 관련 설명과 정책을 매칭한 결과입니다.
            </p>
          </div>

          <button
            className="rag-ai-button"
            onClick={onLoadRagAI}
            disabled={ragAILoading || !hasRag}
          >
            {ragAILoading ? "생성 중..." : 'AI로 "왜 이 정책인지" 설명 보기'}
          </button>
        </div>

        {ragAILoading && (
          <div className="rag-status-card">정책 AI 설명 생성 중...</div>
        )}

        {ragAIError && !ragAIResult && (
          <div className="rag-status-card error">{ragAIError}</div>
        )}

        {ragAIResult && (
          <div className="rag-ai-result-card">
            <div className="rag-ai-result-header">
              <span className="rag-ai-badge">AI 해석</span>
              <h3>정책 추천 설명</h3>
            </div>

            <p className="rag-ai-summary">{ragAIResult.rag_summary}</p>

            {(ragAIResult.explanation_cards ?? []).length > 0 && (
              <div className="rag-ai-mini-list">
                {(ragAIResult.explanation_cards ?? []).map((item, index) => (
                  <div key={index} className="rag-ai-mini-card">
                    <strong>{item.title}</strong>
                    <p>{item.ai_comment}</p>
                  </div>
                ))}
              </div>
            )}

            {(ragAIResult.policy_cards ?? []).length > 0 && (
              <div className="rag-ai-policy-list">
                {(ragAIResult.policy_cards ?? []).map((policy, index) => (
                  <div key={index} className="rag-ai-policy-card">
                    <div className="rag-ai-policy-rank">{index + 1}</div>
                    <div>
                      <strong>{policy.policy_name}</strong>
                      <p>{policy.recommendation_reason}</p>
                      <p className="rag-ai-howto">{policy.how_to_use}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="rag-policy-grid">
          <div className="rag-policy-block">
            <div className="rag-block-title-row">
              <h3>관련 해석</h3>
              <span>{explanations.length}개</span>
            </div>

            {explanations.length > 0 ? (
              <div className="rag-explanation-list">
                {explanations.map((item) => (
                  <article
                    key={item.explanation_id}
                    className="rag-explanation-card"
                  >
                    <h4>{item.title}</h4>
                    <p>{item.summary}</p>

                    <ul>
                      {(item.core_points ?? []).slice(0, 3).map((point, index) => (
                        <li key={index}>{point}</li>
                      ))}
                    </ul>

                    <div className="rag-risk-flow">
                      {(item.risk_links ?? []).map((link, index) => (
                        <span key={index} className="rag-risk-chip">
                          {link}
                        </span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="rag-empty">현재 매칭된 해석이 없습니다.</div>
            )}
          </div>

          <div className="rag-policy-block">
            <div className="rag-block-title-row">
              <h3>추천 정책 Top 3</h3>
              <span>{policies.length}개</span>
            </div>

            {policies.length > 0 ? (
              <div className="rag-policy-list">
                {policies.map((policy, index) => {
                  const aiPolicy = aiPolicyMap[policy.policy_name];

                  const policyRiskFlow =
                    aiPolicy?.risk_flow?.length
                      ? aiPolicy.risk_flow
                      : policy.risk_links?.length
                      ? policy.risk_links
                      : defaultRiskFlow;

                  const riskFlowText =
                    aiPolicy?.risk_flow_text ||
                    (policyRiskFlow.length > 0
                      ? `${policyRiskFlow.join(" → ")} 흐름이 확인되어, 예방 차원에서 해당 정책을 검토할 수 있습니다.`
                      : "");

                  return (
                    <article key={policy.policy_id} className="rag-policy-item">
                      <div className="rag-policy-rank">{index + 1}순위</div>

                      <h4>{policy.policy_name}</h4>
                      <p>{policy.summary}</p>

                      {aiPolicy?.recommendation_reason && (
                        <div className="rag-policy-reason">
                          <strong>💡 추천 이유</strong>
                          <p>{aiPolicy.recommendation_reason}</p>
                        </div>
                      )}

                      {riskFlowText && (
                        <div className="rag-policy-flow-text">
                          <strong>🔗 위험 흐름</strong>
                          <p>{riskFlowText}</p>
                        </div>
                      )}

                      <div className="rag-policy-type">
                        {(policy.policy_type ?? []).map((type) => (
                          <span key={type}>{type}</span>
                        ))}
                      </div>

                      <div className="rag-policy-benefit">
                        <strong>지원 내용</strong>
                        <ul>
                          {(policy.benefit ?? [])
                            .slice(0, 3)
                            .map((benefit, idx) => (
                              <li key={idx}>{benefit}</li>
                            ))}
                        </ul>
                      </div>

                      <p className="rag-policy-apply">
                        <strong>신청 방법</strong>
                        <br />
                        {policy.apply_method}
                      </p>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="rag-empty">현재 추천 가능한 정책이 없습니다.</div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export default AIPolicyCard;