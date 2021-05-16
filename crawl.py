from functions import *

def crawl(code):
    startTime = time.time()
    data = {}
    data.update(fnSnapshot(code))
    data.update(fnFinance(code))
    data.update(fnInvest(code))
    data.update(fnRatio(code))
    data.update(fnConsensus(code))
    data.update(nvMain(code))
    data.update(nvPrice(code))
    endTime = time.time()
    pp('크롤시간: {}초'.format(round(endTime - startTime, 2)))

    # calculated_value
    try:
        priceInstAvg_100 = toInt(data['증권사별적정주가'][0]['AVG_PRC'])
        priceInstAvg_90 = round(toInt(data['증권사별적정주가'][0]['AVG_PRC'])*0.9)
        priceInstAvg_80 = round(toInt(data['증권사별적정주가'][0]['AVG_PRC'])*0.8)
    except:
        priceInstAvg_100 = None
        priceInstAvg_90 = None
        priceInstAvg_80 = None
    try:    EPS = data['재무하이라이트']['EPS']['year'][4]
    except: EPS = None
    try:    EPS_E = data['재무하이라이트']['EPS']['year'][5]
    except: EPS_E = None
    try:    PER = data['재무하이라이트']['PER']['year'][4]
    except: PER = None
    try:    PER_E = data['재무하이라이트']['PER']['year'][5]
    except: PER_E = None
    try:
        ROE_E = data['재무하이라이트']['ROEa']['year'][5]
        if ROE_E < 0: ROE_E = None
    except: ROE_E = None
    try:
        ROE = data['재무하이라이트']['ROE']['year'][4]
        if ROE < 0: ROE = None
    except: ROE = None
    try:    equity = data['재무하이라이트']['자본']['year'][4]
    except: equity = None
    try:    equity_E = data['재무하이라이트']['자본']['year'][5]
    except: equity_E = None
    try:
        profit_1Q = data['재무하이라이트']['순이익']['quarter'][5]
        profit_2Q = data['재무하이라이트']['순이익']['quarter'][4]
        profit_3Q = data['재무하이라이트']['순이익']['quarter'][3]
        profit_4Q = data['재무하이라이트']['순이익']['quarter'][2]
        equity_1Q = data['재무하이라이트']['자본']['quarter'][4]
        profit_avg = profit_1Q + profit_2Q + profit_3Q + profit_4Q
    except:
        profit_avg = None
    try:    equity_avg = equity_1Q
    except: equity_avg = None
    try:    ROE_avg = profit_avg / equity_avg * 100
    except: ROE_avg = None
    try:
        revenue_1Q = data['재무하이라이트']['매출']['quarter'][5]
        revenue_2Q = data['재무하이라이트']['매출']['quarter'][4]
        revenue_3Q = data['재무하이라이트']['매출']['quarter'][3]
        revenue_4Q = data['재무하이라이트']['매출']['quarter'][2]
        revenue_avg = revenue_1Q + revenue_2Q + revenue_3Q + revenue_4Q
    except:
        revenue_avg = None
    shares = data['기업정보']['발행주식수'] - data['기업정보']['자기주식수']
    price_kimsUniversal_100, price_kimsUniversal_90, price_kimsUniversal_80 = price_kimsUniversal(EPS, EPS_E, ROE, ROE_E, ROE_avg)
    price_RIM_100, price_RIM_90, price_RIM_80 = price_RIM(ROE, ROE_E, ROE_avg, equity, equity_E, equity_avg, shares)

    try:
        EPS4y = data['재무하이라이트']['EPS']['year'][1]
        EPS3y = data['재무하이라이트']['EPS']['year'][2]
        EPS2y = data['재무하이라이트']['EPS']['year'][3]
        EPS1y = data['재무하이라이트']['EPS']['year'][4]
        EPS1E = data['재무하이라이트']['EPS']['year'][5]
        dividend = data['배당']['배당수익률'][2]
        PEG_rate = PEG(EPS4y, EPS3y, EPS2y, EPS1y, EPS1E, PER, PER_E, dividend)
    except:
        PEG_rate = None

    calculated_value = {
        '내재가치': {
            '전일종가': data['매매동향']['종가'][0],
            'RIM': {
                '100%': price_RIM_100,
                '90%': price_RIM_90,
                '80%': price_RIM_80,
            },
            '만능공식': {
                '100%': price_kimsUniversal_100,
                '90%': price_kimsUniversal_90,
                '80%': price_kimsUniversal_80,
            },
            '기관평균': {
                '100%': priceInstAvg_100,
                '90%': priceInstAvg_90,
                '80%': priceInstAvg_80,
            },
            'PEG': PEG_rate,
        }
    }
    data.update(calculated_value)



    # rowData
    rowData = {}

    rowData['종목코드'] = code
    try:    rowData['종목명'] = data['기업정보']['기업명']
    except: rowData['종목명'] = None
    try:    rowData['종가'] = data['내재가치']['전일종가']
    except: rowData['종가'] = None
    try:
        if data['내재가치']['전일종가'] > data['내재가치']['RIM']['100%']:
            rowData['RIM비교'] = "고가"
        elif data['내재가치']['전일종가'] > data['내재가치']['RIM']['90%']:
            rowData['RIM비교'] = "적정가"
        elif data['내재가치']['전일종가'] > data['내재가치']['RIM']['80%']:
            rowData['RIM비교'] = "적정저가"
        elif data['내재가치']['전일종가'] <= data['내재가치']['RIM']['80%']:
            rowData['RIM비교'] = "저가"
    except: rowData['RIM비교'] = None
    try:
        if data['내재가치']['전일종가'] > data['내재가치']['만능공식']['100%']:
            rowData['만능비교'] = "고가"
        elif data['내재가치']['전일종가'] > data['내재가치']['만능공식']['90%']:
            rowData['만능비교'] = "적정가"
        elif data['내재가치']['전일종가'] > data['내재가치']['만능공식']['80%']:
            rowData['만능비교'] = "적정저가"
        elif data['내재가치']['전일종가'] <= data['내재가치']['만능공식']['80%']:
            rowData['만능비교'] = "저가"
    except: rowData['만능비교'] = None
    rowData['RIM80'] = data['내재가치']['RIM']['80%']
    rowData['RIM90'] = data['내재가치']['RIM']['90%']
    rowData['RIM100'] = data['내재가치']['RIM']['100%']
    rowData['만능80'] = data['내재가치']['만능공식']['80%']
    rowData['만능90'] = data['내재가치']['만능공식']['90%']
    rowData['만능100'] = data['내재가치']['만능공식']['100%']
    try:    rowData['PEG'] = data['내재가치']['PEG']
    except: rowData['PEG'] = None
    try:    rowData['기관평균'] = data['내재가치']['기관평균']['100%']
    except: rowData['기관평균'] = None
    try:    rowData['배당성향_당기'] = data['배당']['배당성향'][3]
    except: rowData['배당성향_당기'] = None
    try:    rowData['배당성향_1Y'] = data['배당']['배당성향'][2]
    except: rowData['배당성향_1Y'] = None
    try:    rowData['배당성향_2Y'] = data['배당']['배당성향'][1]
    except: rowData['배당성향_2Y'] = None
    try:    rowData['배당성향_3Y'] = data['배당']['배당성향'][0]
    except: rowData['배당성향_3Y'] = None
    try:    rowData['배당수익률_당기'] = data['배당']['배당수익률'][3]
    except: rowData['배당수익률_당기'] = None
    try:    rowData['배당수익률_1Y'] = data['배당']['배당수익률'][2]
    except: rowData['배당수익률_1Y'] = None
    try:    rowData['배당수익률_2Y'] = data['배당']['배당수익률'][1]
    except: rowData['배당수익률_2Y'] = None
    try:    rowData['배당수익률_3Y'] = data['배당']['배당수익률'][0]
    except: rowData['배당수익률_3Y'] = None
    try:    rowData['매출액증가율_1Y'] = data['재무비율']['매출액증가율'][-1]
    except: rowData['매출액증가율_1Y'] = None
    try:    rowData['매출액증가율_2Y'] = data['재무비율']['매출액증가율'][-2]
    except: rowData['매출액증가율_2Y'] = None
    try:    rowData['매출액증가율_3Y'] = data['재무비율']['매출액증가율'][-3]
    except: rowData['매출액증가율_3Y'] = None
    try:    rowData['매출액증가율_4Y'] = data['재무비율']['매출액증가율'][-4]
    except: rowData['매출액증가율_4Y'] = None
    try:    rowData['매출액증가율_5Y'] = data['재무비율']['매출액증가율'][-5]
    except: rowData['매출액증가율_5Y'] = None
    try:    rowData['영업이익증가율_1Y'] = data['재무비율']['영업이익증가율'][-1]
    except: rowData['영업이익증가율_1Y'] = None
    try:    rowData['영업이익증가율_2Y'] = data['재무비율']['영업이익증가율'][-2]
    except: rowData['영업이익증가율_2Y'] = None
    try:    rowData['영업이익증가율_3Y'] = data['재무비율']['영업이익증가율'][-3]
    except: rowData['영업이익증가율_3Y'] = None
    try:    rowData['영업이익증가율_4Y'] = data['재무비율']['영업이익증가율'][-4]
    except: rowData['영업이익증가율_4Y'] = None
    try:    rowData['영업이익증가율_5Y'] = data['재무비율']['영업이익증가율'][-5]
    except: rowData['영업이익증가율_5Y'] = None
    try:    rowData['ROE_당기'] = data['재무하이라이트']['ROE']['year'][5]
    except: rowData['ROE_당기'] = None
    try:    rowData['ROE_4Q'] = ROE_avg
    except: rowData['ROE_4Q'] = None
    try:    rowData['ROE_1Y'] = data['재무하이라이트']['ROE']['year'][4]
    except: rowData['ROE_1Y'] = None
    try:    rowData['ROE_2Y'] = data['재무하이라이트']['ROE']['year'][3]
    except: rowData['ROE_2Y'] = None
    try:    rowData['ROE_3Y'] = data['재무하이라이트']['ROE']['year'][2]
    except: rowData['ROE_3Y'] = None
    try:    rowData['ROE_4Y'] = data['재무하이라이트']['ROE']['year'][1]
    except: rowData['ROE_4Y'] = None
    try:    rowData['ROE_5Y'] = data['재무하이라이트']['ROE']['year'][0]
    except: rowData['ROE_5Y'] = None
    try:    rowData['ROA_당기'] = data['재무하이라이트']['ROA']['year'][5]
    except: rowData['ROA_당기'] = None
    try:    rowData['ROA_1Y'] = data['재무하이라이트']['ROA']['year'][4]
    except: rowData['ROA_1Y'] = None
    try:    rowData['ROA_2Y'] = data['재무하이라이트']['ROA']['year'][3]
    except: rowData['ROA_2Y'] = None
    try:    rowData['ROA_3Y'] = data['재무하이라이트']['ROA']['year'][2]
    except: rowData['ROA_3Y'] = None
    try:    rowData['ROA_4Y'] = data['재무하이라이트']['ROA']['year'][1]
    except: rowData['ROA_4Y'] = None
    try:    rowData['ROA_5Y'] = data['재무하이라이트']['ROA']['year'][0]
    except: rowData['ROA_5Y'] = None
    try:    rowData['매출_당기'] = data['재무하이라이트']['매출']['year'][5]
    except: rowData['매출_당기'] = None
    try:    rowData['매출_4Q'] = revenue_avg
    except: rowData['매출_4Q'] = None
    try:    rowData['매출_1Y'] = data['재무하이라이트']['매출']['year'][4]
    except: rowData['매출_1Y'] = None
    try:    rowData['매출_2Y'] = data['재무하이라이트']['매출']['year'][3]
    except: rowData['매출_2Y'] = None
    try:    rowData['매출_3Y'] = data['재무하이라이트']['매출']['year'][2]
    except: rowData['매출_3Y'] = None
    try:    rowData['매출_4Y'] = data['재무하이라이트']['매출']['year'][1]
    except: rowData['매출_4Y'] = None
    try:    rowData['매출_5Y'] = data['재무하이라이트']['매출']['year'][0]
    except: rowData['매출_5Y'] = None
    try:    rowData['순이익_당기'] = data['재무하이라이트']['순이익']['year'][5]
    except: rowData['순이익_당기'] = None
    try:    rowData['순이익_4Q'] = profit_avg
    except: rowData['순이익_4Q'] = None
    try:    rowData['순이익_1Y'] = data['재무하이라이트']['순이익']['year'][4]
    except: rowData['순이익_1Y'] = None
    try:    rowData['순이익_2Y'] = data['재무하이라이트']['순이익']['year'][3]
    except: rowData['순이익_2Y'] = None
    try:    rowData['순이익_3Y'] = data['재무하이라이트']['순이익']['year'][2]
    except: rowData['순이익_3Y'] = None
    try:    rowData['순이익_4Y'] = data['재무하이라이트']['순이익']['year'][1]
    except: rowData['순이익_4Y'] = None
    try:    rowData['순이익_5Y'] = data['재무하이라이트']['순이익']['year'][0]
    except: rowData['순이익_5Y'] = None
    try:    rowData['순차입금비율_1Y'] = data['재무비율']['순차입금비율'][-1]
    except: rowData['순차입금비율_1Y'] = None
    try:    rowData['순차입금비율_2Y'] = data['재무비율']['순차입금비율'][-2]
    except: rowData['순차입금비율_2Y'] = None
    try:    rowData['순차입금비율_3Y'] = data['재무비율']['순차입금비율'][-3]
    except: rowData['순차입금비율_3Y'] = None
    try:    rowData['이자보상배율_1Y'] = data['재무비율']['이자보상배율'][-1]
    except: rowData['이자보상배율_1Y'] = None
    try:    rowData['이자보상배율_2Y'] = data['재무비율']['이자보상배율'][-2]
    except: rowData['이자보상배율_2Y'] = None
    try:    rowData['이자보상배율_3Y'] = data['재무비율']['이자보상배율'][-3]
    except: rowData['이자보상배율_3Y'] = None
    try:    rowData['잉여현금흐름_1Y'] = data['잉여현금흐름']['FCFF'][-1]
    except: rowData['잉여현금흐름_1Y'] = None
    try:    rowData['잉여현금흐름_2Y'] = data['잉여현금흐름']['FCFF'][-2]
    except: rowData['잉여현금흐름_2Y'] = None
    try:    rowData['잉여현금흐름_3Y'] = data['잉여현금흐름']['FCFF'][-3]
    except: rowData['잉여현금흐름_3Y'] = None
    try:    rowData['총현금흐름_1Y'] = data['잉여현금흐름']['총현금흐름'][-1]
    except: rowData['총현금흐름_1Y'] = None
    try:    rowData['총현금흐름_2Y'] = data['잉여현금흐름']['총현금흐름'][-2]
    except: rowData['총현금흐름_2Y'] = None
    try:    rowData['총현금흐름_3Y'] = data['잉여현금흐름']['총현금흐름'][-3]
    except: rowData['총현금흐름_3Y'] = None
    try:    rowData['총투자_1Y'] = data['잉여현금흐름']['총투자'][-1]
    except: rowData['총투자_1Y'] = None
    try:    rowData['총투자_2Y'] = data['잉여현금흐름']['총투자'][-2]
    except: rowData['총투자_2Y'] = None
    try:    rowData['총투자_3Y'] = data['잉여현금흐름']['총투자'][-3]
    except: rowData['총투자_3Y'] = None
    try:    rowData['영업현금_1Y'] = data['현금흐름']['영업활동으로인한현금흐름'][-1]
    except: rowData['영업현금_1Y'] = None
    try:    rowData['영업현금_2Y'] = data['현금흐름']['영업활동으로인한현금흐름'][-2]
    except: rowData['영업현금_2Y'] = None
    try:    rowData['영업현금_3Y'] = data['현금흐름']['영업활동으로인한현금흐름'][-3]
    except: rowData['영업현금_3Y'] = None
    try:    rowData['투자현금_1Y'] = data['현금흐름']['투자활동으로인한현금흐름'][-1]
    except: rowData['투자현금_1Y'] = None
    try:    rowData['투자현금_2Y'] = data['현금흐름']['투자활동으로인한현금흐름'][-2]
    except: rowData['투자현금_2Y'] = None
    try:    rowData['투자현금_3Y'] = data['현금흐름']['투자활동으로인한현금흐름'][-3]
    except: rowData['투자현금_3Y'] = None
    try:    rowData['재무현금_1Y'] = data['현금흐름']['재무활동으로인한현금흐름'][-1]
    except: rowData['재무현금_1Y'] = None
    try:    rowData['재무현금_2Y'] = data['현금흐름']['재무활동으로인한현금흐름'][-2]
    except: rowData['재무현금_2Y'] = None
    try:    rowData['재무현금_3Y'] = data['현금흐름']['재무활동으로인한현금흐름'][-3]
    except: rowData['재무현금_3Y'] = None
    try:    rowData['기말현금및현금성자산_1Y'] = data['현금흐름']['기말현금및현금성자산'][-1]
    except: rowData['기말현금및현금성자산_1Y'] = None
    try:    rowData['기말현금및현금성자산_2Y'] = data['현금흐름']['기말현금및현금성자산'][-2]
    except: rowData['기말현금및현금성자산_2Y'] = None
    try:    rowData['기말현금및현금성자산_3Y'] = data['현금흐름']['기말현금및현금성자산'][-3]
    except: rowData['기말현금및현금성자산_3Y'] = None
    try:    rowData['현금및현금성자산의증가_1Y'] = data['현금흐름']['현금및현금성자산의증가'][-1]
    except: rowData['현금및현금성자산의증가_1Y'] = None
    try:    rowData['현금및현금성자산의증가_2Y'] = data['현금흐름']['현금및현금성자산의증가'][-2]
    except: rowData['현금및현금성자산의증가_2Y'] = None
    try:    rowData['현금및현금성자산의증가_3Y'] = data['현금흐름']['현금및현금성자산의증가'][-3]
    except: rowData['현금및현금성자산의증가_3Y'] = None
    try:    rowData['거래량_10D평균'] = sum(data['매매동향']['거래량']) / len(data['매매동향']['거래량'])
    except: rowData['거래량_10D평균'] = None
    try:    rowData['주가증감_1D'] = yieldRate(data['매매동향']['종가'][0], data['매매동향']['종가'][1])
    except: rowData['주가증감_1D'] = None
    try:    rowData['주가증감_5D'] = yieldRate(data['매매동향']['종가'][0], data['매매동향']['종가'][5])
    except: rowData['주가증감_5D'] = None
    try:    rowData['주가증감_10D'] = yieldRate(data['매매동향']['종가'][0], data['매매동향']['종가'][10])
    except: rowData['주가증감_10D'] = None
    try:    rowData['주가증감_30D'] = yieldRate(data['매매동향']['종가'][0], data['매매동향']['종가'][-1])
    except: rowData['주가증감_30D'] = None
    try:    rowData['개인매매_최근'] = data['매매동향']['개인매매'][0]
    except: rowData['개인매매_최근'] = None
    try:    rowData['개인매매_5D합'] = sum(data['매매동향']['개인매매'][0:5])
    except: rowData['개인매매_5D합'] = None
    try:    rowData['개인매매_10D합'] = sum(data['매매동향']['개인매매'][0:10])
    except: rowData['개인매매_10D합'] = None
    try:    rowData['개인매매_30D합'] = sum(data['매매동향']['개인매매'][0:-1])
    except: rowData['개인매매_30D합'] = None
    try:    rowData['기관매매_최근'] = data['매매동향']['기관매매'][0]
    except: rowData['기관매매_최근'] = None
    try:    rowData['기관매매_5D합'] = sum(data['매매동향']['기관매매'][0:5])
    except: rowData['기관매매_5D합'] = None
    try:    rowData['기관매매_10D합'] = sum(data['매매동향']['기관매매'][0:10])
    except: rowData['기관매매_10D합'] = None
    try:    rowData['기관매매_30D합'] = sum(data['매매동향']['기관매매'][0:-1])
    except: rowData['기관매매_30D합'] = None
    try:    rowData['외국인매_최근'] = data['매매동향']['외국인매매'][0]
    except: rowData['외국인매_최근'] = None
    try:    rowData['외국인매매_5D합'] = sum(data['매매동향']['외국인매매'][0:5])
    except: rowData['외국인매매_5D합'] = None
    try:    rowData['외국인매매_10D합'] = sum(data['매매동향']['외국인매매'][0:10])
    except: rowData['외국인매매_10D합'] = None
    try:    rowData['외국인매매_30D합'] = sum(data['매매동향']['외국인매매'][0:-1])
    except: rowData['외국인매매_30D합'] = None
    try:    rowData['외국인보유율_최근'] = round(data['매매동향']['외국인보유율'][0], 2)
    except: rowData['외국인보유율_최근'] = None
    try:    rowData['외국인보유율증감_5D'] = round(data['매매동향']['외국인보유율'][0] - data['매매동향']['외국인보유율'][4], 2)
    except: rowData['외국인보유율증감_5D'] = None
    try:    rowData['외국인보유율증감_10D'] = round(data['매매동향']['외국인보유율'][0] - data['매매동향']['외국인보유율'][9], 2)
    except: rowData['외국인보유율증감_10D'] = None
    try:    rowData['외국인보유율증감_30D'] = round(data['매매동향']['외국인보유율'][0] - data['매매동향']['외국인보유율'][-1], 2)
    except: rowData['외국인보유율증감_30D'] = None
    try:    rowData['소속'] = data['기업정보']['소속']
    except: rowData['소속'] = None
    try:    rowData['업종'] = data['기업정보']['업종']
    except: rowData['업종'] = None
    try:    rowData['핵심요약'] = data['기업정보']['핵심요약']
    except: rowData['핵심요약'] = None
    try:    rowData['설명1'] = data['기업정보']['설명1']
    except: rowData['설명1'] = None
    try:    rowData['설명2'] = data['기업정보']['설명2']
    except: rowData['설명2'] = None

    return data, rowData
