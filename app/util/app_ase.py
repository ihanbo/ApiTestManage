import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

'''
采用AES对称加密算法
'''

# str不是16的倍数那就补足为16的倍数s
def add_to_16(value):
    value = value[::-1][len(value) - 10:]
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes

#加密方法
def encrypt_req(req):
    #req = {'method': 'POST', 'files': {}, 'data': {'mobile': 'aaaa'}, 'headers': {'google': 'baidu'}, 'url': 'http://mapi.yiche.com/app_carmodel/api/v1/inquiry/add', 'params': {}, 'verify': True}
    if req.get('headers').get('name'):
        encry_str = app_encrypt(req['headers']['name'])
        req['headers']['name'] = encry_str

    if req.get('headers').get('mobile'):
        encry_str = app_encrypt(req['headers']['mobile'])
        req['headers']['mobile'] = encry_str

    if req['method'] == 'POST':
        if  req.get('json') and req.get('json').get('param').get('name'):
            encry_str = app_encrypt(req['json']['param']['name'])
            req['json']['param']['name'] = encry_str

        if  req.get('json') and req.get('json').get('param').get('mobile'):
            encry_str = app_encrypt(req['json']['param']['mobile'])
            req['json']['param']['mobile'] = encry_str

        if req.get('data') and req.get('data').get('name'):
            encry_str = app_encrypt(req['data']['name'])
            req['data']['name'] = encry_str

        if req.get('data') and req.get('data').get('mobile'):
            encry_str = app_encrypt(req['data']['mobile'])
            req['data']['mobile'] = encry_str
    else:
        encry_str = app_encrypt(req['params']['name'])
        req['params']['name'] = encry_str
        encry_str = app_encrypt(req['json']['param']['mobile'])
        req['params']['mobile'] = encry_str

def encrypt_resp(resp):
    if  resp['status'] == 1:
        encry_str = app_encrypt(resp['data']['priceList'])
        resp['data']['priceList'] = encry_str

def decrypt_resp(resp):
    content = resp.resp_obj.content
    my_json = content.decode('utf8').replace("'", '"')
    data = json.loads(my_json)
    str = data['data']['priceList']
    es_str = app_decrypt(str, 'caf86ffe6814454096572dcdffacd2b4')
    new_data = json.loads(es_str)
    data['data']['priceList'] = new_data
    newbytes = bytes(json.dumps(data), 'utf-8')
    resp.resp_obj._content = newbytes

def app_encrypt(target):
    bs = AES.block_size
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    pad_data = pad(bytes(target, encoding='utf-8'), bs)
    #先进行aes加密
    encrypt_aes = aes.encrypt(pad_data)
    #用base64转成字符串形式
    base64_encrypt_aes = base64.encodebytes(encrypt_aes)
    str_base64_encrypt_aes = str(base64_encrypt_aes, encoding='utf-8')
    #encrypted_target = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    encrypted_target = str_base64_encrypt_aes.replace('+', '-').replace('/', '_').replace('\n', '')
    #print(encrypted_target)
    return encrypted_target

#解密方法
def app_decrypt(target, key):
    bs = AES.block_size
    # 秘钥
    #发票类key
    # key = 'caf86ffe6814454096572dcdffacd2b4'
    # #其他key
    # key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 密文
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    #优先逆向解密base64成bytes
    target = target.replace('-','+').replace('_','/').replace('', '\n')
    base64_decrypted = base64.b64decode(target.encode(encoding='utf-8'))
    #base64_decrypted = base64.decodebytes(target.encode(encoding='utf-8'))
    #执行解密密并转码返回str
    #decrypted_target = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','').replace('\n','')
    unpad_data = unpad(aes.decrypt(base64_decrypted),bs)
    decrypted_target = str(unpad_data, encoding ='utf-8').replace('\0', '').replace('\n', '')
    print(decrypted_target)
    return decrypted_target

