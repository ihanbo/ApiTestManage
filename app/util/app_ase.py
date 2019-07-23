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
    return str.encode(value)  # 返回bytes

#加密方法
def app_encrypt(target):
    bs = AES.block_size
    pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    unpad = lambda s: s[0:-ord(s[-1])]
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    #先进行aes加密
    encrypt_aes = aes.encrypt(bytes(pad(target),encoding='utf-8'))
    #encrypt_aes = aes.encrypt(pad(bytes(target, encoding='utf-8')))
    #用base64转成字符串形式
    encrypted_target = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    encrypted_target = encrypted_target.replace('+', '-').replace('/', '_')
    print(encrypted_target)
    return encrypted_target

#解密方法
def app_decrypt(target):
    bs = AES.block_size
    unpad = lambda s: s[0:-ord(s[-1])]
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 密文
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    #优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(target.encode(encoding='utf-8'))
    #执行解密密并转码返回str
    #decrypted_target = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','')
    
    decrypted_target = unpad(aes.decrypt(base64_decrypted).decode('utf-8'))
    decrypted_target = decrypted_target.replace('\0', '').replace('+', '-').replace('/', '_')
    print(decrypted_target)

    return decrypted_target

if __name__ == '__main__':
    app_encrypt('jacktony')
    #app_decrypt('lVq_rdD_lmIcvY2ezvtHBA==')