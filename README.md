# 삼성전자 OpenDART 재무 분석 Agent

[![🔗 대시보드 바로가기](https://img.shields.io/badge/🔗-대시보드%20바로가기-315EFB?style=for-the-badge)](https://hsc-class02.github.io/sj_samsung1/)

삼성전자(005930)의 OpenDART 공시에서 2010년 이후 사업보고서·반기보고서·분기보고서의 주요 재무계정을 수집하고, GitHub Actions로 매월 1일 자동 갱신하며 GitHub Pages 대시보드로 시각화하는 프로젝트입니다.

## 대시보드

- **Dashboard:** https://hsc-class02.github.io/sj_samsung1/
- **OpenDART:** https://opendart.fss.or.kr/
- **저장소:** https://github.com/HSC-Class02/sj_samsung1

> 위 Pages 주소는 저장소 설정에서 GitHub Pages가 활성화된 후에 공개됩니다. 이 ZIP 파일만으로 원격 저장소의 About/README 설정이나 배포를 대신 완료할 수는 없습니다.

## 빠른 설치

1. ZIP 압축을 풉니다. `.github/workflows/update.yml`은 월간 자동 실행에 꼭 필요한 GitHub Actions 설정입니다.
2. 이 프로젝트의 파일들을 `HSC-Class02/sj_samsung1` 저장소의 기본 브랜치(`main`)에 업로드합니다. 기존 파일이 있다면 먼저 비교·병합하세요.
3. OpenDART에서 API 인증키를 발급받습니다: https://opendart.fss.or.kr/  
4. GitHub 저장소에서 **Settings → Secrets and variables → Actions → New repository secret**으로 이동합니다.
   - Name: `DART_API_KEY`
   - Secret: 발급받은 OpenDART 인증키
   - API 키는 코드, README, 공개 파일에 직접 입력하지 마세요.
5. **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions`를 선택하고 저장합니다.
6. **Actions** 탭에서 `Update Samsung DART financial data`를 선택한 뒤 **Run workflow**로 최초 실행합니다.
7. **Settings → Pages**에서 `Deploy from a branch`를 선택하고 branch `main`, folder `/docs`로 저장합니다.
8. 저장소 페이지의 **About → 톱니바퀴**에서 Website에 `https://hsc-class02.github.io/sj_samsung1/`를 입력하고 저장합니다.

## 자동 업데이트

`.github/workflows/update.yml`의 `cron: '15 0 1 * *'`은 UTC 기준 매월 1일 00:15, 한국 시간(KST) 매월 1일 09:15에 실행됩니다. GitHub Actions는 부하에 따라 예약 작업이 지연될 수 있습니다. 수동 실행은 `workflow_dispatch`로 가능합니다.

## 수집 계정 및 비율

기본 계정: 매출액, 영업이익, 당기순이익, 자산총계, 부채총계, 자본총계, 유동자산, 유동부채, 현금및현금성자산, 영업활동현금흐름, 이자비용.

- 영업이익률 = 영업이익 ÷ 매출액 × 100
- 순이익률 = 당기순이익 ÷ 매출액 × 100
- 부채비율 = 부채총계 ÷ 자본총계 × 100
- 유동비율 = 유동자산 ÷ 유동부채 × 100
- 자기자본비율 = 자본총계 ÷ 자산총계 × 100

연결재무제표(CFS)를 먼저 조회하고, 연결 자료가 없으면 별도재무제표(OFS)를 조회합니다. 분기·반기 보고서의 당기 값은 누적 금액일 수 있으므로 연간 값과 무조건 더하지 마세요. 데이터 원본은 `data/financials.json`, 공시 링크는 `data/filings.json`이며, Pages 배포를 위해 `docs/data/`에도 동일한 JSON을 복사합니다.

## 국내 Peer Firms

| 기업 | 종목코드 | 비교 관점 |
|---|---:|---|
| SK하이닉스 | 000660 | 메모리 반도체 |
| LG전자 | 066570 | 전자·가전 |
| 삼성SDI | 006400 | 배터리·전자재료 |
| LG디스플레이 | 034220 | 디스플레이 패널 |
| 한미반도체 | 042700 | 반도체 제조 장비 |

비교 기업은 산업 참고용이며 삼성전자와 사업 구성이 완전히 동일하지 않습니다. 기업 간 비교 시 회계 기준, 연결/별도 여부, 보고기간을 맞추세요.

## 검증 메모 및 문제 해결

- workflow 파일은 YAML 문법과 GitHub Actions 문법을 단순하게 유지했습니다. GitHub에서 실제 실행 후 `Actions` 로그를 확인해야 합니다.
- API 인증키 누락/오류 시 workflow의 수집 단계가 실패합니다. `DART_API_KEY` secret 이름과 값이 정확한지 확인하세요.
- `data/`가 비어 있거나 업데이트되지 않으면 Actions 권한(`Read and write permissions`)과 API 요청 한도를 확인하세요.
- API 데이터 구조 및 계정명은 시점/보고서별로 다를 수 있습니다. 현재 기본 계정명 필터에 맞지 않는 표기 변형은 별도 조정이 필요합니다.
- 첨부파일에 지정된 재무항목 목록은 이 작업 세션에서 확인되지 않아 일반적인 핵심 재무 계정을 기본값으로 설정했습니다. 첨부파일의 실제 항목과 대조해 `config/metrics.json` 및 `src/update_data.py`의 계정 필터를 수정하세요.
