# ILLO

AI 기반 노동환경 분석 및 과로 위험 판단 보조 서비스

---

## 프로젝트 소개

ILLO는 공공데이터와 생성형 AI를 활용하여  
사용자의 노동환경을 분석하고 과로 위험을 정량적으로 판단할 수 있도록 설계된 서비스입니다.

기존 서비스가 단순 통계 제공 또는 일자리 추천에 집중되어 있는 것과 달리,  
ILLO는 근로시간, 임금 수준, 고용 형태, 업종 위험도 등을 기반으로  
노동환경 위험도를 계산하고 AI 해석 및 정책 추천까지 연결하는 구조를 제공합니다.

특히 공공데이터를 단순 시각화하는 수준을 넘어  
실제 서비스 로직에 적용 가능한 형태로 전처리 및 구조화하여 활용한 것이 특징입니다.

---

## 핵심 기능

### 노동환경 위험도 분석
- 근로시간 / 임금 / 고용형태 / 업종 위험도 기반 분석
- 노동강도지수(Workload Index) 계산
- 위험군 분류 (양호 / 보통 / 주의 / 위험 / 과로위험)

### AI 해석 리포트
- 생성형 AI 기반 결과 해석
- 위험 원인 분석
- 사용자 상황 기반 설명 제공

### 정책 추천 (RAG)
- 노동환경 상태 기반 정책 추천
- 지원 제도 및 개선 가이드 연결
- 정책 추천 AI 설명 제공

### 노동환경 개선 시뮬레이션
- 근로시간 조정 시 변화 분석
- 노동환경 개선 방향 제시

### PDF 결과 리포트
- 결과 페이지 PDF 저장
- AI 해석 및 정책 추천 포함 출력 지원

---

## 기술 스택

### Frontend
- React
- Vite
- Recharts
- Axios

### Backend
- Flask
- Pandas
- Flask-CORS

### AI
- OpenAI API
- RAG 기반 정책 추천 구조

### Deploy
- Vercel
- Render

---

## 데이터 활용

ILLO는 아래 공공데이터를 활용하여 노동환경 분석 구조를 설계하였습니다.

- 공공데이터포털(Data.go.kr)
- 고용노동 행정통계(EIS)
- 고용노동부 노동통계
- 산업재해 통계
- 근로환경 및 노무관리 자료

활용 데이터는 근로시간, 임금 수준, 고용 형태, 업종 위험도 등을 기준으로
전처리 및 정규화 과정을 거쳐 분석 모델에 반영되었습니다.

또한 공공데이터 기반 평균값과 사용자 입력 데이터를 비교 분석하여
노동환경 위험 수준을 정량적으로 산출하도록 설계하였습니다.

---

## 서비스 차별성

- 노동환경 위험도를 정량적으로 계산하는 구조
- 단순 챗봇이 아닌 AI 해석 및 정책 연결 구조
- 공공데이터 기반 비교 분석 제공
- 위험 원인 분석 및 개선 방향 제시
- RAG 기반 정책 추천 시스템 구축

---

## 기대 효과

- 노동환경 위험에 대한 객관적 인식 제공
- 과로 위험 예방 및 개선 방향 제시
- 데이터 기반 노동환경 관리 지원
- 향후 기업 및 공공기관 노동환경 관리 지표로 활용 가능
- 정책 및 제도 연결 기반 예방 중심 서비스 확장 가능

---

## 배포 링크

### Frontend
https://illo-one.vercel.app

### Backend
https://illo-ai-labor-analysis.onrender.com

---

## 프로젝트 문서

### Notion Workspace
https://elated-dessert-bb9.notion.site/ILLO-AI-SERVICE-5-AI-32722f06a9ce80d7bbc4fd6ceb2a8baf

---

## 프로젝트 구조

```bash
frontend/
backend/
backend/data/
backend/data/rag/
backend/app/services/
backend/outputs/

---

## 개발자
이예린

Full Stack Developer

공공데이터 분석 구조 설계
노동강도지수 계산 엔진 구현
AI 해석 시스템 구축
RAG 데이터 구조 설계
프론트엔드 UI/UX 개발
백엔드 API 구축
PDF 리포트 시스템 구현
Vercel / Render 배포

Mail : yesrin14@gmail.com

GitHub :
https://github.com/y8r1n/illo-ai-labor-analysis
Notion : 
https://elated-dessert-bb9.notion.site/ILLO-AI-SERVICE-5-AI-32722f06a9ce80d7bbc4fd6ceb2a8baf?pvs=74
