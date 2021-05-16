import requests as req
import time

from requests.api import head
from bs4 import BeautifulSoup as bs4
from fake_useragent import UserAgent
from datetime import datetime, timedelta
from pprintpp import pprint as pp
import numpy_financial as npf
import json

# 범용 함수
def soup_single_str(location, soup):
	# 선택자에 해당하는 하나의 값을 가져오는 함수.
	try:
		location = soup.select(location)[0].get_text().replace(u'\xa0', u' ')
	except:
		location = '크롤 실패'
	return location

def soup_tr_match(soup, match1, match2="를훌통", location='tbody tr', n=None):
	tr_list = soup.select(location)
	list = []
	for i in tr_list:
		try:
			th = i.select("th")[0].get_text()
			if match1 in th or match2 in th:
				for j in i.select("td"):
					try: value = round(float(j.get_text().replace(',', '')), n)
					except : value = None
					list.append(value)
				break
		except:
			continue
		
	return list

def toFloat(str, n=None):
	str = str.replace(',', '')
	try:
		result = float(str, n)
	except:
		result = str
	return result

def toInt(str):
	str = str.replace(',', '')
	try:
		result = int(str)
	except:
		result = str
	return result

def yieldRate(currentValue, pastValue):
	result = round(((currentValue-pastValue)/pastValue)*100, 2)
	return result

def yesterday():
	yesterday = datetime.today() - timedelta(1)
	yesterday = yesterday.strftime("%Y-%m-%d")
	return yesterday
def today():
	result = datetime.today().strftime("%Y-%m-%d")
	return result

# 크롤러
def fnSnapshot(stock):
	# fnguide 기업정보 > snapshot
	with req.Session() as s:
		ua = UserAgent()
		headers = {
			'user-agent': ua.random,
			'referer': f'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{stock}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701'
		}
		url = f'https://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{stock}'
		print(url)
		get_url = s.get(url, headers=headers).text
		soup = bs4(get_url, 'html.parser')

		def soup_financial_highlight(location, n=None):
			# 파이넨셜 하이라이트에서 연간/분기의 td항목을 각각 리스트로 반환하는 함수.
			d_year = soup.select('#highlight_D_Y tbody tr:nth-child({}) td'.format(location))
			for idx, val in enumerate(d_year):
				try:
					d_year[idx] = round(float(val.get_text().replace(',', '')), n)
				except ValueError:
					d_year[idx] = None
				except:
					d_year[idx] = '크롤 실패'

			d_quarter = soup.select('#highlight_D_Q tbody tr:nth-child({}) td'.format(location))
			for idx, val in enumerate(d_quarter):
				try:
					d_quarter[idx] = round(float(val.get_text().replace(',', '')), n)
				except ValueError:
					d_quarter[idx] = None
				except:
					d_quarter[idx] = '크롤 실패'
			return d_year, d_quarter

		d_name = soup_single_str('#giName', soup)
		d_market = soup_single_str('#strMarketTxt', soup)
		d_sectors = soup_single_str('.stxt.stxt2', soup)
		d_summary_1 = soup_single_str('#bizSummaryHeader', soup)
		d_summary_2 = soup_single_str('#bizSummaryContent li:first-child', soup)
		d_summary_3 = soup_single_str('#bizSummaryContent li:last-child', soup)
		d_treasury_shares = soup_single_str('#svdMainGrid5 table tr:nth-child(5) td:nth-child(3)', soup)
		try:d_outstanding_shares = int(soup_single_str('#svdMainGrid1 table tr:last-child td:nth-child(2)', soup).split("/")[0].replace(',', ''))
		except: d_outstanding_shares = 0
		try: d_treasury_shares = int(d_treasury_shares)
		except: d_treasury_shares = 0

		d_revenue_year, d_revenue_quarter = soup_financial_highlight('1')
		d_operatingIncome_year, d_operatingIncome_quarter = soup_financial_highlight('3')
		d_profit_year, d_profit_quarter = soup_financial_highlight('5')
		d_equity_year, d_equity_quarter = soup_financial_highlight('10')
		d_ROA_year, d_ROA_quarter = soup_financial_highlight('17', 2)
		d_ROE_year, d_ROE_quarter = soup_financial_highlight('18', 2)
		d_EPS_year, d_EPS_quarter = soup_financial_highlight('19')
		d_PER_year, d_PER_quarter = soup_financial_highlight('22', 2)

		dict = {
			'크롤일자': time.strftime('%Y-%m-%d', time.localtime(time.time())),
			'크롤시간': time.strftime('%p %I:%M:%S', time.localtime(time.time())),
			'기업정보': {
				'기업명': d_name,
				'소속': d_market,
				'업종': d_sectors,
				'핵심요약': d_summary_1,
				'설명1': d_summary_2,
				'설명2': d_summary_3,
				'발행주식수': d_outstanding_shares,
				'자기주식수': d_treasury_shares,
			},
			'재무하이라이트': {
				# year: [4년전, 3년전, 2년전, 1년전, 최근, 1년후(예상 또는 잠정), 2년후(예상), 3년후(예상)]
				# quarter: [4분기전, 3분기전, 2분기전, 1분기전, 최근, 1분기후(예상 또는 잠정), 2분기후(예상), 3분기후(예상)]
				'매출': {
					'year': d_revenue_year,
					'quarter': d_revenue_quarter,
				},
				'영업이익': {
					'year': d_operatingIncome_year,
					'quarter': d_operatingIncome_quarter,
				},
				'순이익': {
					'year': d_profit_year,
					'quarter': d_profit_quarter,
				},
				'자본': {
					'year': d_equity_year,
					'quarter': d_equity_quarter,
				},
				'ROE': {
					'year': d_ROE_year,
					'quarter': d_ROE_quarter,
				},
				'ROA': {
					'year': d_ROA_year,
					'quarter': d_ROA_quarter,
				},
				'EPS': {
					'year': d_EPS_year,
					'quarter': d_EPS_quarter,
				},
				'PER': {
					'year': d_PER_year,
					'quarter': d_PER_quarter,
				},
			}
		}
	pp('크롤완료: 스냅샷')
	return dict

