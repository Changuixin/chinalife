import requests
import base64
import json


def readBase64Img():
    '''
    读取图片 并且转换成 base64 -> standard_b64encode
    :return: base64 图片
    '''
    with open('verify.png', 'rb') as fp:
        img = fp.read()
        img = base64.standard_b64encode(img)  # 需要转换成 base64
        return img


def get_verify_code():
    try:
        img = readBase64Img()
        url = 'http://127.0.0.1:8001/gecko'
        response = requests.post(url=url, data={
            'img': img
        })
        return json.loads(response.text).get('result')
    except:
        return ''

if __name__ == '__main__':
    get_verify_code()
