import os, json, time, zipfile, io
from pathlib import Path
from datetime import datetime
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
API_KEY = os.environ.get('DART_API_KEY', '').strip()
BASE = 'https://opendart.fss.or.kr/api'
COMPANY = {'name':'삼성전자','corp_code':'00126380','stock_code':'005930'}
PEERS = [
 {'name':'SK하이닉스','stock_code':'000660','corp_code':'00164779','note':'메모리 반도체'},
 {'name':'LG전자','stock_code':'066570','corp_code':'00401731','note':'전자·가전'},
 {'name':'삼성SDI','stock_code':'006400','corp_code':'00126362','note':'배터리·전자재료'},
 {'name':'LG디스플레이','stock_code':'034220','corp_code':'00401731','note':'디스플레이'},
 {'name':'한미반도체','stock_code':'042700','corp_code':'003 เว็บไซต์','note':'반도체 장비'}
]
# DART report codes: annual, half-year, Q1, Q3
REPORTS = [('annual','사업보고서','11011'),('half-year','반기보고서','11012'),('quarterly','1분기보고서','11013'),('quarterly','3분기보고서','11014')]

def get_json(path, params, retries=4):
    params = dict(params, crtfc_key=API_KEY)
    for attempt in range(retries):
        r = requests.get(f'{BASE}/{path}', params=params, timeout=45)
        r.raise_for_status(); payload = r.json()
        if payload.get('status') == '000': return payload
        if payload.get('status') in ('013','020'): return payload
        if payload.get('status') == '020': raise RuntimeError('DART API 호출 한도 초과')
        if payload.get('status') == '010': raise RuntimeError('DART_API_KEY가 올바르지 않거나 권한이 없습니다.')
        if attempt == retries-1: raise RuntimeError(f'DART API 오류: {payload}')
        time.sleep(2**attempt)
    return {}

def number(v):
    try: return float(str(v).replace(',','').strip())
    except (ValueError, TypeError): return None

def main():
    if not API_KEY: raise SystemExit('환경변수 DART_API_KEY를 설정하세요. GitHub Actions에서는 Repository Secrets에 저장합니다.')
    DATA.mkdir(exist_ok=True)
    rows=[]; filings=[]
    now_year=datetime.now().year
    # Quarterly and half-year reports can appear in the following year; search from 2010 through current year.
    for year in range(2010, now_year+1):
        for category, report_name, reprt_code in REPORTS:
            p=get_json('fnlttSinglAcntAll.json', {'corp_code':COMPANY['corp_code'],'bsns_year':str(year),'reprt_code':reprt_code,'fs_div':'CFS'})
            if p.get('status') == '013':
                p=get_json('fnlttSinglAcntAll.json', {'corp_code':COMPANY['corp_code'],'bsns_year':str(year),'reprt_code':reprt_code,'fs_div':'OFS'})
            if p.get('status') != '000': continue
            for x in p.get('list',[]):
                account=x.get('account_nm','')
                if account not in ('매출액','영업이익','당기순이익','자산총계','부채총계','자본총계','유동자산','유동부채','현금및현금성자산','영업활동현금흐름','이자비용'): continue
                rows.append({'year':year,'period_type':category,'report_name':report_name,'reprt_code':reprt_code,'account':account,'account_id':x.get('account_id'),'fs_div':x.get('fs_div'),'fs_nm':x.get('fs_nm'),'sj_div':x.get('sj_div'),'thstrm_nm':x.get('thstrm_nm'),'thstrm_amount':number(x.get('thstrm_amount')),'frmtrm_amount':number(x.get('frmtrm_amount')),'currency':'KRW','unit':'원'})
            time.sleep(.08)
        # Filing list is used for report links and audit trail.
        try:
            fp=get_json('list.json', {'corp_code':COMPANY['corp_code'],'bgn_de':f'{year}0101','end_de':f'{year}1231','page_count':'100'})
            for f in fp.get('list',[]):
                if f.get('pblntf_ty') == 'A' and any(k in f.get('report_nm','') for k in ('사업보고서','반기보고서','분기보고서')):
                    filings.append({'year':year,'report_nm':f.get('report_nm'),'rcept_no':f.get('rcept_no'),'rcept_dt':f.get('rcept_dt'),'url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+str(f.get('rcept_no'))})
        except Exception as e: print(f'공시 목록 경고({year}): {e}')
    # Normalize one record per report/year/account; retain data as delivered by DART.
    rows.sort(key=lambda r:(r['year'],r['period_type'],r['account']))
    docs_data = ROOT / 'docs' / 'data'
    docs_data.mkdir(parents=True, exist_ok=True)
    financials_text = json.dumps(rows,ensure_ascii=False,indent=2)
    filings_text = json.dumps(sorted(filings,key=lambda f:(f['rcept_dt'] or '',f['report_nm'])),ensure_ascii=False,indent=2)
    (DATA/'financials.json').write_text(financials_text,encoding='utf-8')
    (DATA/'filings.json').write_text(filings_text,encoding='utf-8')
    (docs_data/'financials.json').write_text(financials_text,encoding='utf-8')
    (docs_data/'filings.json').write_text(filings_text,encoding='utf-8')
    meta={'company':COMPANY,'updated_at':datetime.now().astimezone().isoformat(),'from_year':2010,'to_year':now_year,'record_count':len(rows),'filing_count':len(filings),'source':'OpenDART','notes':'CFS 우선, 연결재무제표가 없을 때 OFS를 조회. 재무비율은 동일 보고서 내 항목이 모두 존재할 때만 계산.'}
    metadata_text = json.dumps(meta,ensure_ascii=False,indent=2)
    (DATA/'metadata.json').write_text(metadata_text,encoding='utf-8')
    (docs_data/'metadata.json').write_text(metadata_text,encoding='utf-8')
    print(f'완료: {len(rows)} 재무 항목, {len(filings)} 공시')
if __name__=='__main__': main()