def fnFinance(stock):
	# fnguide 기업정보 > 재무제표
	with req.Session() as s:
		ua = UserAgent()
		headers = {
			'user-agent': ua.random,
			'referer': 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A005930&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701'
		}
		get_url = s.get('https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{}'.format(str(stock)), headers=headers).text
		soup = bs4(get_url, 'html.parser')

		try: d_CF_operating = soup_tr_match(soup, '영업활동으로인한현금흐름', location='#divCashY tbody tr')
		except: d_CF_operating = None
		try: d_CF_investing = soup_tr_match(soup, '투자활동으로인한현금흐름', location='#divCashY tbody tr')
		except: d_CF_investing = None
		try: d_CF_financing = soup_tr_match(soup, '재무활동으로인한현금흐름', location='#divCashY tbody tr')
		except: d_CF_financing = None
		try: d_CF_netIncrease = soup_tr_match(soup, '현금및현금성자산의증가', location='#divCashY tbody tr')
		except: d_CF_netIncrease = None
		try: d_CF_endOfPeriod = soup_tr_match(soup, '기말현금및현금성자산', location='#divCashY tbody tr')
		except: d_CF_endOfPeriod = None

		dict = {
			'현금흐름': {
				'영업활동으로인한현금흐름': d_CF_operating,
				'투자활동으로인한현금흐름': d_CF_investing,
				'재무활동으로인한현금흐름': d_CF_financing,
				'현금및현금성자산의증가': d_CF_netIncrease,
				'기말현금및현금성자산': d_CF_endOfPeriod,
			}
		}
	pp('크롤완료: 재무제표')
	return dict

def fnInvest(stock):
	# fnguide 기업정보 > 재무제표
	with req.Session() as s:
		ua = UserAgent()
		headers = {
			'user-agent': ua.random,
			'referer': 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A005930&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701'
		}
		get_url = s.get('https://comp.fnguide.com/SVO2/ASP/SVD_Invest.asp?pGB=1&gicode=A{}'.format(str(stock)), headers=headers).text
		soup = bs4(get_url, 'html.parser')

		try: d_totalCashflow = soup_tr_match(soup, '총현금흐름')
		except: d_totalCashflow = None
		try: d_totalInvesting = soup_tr_match(soup, '총투자')
		except: d_totalInvesting = None
		try: d_FCFF = soup_tr_match(soup, 'FCFF')
		except: d_FCFF = None

		dict = {
			'잉여현금흐름': {
				'총현금흐름': d_totalCashflow,
				'총투자': d_totalInvesting,
				'FCFF': d_FCFF,
			}
		}
	pp('크롤완료: 투자지표')
	return dict

def fnRatio(stock):
	# fnguide 기업정보 > 재무제표
	with req.Session() as s:
		ua = UserAgent()
		headers = {
			'user-agent': ua.random,
			'referer': 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A005930&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701'
		}
		get_url = s.get('https://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode=A{}'.format(str(stock)), headers=headers).text
		soup = bs4(get_url, 'html.parser')

		try: d_revenueGrowth = soup_tr_match(soup, '매출액증가율', match2='이자수익증가율', n=2)
		except: d_revenueGrowth = None
		try: d_operatingIncomeGrowth = soup_tr_match(soup, '영업이익증가율', n=2)
		except: d_operatingIncomeGrowth = None
		try: d_borrowings = soup_tr_match(soup, '순차입금비율', n=2)
		except: d_borrowings = None
		try: d_interestCoverage = soup_tr_match(soup, '이자보상배율', n=2)
		except: d_interestCoverage = None

		dict = {
			'재무비율': {
				'매출액증가율': d_revenueGrowth,
				'영업이익증가율': d_operatingIncomeGrowth,
				'순차입금비율': d_borrowings,
				'이자보상배율': d_interestCoverage,
			}
		}
	pp('크롤완료: 재무비율')
	return dict

