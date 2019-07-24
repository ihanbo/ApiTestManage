import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
'''
采用AES对称加密算法
'''
# str不是32的倍数那就补足为16的倍数
def add_to_32(value):
    value = value[::-1][len(value) - 10:]
    while len(value) % 16 != 0:
        value += '\0'
    #print(value)
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

def app_encrypt(target):
    bs = AES.block_size
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    pad_data = pad(bytes(target, encoding='utf-8'), bs)
    #先进行aes加密
    encrypt_aes = aes.encrypt(pad_data)
    #用base64转成字符串形式
    base64_encrypt_aes = base64.encodebytes(encrypt_aes)
    str_base64_encrypt_aes = str(base64_encrypt_aes, encoding='utf-8')
    #encrypted_target = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    encrypted_target = str_base64_encrypt_aes.replace('+', '-').replace('/', '_').replace('\n', '')
    return encrypted_target

#解密方法
def app_decrypt(target):
    bs = AES.block_size
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 密文
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    #优先逆向解密base64成bytes
    target = target.replace('-','+').replace('_','/').replace('', '\n')
    base64_decrypted = base64.b64decode(target.encode(encoding='utf-8'))
    #base64_decrypted = base64.decodebytes(target.encode(encoding='utf-8'))
    #执行解密密并转码返回str
    #decrypted_target = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','').replace('\n','')
    unpad_data = unpad(aes.decrypt(base64_decrypted),bs)
    decrypted_target = str(unpad_data, encoding ='utf-8').replace('\0', '').replace('\n', '')
    return decrypted_target

if __name__ == '__main__':
    app_encrypt('中国')
    app_decrypt('N8CPDrrrTyKDwBkixqgTmg==')

