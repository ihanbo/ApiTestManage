from ..util.app_ase import *

def resp_decrypt(res):
    for index, case in enumerate(res['details']):
        if case['records']:
            for casedata in case['records']:
                if int(casedata['meta_datas']['data'][0]['response']['json']['status']) == 1:
                    for data in casedata['meta_datas']['data']:
                        if data.get('response').get('json').get('data').get('priceList'):
                            target = data['response']['json']['data']['priceList']
                            data['response']['json']['data']['priceList'] = app_decrypt(target, 'caf86ffe6814454096572dcdffacd2b4')
                        else:
                            pass
                else:
                    pass
        else:
            pass