def fnConsensus(stock):
	# fnguide 기업정보 > 컨센서스
	with req.Session() as s:
		ua = UserAgent()
		url = 'https://comp.fnguide.com/SVO2/json/data/01_06/03_A{}.json'.format(stock)
		headers = {
			'user-agent': ua.random,
			'referer': 'https://comp.fnguide.com/SVO2/ASP/SVD_Consensus.asp?pGB=1&gicode=A{}'.format(stock)
			}
		r = json.loads(req.get(url, headers=headers).content.decode('utf-8-sig'))['comp']

		if len(r) == 0:
			r = None
		
		# 'AVG_PRC': 증권사평균 적정가,
		# 'AVG_PRC_BF': 증권사평균 직전 적정가,
		# 'AVG_RECOM_CD': 증권사평균 투자의견,
		# 'AVG_RECOM_CD_BF': 증권사평균 직전 투자의견,
		# 'EST_DT': 추정일자,
		# 'INST_CD': 증권사코드,
		# 'INST_NM': 증권사이름,
		# 'RECOM_CD': 투자의견,
		# 'RECOM_CD_BF': 직전 투자의견,
		# 'TARGET_PRC': 적정가,
		# 'TARGET_PRC_BF': 직전 적정가,
		# 'YOY': 증감율,

		dict = {
			'증권사별적정주가': r,
		}
	pp('크롤완료: 컨센서스')
	return dict

def nvMain(stock):
	# naver 메인
	with req.Session() as s:
		ua = UserAgent()
		headers = {
			'user-agent': ua.random,
			'referer': 'https://finance.naver.com/'
		}
		get_url = s.get('https://finance.naver.com/item/main.nhn?code={}'.format(str(stock)), headers=headers).text
		soup = bs4(get_url, 'html.parser') 

		d_dividendPayout = soup_tr_match(soup, '배당성향(%)', n=2)
		d_dividendYield = soup_tr_match(soup, '시가배당률(%)', n=2)

		dict = {
			'배당': {
				'배당성향': d_dividendPayout,
				'배당수익률': d_dividendYield,
			}
		}
	pp('크롤완료: 네이버 메인배당')
	return dict

def nvPrice(stock):
	# naver 주가
	with req.Session() as s:
		ua = UserAgent()
		url = 'https://m.stock.naver.com/api/item/getTrendList.nhn?code={}&size=30'.format(str(stock))
		headers = {
			'user-agent': ua.random,
			'referer': 'https://m.stock.naver.com/item/main.nhn'
			}
		r = req.get(url, headers=headers).json()['result']

		def appender(item):
			list = []
			for i in r:
				try:
					list.append(i[item])
				except:
					list.append(None)
			return list
		
		bizdate = appender('bizdate')
		frgn_pure_buy_quant = appender('frgn_pure_buy_quant')
		indi_pure_buy_quant = appender('indi_pure_buy_quant')
		organ_pure_buy_quant = appender('organ_pure_buy_quant')
		frgn_hold_ratio = appender('frgn_hold_ratio')
		close_val = appender('close_val')
		change_val = appender('change_val')
		acc_quant = appender('acc_quant')
		risefall = appender('risefall')
		sosok = appender('sosok')
		
		dict = {
			'매매동향': {
				'날짜': bizdate, #날짜
				'외국인매매': frgn_pure_buy_quant, #외국인
				'개인매매': indi_pure_buy_quant, #개인
				'기관매매': organ_pure_buy_quant, #기관
				'외국인보유율': frgn_hold_ratio, #외국인 보유율
				'종가': close_val, #종가
				'전일비': change_val, #전일비
				'거래량': acc_quant, #거래량
				'전일비등락': risefall, #전일비의 등락. 5는 하락, 2는 상승, 3은 보합
				'소속': sosok, #시장. 1는 코스피, 2는 코스닥
			},
		}
	pp('크롤완료: 네이버 매매동향')
	return dict

