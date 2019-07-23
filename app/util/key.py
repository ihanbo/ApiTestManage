import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

'''
采用AES对称加密算法
'''


# str不是32的倍数那就补足为16的倍数
def add_to_16(value):
    value = value[::-1][len(value) - 10:]
    while len(value) % 16 != 0:
        value += '\0'
    # print(value)
    return str.encode(value)  # 返回bytes


# 加密方法
def app_encrypt(target):
    bs = AES.block_size
    pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    unpad = lambda s: s[0:-ord(s[-1])]
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 先进行aes加密
    padData = _padData(bytes(target, encoding='utf-8'))
    encrypt_aes = aes.encrypt(padData)
    # encrypt_aes = aes.encrypt(pad(bytes(target, encoding='utf-8')))
    # 用base64转成字符串形式
    encrypted_target = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    encrypted_target = encrypted_target.replace('+', '-').replace('/', '_')
    print(encrypted_target)
    return encrypted_target


# 解密方法
def app_decrypt(target):
    bs = AES.block_size
    unpad = lambda s: s[0:-ord(s[-1])]
    # 秘钥
    key = 'ed331c109fd84d6a83f34b9d1c0512a0'
    # 密文
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(target.encode(encoding='utf-8'))
    # 执行解密密并转码返回str
    # decrypted_target = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','')

    decrypted_target = _unpadData(aes.decrypt(base64_decrypted).decode('utf-8'))
    decrypted_target = decrypted_target.replace('\0', '').replace('+', '-').replace('/', '_')
    print(decrypted_target)

    return decrypted_target


def _padData(data):
    """
    按AES加密的要求，填充内容，使其为block_size的整数倍
    """
    block_size = 16
    padding = b"\0"
    padData = data + (block_size - len(data) % block_size) * padding
    return padData


def _unpadData(data):
    """
    删除填充数据
    """
    padding = b"\0"
    index = -1
    while data[index] == padding[0]:
        index += -1
    if index != -1:
        return data[0: index + 1]
    else:
        return data


if __name__ == '__main__':
    app_encrypt('13401089058')
    app_decrypt('YszAva_hSreV7iWQ-rz-fw==')