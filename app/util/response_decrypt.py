from ..util.app_ase import *

def resp_decrypt(res):
    print('11111111111111111111111111',res)
    for index, case in enumerate(res['details']):
        print('22222222222222222222222222222', case)
        if case['records']:
            for casedata in case['records']:
                if casedata['status'] != 'error' and int(casedata['meta_datas']['data'][0]['response']['json']['status']) == 1:
                    for data in casedata['meta_datas']['data']:
                        if 'get_car_price_list' in data['request']['url']:
                            target = data['response']['json']['data']['priceList']
                            data['response']['json']['data']['priceList'] = app_decrypt(target, 'caf86ffe6814454096572dcdffacd2b4')
                            commstr = data['response']['json']['data']['commendList']
                            if commstr:
                                data['response']['json']['data']['commendList'] = app_decrypt(target,  'caf86ffe6814454096572dcdffacd2b4')
                        elif 'get_invoice_price_list' in data['request']['url']:
                            target = data['response']['json']['data']['priceList']
                            data['response']['json']['data']['priceList'] = app_decrypt(target, 'caf86ffe6814454096572dcdffacd2b4')
                            commstr = data['response']['json']['data']['commendList']
                            if commstr:
                                data['response']['json']['data']['commendList'] = app_decrypt(target,  'caf86ffe6814454096572dcdffacd2b4')
                        else:
                            pass
                else:
                    pass
        else:
            pass