def hankyungIndustry():
	with req.Session() as s:
		date = today()
		ua = UserAgent()
		url = 'http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=industry&search_date=1w&search_text=&now_page=1&type=more'
		headers = {
			'user-agent': ua.safari,
			'referer': 'http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=industry&search_date=1w&search_text=',
			'host': "consensus.hankyung.com",
			}
		r = req.get(url, headers=headers)
		r.encoding = "EUC-KR"
		soup = bs4(r.text, "html.parser").select('.table_style01 tbody tr')

		list = []
		dict = {
			'산업리포트': {
				date: []
			}
		}

		for val in soup:
			report_date = val.select('.txt_number')[0].text
			report_title = val.select('.text_l a')[0].text
			report_url = "http://consensus.hankyung.com{}".format(val.select('td:last-child a[href]')[0]['href'])
			print(report_date)
			print(report_title)
			print(report_url)
			print(date)
			print('-----------')

			if report_date == date:
				appendItem = {}
				appendItem['제목'] = report_title
				appendItem['링크'] = report_url


				dict['산업리포트'][date].append(appendItem)


	pp('크롤완료: 한경컨센서스-산업')
	return dict

# 내재가치 계산
def price_kimsUniversal(EPS, EPS_E, ROE, ROE_E, ROE_avg):
	try:
		if ROE_E != None and EPS_E != None:
			value_100 = round(EPS_E * ROE_E)
			value_90 = round(EPS_E * ROE_E * 0.9)
			value_80 = round(EPS_E * ROE_E * 0.8)
		elif ROE_avg != None and EPS_E != None:
			value_100 = round(EPS_E * ROE_avg)
			value_90 = round(EPS_E * ROE_avg * 0.9)
			value_80 = round(EPS_E * ROE_avg * 0.8)
		else:
			pp(ROE)
			value_100 = round(EPS * ROE)
			value_90 = round(EPS * ROE * 0.9)
			value_80 = round(EPS * ROE * 0.8)
	except:
		value_100 = None
		value_90 = None
		value_80 = None
	return value_100, value_90, value_80

def price_RIM(ROE, ROE_E, ROE_avg, 자본, 자본_E, 자본_avg, 주식수):
	요구수익률 = 0.0821

	def rim(roe, equity, 지속계수):
		Y10 = {
			'초과이익률': [roe-요구수익률, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			'ROE': [roe, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			'순이익': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			'자본': [equity, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			'초과이익': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
		}

		for i in range(1, 11):
			Y10['초과이익률'][i] = Y10['초과이익률'][i-1] * 지속계수
			Y10['ROE'][i] = 요구수익률 + Y10['초과이익률'][i]
			Y10['순이익'][i] = Y10['자본'][i-1] * Y10['ROE'][i]
			Y10['자본'][i] = Y10['자본'][i-1] + Y10['순이익'][i]
			Y10['초과이익'][i] = Y10['순이익'][i] - (Y10['자본'][i-1] * 요구수익률)

		순현재가치 = npf.npv(요구수익률, Y10['초과이익'])
		RIM주주가치 = 자본 + 순현재가치
		RIM주당가치 = round(RIM주주가치*100000000/주식수)
		return RIM주당가치	

	try:
		if ROE_E != None and 자본_E != None:
			ROE_E = ROE_E/100
			value_100 = rim(ROE_E, 자본_E, 1)
			value_90 = rim(ROE_E, 자본_E, 0.9)
			value_80 = rim(ROE_E, 자본_E, 0.8)
		elif ROE_avg != None and 자본_avg != None:
			ROE_avg = ROE_avg/100
			value_100 = rim(ROE_avg, 자본_avg, 1)
			value_90 = rim(ROE_avg, 자본_avg, 0.9)
			value_80 = rim(ROE_avg, 자본_avg, 0.8)
		else:
			ROE = ROE/100
			value_100 = rim(ROE, 자본, 1)
			value_90 = rim(ROE, 자본, 0.9)
			value_80 = rim(ROE, 자본, 0.8)
	except:
		value_100 = None
		value_90 = None
		value_80 = None
	
	return value_100, value_90, value_80

def PEG(EPS4y, EPS3y, EPS2y, EPS1y, EPS1E, PER, PER_E, dividend):
	'''
		r1: eps 4년-3년 성장률
		r2: eps 3년-2년 성장률
		r3: eps 2년-1년 성장률
		r1E: eps 1년-1E년 성장률
		per: 최근 per
		dividend: 최근 배당
	'''

	r1 = yieldRate(EPS3y, EPS4y)
	r2 = yieldRate(EPS2y, EPS3y)
	r3 = yieldRate(EPS1y, EPS2y)
	if EPS1E == None:
		r1E = (r1 + (r2*2) + (r3*3)) / 6
	else:
		r1E = yieldRate(EPS1E, EPS1y)

	if PER_E == None:
		PER_E = PER

	장기성장률 = (r1 + (r2*2) + (r3*3) + (r1E*6)) / 12
	result = round((장기성장률 + dividend) / PER_E, 2)

	return result