if __name__ == '__main__':
    #app_encrypt('15801672960')
    #app_decrypt('N8CPDrrrTyKDwBkixqgTmg==')
    app_decrypt('H-lA7ctHHeKMvuwrjmDG7IFRgumBQ8vVRxRbbF08pJYPFcL9_aO3QxUcoj5O8FIpCQOhlqVp6HzmlgccQDIhAYcn0IFaOasrKr9k_1Nz8D0MsBt2UwaqPD3ncTSxTlY76f9cvHPtFyf-LvM0wovsfYEkycwfdFhP56s9mDuBDmMCGIlryjaVni_rl3R5tsYgd1lP9q3TfkGkm-GGGo0mifpZJoVOJQOwZI950vHERXgqeoQllGK5_0BM7_OCfh54GN4pXpXtkqpCkXbv7SaF2LmzXn8aTyYHnNPoZyKYWh8XtuJu6Tgel_XkWianQxv87mAEaKlLXo4RcMFl7ZOeWD2RPdpwiIN1nvgdiuc7fWy0aXKL_Td4rrE_z6fm5tggGPgET4Te59UhCsxuDR_VM664Unn6JICylLFun3tgvJtiyaJp-ofI9OEnksuZ59iXvyVaXX-5to462fktKChGOOiQNGNP4F9j-AlHy1zKq_V0q9ylRWCRlyLSpwLnKtCdjbJvTSJqba6jH_VPMVwb7qDIcuD5_0jh-falRVKEFouPItoSQj5zCcSrwbUMy9PWTHRQHdN0xyy2sCF4EmvDnIkCmeR_EDHLTa8V63Rg7tCZQ19iOtn6N-hPbCaido4dPFetjKc129ak8kg1IxalvXgEBhSaJbxI388RWqoQv72_8KgFji-9dxx6hKjkRbyFb0f63Pv2lSJN2RhWbRzi8Wgj887_kHuj1R92xbT7jYkOZkUTTtKgilDezue0kMMN2RBt6FsUrfG2BrwHo6_NJdU_r9xaoZruEH6nHj4G2jGzlSCva4iTnXqQMa5JNymtX4LW9RRX6CB9PNun0Lo5TaQx0zznDCdDE8JNBTP0A15O-taq4szTYD1nLto7wzalYsAqHvlNpwxX0CPX3-XXt11ojGvSgm2NUaX8AzX3mD_dVdlgiAVpw4x7aoJJSfaMTPFyH2fzc1Gap6Xn4t1k96PmsP8KAujHUVdCPrLaVMtYOqRh5PgYJAmIBjo79FyYwMDq70zCiQEPSmlJCKOMtvhcjZkfJAllP5of3OyNupjmWqB0GMkCMTbFtTgJrdpH7n2MTETOAAjZQUvCu7oIjaxLpztb9MswNS2EQPRxQjm8NEPVJGnxz9sk_Dds8FagLndHjtKvkVdJgycfKj6QS2bmDlaodTFB1YHZZS2oDeAyDXhciR4WcAJpUaDBucTZvLDS3p0PZhPthfyjxgPLeWpV7relbRioVPYDfWXCQsy_EpLjwfDZjBCP1TLgvmA5JvACxW_H4vj1QGqokYzDRE_-EdlSNJXsb6wSLtYntwrZfXcnSutG_eYE8AXakNfACFjouvH7-Ra9VBHY_3EIpAuhTPoyHNB1dZZC5uThgIq-geCuMGmKyTLSalLplsXlWKZ7ABiaL_7acr90-AllIJQd9dw-WueBd13rXxUCeYtdrE5d6i5-NP5D-LCPJKfNs2_8UtFB4dzxjhT1gjqXNMwcZGjUDgaZ9OfH0mBlufZv2AOfKGSnEWhCX-X9Htzta3nKI5BKqncjXCMbv00C41V8bzGxo3WJuSTosZ3-g-UrkUd-HlsHLQCwo77joaq8WspkixjN5lwzMXg6E4h-64z3XOXCncuJUAgVLInKo0IH_L0bYzGoQZvoVnwiZAORZCMBM9JaXuv-DuUUg-roD_Z2PQFWTSsIUHDGLXkr2fdCJcJh2tuugWRankDhf4kblkzoNGIR8ViLXErrof0ia5n0CYY_r6jYCkAge74oZVc2_GZQoRglv9Bus_bi7u3pgdHFz3DLmwfayaaJfShVj4pm1B1rIK_xpAqssEfn6Ubzf6kW63YLvH0mKcDtl6Wbrja0wfTVW6rK05DP8e5spSb8JFYWIE_UckpkzGfBC-rKM0mHrS1dRsvy_oI8oCqWg1EtXeCQjy8rI6h2qd7cEblrPM5VXRk8TZaQR4zO50UlKODl75x5PL6qWIucF2229YvoBIbl80j4DYN-fasx503zqbq0nFjFu6mvXV9Osahw_B7LBe--k34e4PhinRwfgOQlReY9vYEuqd0u7zf47CmUH6chd2l3atjHA2XIYcB3HQyF3BJRlGdUXzJxu88N7XdYU_LDdrGCI5Qxrs95HiZBiqBnq2CyjG43rGanVXssauxcrvsBj7bLE5tMELEq3piqsEzxmdN_u7kWdwjHJFvrzNYpTKbRFKhK7IkOImCSKbWe8mD138Yw4IvbZ6fMauP91ye5ujp8WNfVOfgSUvr5mcXFXyf9OQpzqU7AajkUczFH79Wh4888nR4EoXudULwbLgqO3JbMBlyvjiLX0p0wMB3X-ginzotNmfOOxTI4hHhjG8t65TP_df8SuV5Yg428xuGErzZnlhyQyAEC-DVBQ1wu-T1fWnDURWZrjHYVeWFcQSz2KAp4fnkNb5vDG8c46yWItxPJfJzw22wrnvKKO7O_47aGFwVzkqWN7k7IslZeKRSjvWa3_pLNDJyJZYYB0blAhaLJoklPLmgLf7lxM5vwmJwdsMAU6z5UofiZFerjmAL9ybQfo4w_dxWXVEo2OyTvMBNbTDJ74dlhy7_jLdw3Y_JtcT7Oklj4obfQpa6ALH3IwSgllWFoeIIc6f9cvHPtFyf-LvM0wovsfYEkycwfdFhP56s9mDuBDmMOp7Z9K3qvuYDQs1xdHVgPashDliNpyY8U5Q-OkETDrnlm9WptDqBhvmYbgNGS9z4qeoQllGK5_0BM7_OCfh54xTPYMliv1tDCCG4uyFQT4MUwZtUjY6F2O3tT9btCbZoXtuJu6Tgel_XkWianQxv8nWsw5lzhhyE6UHr6acA2JliEcjt5YC_zokkiZ_VqdRlw9UaEYkQ94-yyI6ByFB7ur9IANTFqYlqEnQP14efJS6asnxLpAMUpwCR1Y-1cpqe8dNxOH_4HYNF1gHk10qG6XZoNZ9AGbgrwp56Bdx3ZLBBdWPo_GFe2U5BO3cMOuZa-BIxEsbADe8Ilki2uzlKc0n-XAjrhUQq2bcYefA_pZf_kRO2I0vcf3XEOmdQJ3y7vbi5t0fw9zcmUCY8BDEMDUW-3MerftU5u_fDPC3tNgOxtSO9zKBXqSv3qk6qdq0IcVV_tFqItfoBjLo2MyrQusaaX61QdEmPlDESJjrzrMNgIMq5paviAV2_k8KbgqHSGEwBIjZAiacjNZeMpfnagHsIsbbyJkPj_ziY9dffqXp_jQ4c0B_zJDbACWKkazYN9UO-IaUXgwoyRBrgM8tV2WyFL8L-FEFPpQ2rq7J1nsxioz2tAvDisEjRNLmxyVKUSZkANoK8xFX-9wuc-akK_pPANXBdMBkIoPdvtTchldIJtRCUVqytkFSWnH3-fmUqgLq4FDeB_52ltw03qTLY5TZ_-juLlcnOFapd_B6LUgLVWpOmu_hXXjbh2POCi3Vjf2FIYqMZj-_kkszn9NQ5LdxvcEqHdfQd7mVT3FhT0Oht94IDkDO4ZM7fC4XcyKxKIQ8K8io1pYV91VWErNbsoZp7_2KCR1UvP-W1TJ7p8bDOZnI1_8swYCgxx94MGITKvOFd8m1LopvOVMXI6S3ecJqaryM1sCVFsf06Sb-0b7JJbzbEyEH3uQPYTMQoqywcXoOZoI3WCgbBhr1VjAbrWjj7hm4JegDvTVPWs7o2PHA2nP9ZpWV5_o33tfGish6T5JdtimeH1dyqPttLs7x2Wf3sUmV5-SsVNgQP9_PINxBfKDXBDki0AqfO7dCJ5NpysMHPfp0Ea6lBiGgIlYCagUddFhOi-aeXLxMZhjdjfHHQkSmW5n4_D8z8_wYuORGk_FG8Ppjtc1wwyauVmzWhdsFLneIqnLgqAzmxg6smzYz2nl7FgATKJDq6MNqqzIzSW75dMLPpK1SZI8X6HV95F5crmHMLQOPW6KTUhER2neFB1eqhjwvaxYuu1L5KQnSZnC5vWrT0C2dDOcdtTIvz_6phgx2ujrfiBKAHbg22gNxtCI6SKrKfwFUBSCNZ3j38s3pTWxxnEQNhDgedDuXytoObRKB3WWH85KWmIAvAGhzWW9diU-EFuUZKWnKke18bh5BGfFiu4hC-IqszUs8tadD0nQKZPShTbv29Nc_Sbkryw0t6dD2YT7YX8o8YDy3lqVe63pW0YqFT2A31lwkLMvxKS48Hw2YwQj9Uy4L5gOSbwAsVvx-L49UBqqJGMw0RP_hHZUjSV7G-sEi7WJ7cKSLwkYjgYSX_-bl1fIooO6dQt0N6C5_8RIDg0rQ1bBqQP2zdpHXrBIl_pTuK0ago-Rve_P8vCo5a4ndkJTK0uPHPRLqhEEsGoJFUasaKC5ABsYBAKl9PdV9H5NNdaXO4F-WOsRSQQKbM5mZP2ErPJ2skEKPosZQon6Qh8Tmg2XOdb9qTEgrYn2kCOuDcR2J1JJZAO0ShwxuHi4kpP-RII94NLBXwvJYW0T_-zPv2hYrvLTfPf7L8bCXK38H9g2yyv_dpRLTNuSb4yQeSS5mBi6u830Haods8TLsmViaWiws-uwC6syu_A7oykqU_5wKYOCodtI82SQyqJGPf7JRM6ORZKV6PhHHp8n0L7v7-gBc8mOlzTnx4IbodJ2tzN_E9q8S_pUJzdhrGmkwgRZSYib3mu1e8JSVS4wFbJUYoGgI6HLRQjjBf5_uG6_sX3AMxRsFLneIqnLgqAzmxg6smzYz2nl7FgATKJDq6MNqqzIzSW75dMLPpK1SZI8X6HV95FV5NKXgCMmgouekYJplxizqmLhlSCf19gsMjTnGb5bqMR8Qhbw5A1sSlvyZ_crKtz6phgx2ujrfiBKAHbg22gNxtCI6SKrKfwFUBSCNZ3j3-NQkN3KI5hxOGAyWux28OUoObRKB3WWH85KWmIAvAGhw866MFuDLBBQsBLqqhELYjC8fhDd0daC69PmoFj_l97jPdc5cKdy4lQCBUsicqjQgf8vRtjMahBm-hWfCJkA5FkIwEz0lpe6_4O5RSD6ugPH-Yet14bXaaYLGA1yaEfmUIlwmHa266BZFqeQOF_iRuWTOg0YhHxWItcSuuh_SJrGDenQKMNj4gMcFAcxtUoaiUKJWtPoubDYN1fdZK_43Hx5bo73FWRawftkV6BPusnJt8WG9RPs9gY_qbdJY7PWIwtyEtwQMgFYMqwNx7MP3O7G6eLkyU1cGKQSRhtKYqbzTccj_2m1U93MyEgP6OD2Tz1n19dQugA7XqrqvhFGhmWFGdHzVG4zcxkmSOin3PjhilTqvnM_wI4iZDuEc44LOVm6B3uvEO7J5ameeFVT3E9j94ihH25PKXbbZ2IPVPHnN1_PS8wzVTULctS522lIINq4Z30gH2XSUwo7XOojZaEeEL2K71-cnvnJh6pwyXImp1a8mR0cupWZAMFsg19JWcFhnDIWMYuzVw0C4BVtvZuDaKPyw_s52KutgSS5ZWmQ1PLzs13_eDawzlEMiY-nnOQZLi4OjRQ8s661spXi7wZRJueVOFEuJ77Sa-9W3PP6mizz00_1YjwC47NSKGyy4B3TRAJ5iCRIilZuNJHI5Wpr8DPd3FmZmOIvGU27cSoGfvriIcHYHRFZz0KnI33uygi3wPOx65j77DtO0RGiy4JA8AkKfsa3Q-SIYVUN7GCqmN2b0pFtgtRaQ_hm3gk2Oy-iIrbU4lTXa0AqDwpHmbi3h6YRbNbEUsyNGXpeTSop7Rs8U9kaKd58c5Gr9fSUFnKmy979pJdionDiN4i8Ib1Vkj_nPq-80rj7x-ET8LaZyu27g3z4cnvoarfGJSf7mKHKCvHA_CvHdxAjn0yp_jYc9XK_tTkKPxDc7redtIhvFYg4HHG2dNieO_LVORZcQv9LLtE6JgwYZ-P0Ym8298_zKUaaqs9JbsNBJXC2ISJCzHylhc9lExSeSEw44YjPlvrzNYpTKbRFKhK7IkOImCSKbWe8mD138Yw4IvbZ6fMauP91ye5ujp8WNfVOfgSUsVXnuqQ1Iw_knHNYkS8hDKLjisfbHFbrVwukr2JaJSkULwbLgqO3JbMBlyvjiLX0iQ2AR8FxnIcppcikBlwsxY4hHhjG8t65TP_df8SuV5YYmtK1vHFXF66XeXCAe8KRiu3Wbi0tg-e7QbUruiozaaXvf3MRcJSCyRI1xJwr41TSZPsF8VZor_a8nIpJqefY8FAm6vI3EQOW-hAIVPnutL2DGUJCzaZnCV6Zso30S7eRk114ePvL0iS1xp16vn3fdG2lT_ZbNHwXfGxIdasFnbbtvxxm_Bsu7escPO-VZuE0tZ3qC3a80nCo-cWFC-LyRcg55n_-7mJL8BMx0NAGXNOWEBcv3mVfC-Jcwvr2sJv-cwgEucAk4Mf68Q1otsD7Ki8ycEWF8SShTUnL75N2igOLeC-738tL7fo0T6KP0PkhN4yEEEz39Rs4d5sBKC8E1DfGcPL_uTMPosLTo5IW8JKA3iYDqRMpAI2B9Xs6k4zBJRBeH18QKVDt7UtOd2roJOqZ4kRNR5Xq1KZG7JTHH_O079V6B0W6_wMAXqL9i5JHJqfHoW7pxjZUOTFA6A1IuBU0rakn7ZnETodyypl0MLVUbVBmdOIzFceLBbUxpmiEmZADaCvMRV_vcLnPmpCv0FEy3blOQ8x_dBw9zzaEmw7DeLuyAX7LehSf4LpssujoC6uBQ3gf-dpbcNN6ky2OU2f_o7i5XJzhWqXfwei1IB_BTx0JzbKb4SeYymanRUX3VXZYIgFacOMe2qCSUn2jEzxch9n83NRmqel5-LdZPcizpD08PY-7fOxseetiLIqGDoxB9EOsB8qzsfXr0cF469Nr72UipTqt5UIlK9zhX__UuMHGonewxnChFRD5qNf9OpUZHrz5RKV5WQWpv7Kgk5og3gXa2TMAJf3Voz67Zwz2O2q4SK_t_HpCGn1S50xfCfJL99FrKq8GKWXdPeGpG6aL6eilFPAG8VCrhJy22BlcaOq9Xmz4UxjzgWeR3whp4BVGvt4-4xUX_e8lJGHHwqHbSPNkkMqiRj3-yUTOjkWSlej4Rx6fJ9C-7-_oAXPJjpc058eCG6HSdrczfxPavEv6VCc3YaxppMIEWUmIm95rtXvCUlUuMBWyVGKBoCOhy0UI4wX-f7huv7F9wDMUbBS53iKpy4KgM5sYOrJs2M9p5exYAEyiQ6ujDaqsyM0lu-XTCz6StUmSPF-h1feRfP0LjqUuX55FkMIJeqK94Gs1YEmtzXTcQBdv76l-89REfEIW8OQNbEpb8mf3Kyrc-qYYMdro634gSgB24NtoDcbQiOkiqyn8BVAUgjWd49_jUJDdyiOYcThgMlrsdvDlKDm0Sgd1lh_OSlpiALwBocPOujBbgywQULAS6qoRC2IwvH4Q3dHWguvT5qBY_5fe4z3XOXCncuJUAgVLInKo0IH_L0bYzGoQZvoVnwiZAORZCMBM9JaXuv-DuUUg-roD0FErVMloi44s2EmE-jS7yVCJcJh2tuugWRankDhf4kblkzoNGIR8ViLXErrof0ia_y28H9SltcW8KuNJkAXcRI2_GZQoRglv9Bus_bi7u3pgdHFz3DLmwfayaaJfShVj4pm1B1rIK_xpAqssEfn6UbeuEXHRnneoYUD2iUSBLV7XTaHCA68JquR07onU1e5Ve1SOBncfq5mRO96xVFrt6UmVSvhyvegqVfV85WO5kKUg1EtXeCQjy8rI6h2qd7cEUsW7NwotrHsPIfGQRH6_6QlKODl75x5PL6qWIucF2222j1gNcML3nnkexlFXXHuKDcnfA0Q-hKP2zIVM4u2ueZ4SwfljBcQb_Z2-LtnGA26yLJWXikUo71mt_6SzQyciWWGAdG5QIWiyaJJTy5oC3-yqzEvdYT0kCm7wJnTgJowmRXq45gC_cm0H6OMP3cVl2pw3Ma2rDI-jCacCHKlyprqwEWEQllokqKaXL2dI0pGk_CEXMSZ2BjzCQsAvPv23-pos89NP9WI8AuOzUihssuAd00QCeYgkSIpWbjSRyOV1faJITtazF8ghxTOAGQz-wVDnzk0ngAGsDJ7r-fr5aTYRcajQxDq1HmFR5sQ5-srCQPAJCn7Gt0PkiGFVDexgn05O4SbrGAXasel_aUWRh_fWmku9tGNNJQkuPfXA2pL4t4emEWzWxFLMjRl6Xk0qKe0bPFPZGinefHORq_X0lBZypsve_aSXYqJw4jeIvCG9VZI_5z6vvNK4-8fhE_C2mcrtu4N8-HJ76Gq3xiUn-4R7hZc45LtvJmx86upIOhf')
