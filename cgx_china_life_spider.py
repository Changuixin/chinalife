# coding: utf8

import json
import requests
import re
import cgx_sql_data
import time
import cgx_verify
import os
import cgx_requests
import multiprocessing

from cgx_insured import InsuredPerson


class ChinaLifeSpider(object):
    def __init__(self, data):
        self.verify_code = ""
        self.msg = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        self.__cookies = {
            'JSESSIONID': None,
            'cookiename': 'value',
            'webVer': '1.0.0',
            'systemVer': '1.0.0',
        }
        self.policy_number = data[5].split('_')[0]  # 团单号 eg：2020350425689400026176
        self.Insured = InsuredPerson(data[5], data[4], data[2])  # 被保人

    # 刷新cookies
    def refresh_cookies(self):
        self.__cookies['JSESSIONID'] = self.__get_JSESSIONID()

    # 获取JSESSIONID
    def __get_JSESSIONID(self):
        GET_JSESSIONID_URL = 'https://ecssmobile.e-chinalife.com:8082/ocs/jsp/optimize/individual/queryIndividual.jsp'
        response = cgx_requests.get(url=GET_JSESSIONID_URL, headers=self.headers)
        JSESSIONID = ""
        for key, value in response.headers.items():
            if key == 'Set-Cookie':
                JSESSIONID_str = re.findall('JSESSIONID=.*?;', value)[0]
                JSESSIONID = JSESSIONID_str[len("JSESSIONID="):len(JSESSIONID_str) - 1]
                break
        # print("JSESSION = " + JSESSIONID)
        return JSESSIONID

    # 获取校验正确的验证码
    def get_correct_verify_code(self):
        for index in range(40):
            self.__download_verify_image()
            verify_code = self.__check_verify()
            # time.sleep(1)
            if verify_code is True:
                return True

        print('未能获取到正确的验证码')
        return False

    # 下载验证码图片
    def __download_verify_image(self):
        VERIFY_IMAGE_URL = 'https://ecssmobile.e-chinalife.com:8082/ocs/jcaptcha'
        r = cgx_requests.get(url=VERIFY_IMAGE_URL, headers=self.headers, cookies=self.__cookies)
        # print(r.status_code)  # 返回状态码
        if r.status_code == 200:
            with open('verify.png', 'wb') as file:
                file.write(r.content)
        del r

    # 检查验证码是否正确
    def __check_verify(self):
        # 识别验证码图片，获取对应的验证码
        self.verify_code = cgx_verify.get_verify_code()

        # 发送请求，校验获取到的验证码
        CHECK_VERIFY_CORRECTION_URL = 'https://ecssmobile.e-chinalife.com:8082/ocs/AjaxCollectAction.action?cmd=checkNumber_new'
        response = cgx_requests.post(url=CHECK_VERIFY_CORRECTION_URL, headers=self.headers, cookies=self.__cookies,
                                     data={
                                         'checkNumber': self.verify_code,
                                     })
        verify_code_is_true = json.loads(response.text).get('data')
        if verify_code_is_true == 'false':
            return False
        return True

    # 查询保单
    def query_policy(self):
        QUERY_POLICY_URL = 'https://ecssmobile.e-chinalife.com:8082/ocs/AjaxIndividualUpgradeAction.action?cmd=queryIndividualPolicyType'
        response = cgx_requests.post(url=QUERY_POLICY_URL, headers={
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://ecssmobile.e-chinalife.com:8082',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://ecssmobile.e-chinalife.com:8082/ocs/jsp/optimize/individual/queryIndividual.jsp',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }, cookies=self.__cookies, data={
            'cntrNo': self.policy_number,
            'insuredNameOne': self.Insured.name,
            'insuredBirthday': self.Insured.format_birthday_str,
            'queryMake': 1,
            'checkNumber': self.verify_code
        })
        query_result = json.loads(response.text).get('data')
        if query_result == 'L':
            # print('查询成功')
            return True
        elif query_result == 'Lerr':
            print('未查询到相关数据' + self.Insured.policy_number + '\t被投保人：' + self.Insured.name)
            return False
        else:
            print('查询失败：' + self.Insured.policy_number + '\t被投保人：' + self.Insured.name)
            return False

    # 查询保单list
    def __query_insured_policy_list(self):
        QUERY_INSURED_POLICY_LIST = "https://ecssmobile.e-chinalife.com:8082/ocs/AjaxGrpByInsureUpAction.action?cmd=queryInsuredListForSession"
        cgx_requests.post(url=QUERY_INSURED_POLICY_LIST, headers={
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://ecssmobile.e-chinalife.com:8082',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://ecssmobile.e-chinalife.com:8082/ocs/jsp/optimize/individual/insured/insuredList.jsp',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }, cookies=self.__cookies, data={
            'currentPage': 1,
        })

    # 优化准备就绪
    def __optimize_ready_over(self):
        OPTIMIZE_READY_OVER_URL = "https://ecssmobile.e-chinalife.com:8082/ocs/AjaxCollectAction.action?cmd=optimizeReadyshitOver"
        cgx_requests.post(url=OPTIMIZE_READY_OVER_URL, headers={
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://ecssmobile.e-chinalife.com:8082',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://ecssmobile.e-chinalife.com:8082/ocs/jsp/optimize/individual/insured/insuredList.jsp',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }, cookies=self.__cookies, data={
            'cntrNo': self.Insured.policy_number,
        })

    def download_file(self):
        self.__query_insured_policy_list()  # 查询被保险人的保单列表
        self.__optimize_ready_over()  # 提醒后端优化准备就绪

        while True:
            # time.sleep(5)
            GET_DOWNLOAD_FILE_INFO_URL = 'https://ecssmobile.e-chinalife.com:8082/ocs/AjaxCollectAction.action?cmd=getDownloadFileInfo_new'
            response = requests.post(url=GET_DOWNLOAD_FILE_INFO_URL, verify=False, headers={
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://ecssmobile.e-chinalife.com:8082',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://ecssmobile.e-chinalife.com:8082/ocs/jsp/optimize/individual/insured/insuredList.jsp',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }, cookies=self.__cookies, data={
                'cntrNo': self.Insured.policy_number_with_encryption,
            })
            self.msg = json.loads(response.text).get('data').get('msg')
            if not self.msg.isalpha():  # 学平险正在生成中
                continue
            else:
                break
        # time.sleep(5)

        # 下载文件
        DOWNLOAD_PDF_URL = "https://ecssmobile.e-chinalife.com:8082/ocs/AjaxCollectAction.action?cmd=downloadPdfFromLocal"
        download_response = cgx_requests.post(url=DOWNLOAD_PDF_URL, headers={
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://ecssmobile.e-chinalife.com:8082',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://ecssmobile.e-chinalife.com:8082/ocs/jsp/optimize/individual/insured/insuredList.jsp',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }, cookies=self.__cookies, data={
            'downloadUrl': self.msg,
            'downloadCntrNo': self.Insured.policy_number_with_encryption
        })

        # 保存文件
        if not os.path.exists('./学平险'):
            os.makedirs('学平险')
        if not os.path.exists('./学平险/' + self.policy_number):
            os.makedirs('./学平险/' + self.policy_number)

        with open('./学平险/' + self.policy_number + '/' + self.Insured.policy_number + ".pdf", 'wb') as file:
            file.write(download_response.content)
            print('下载成功：' + self.Insured.policy_number + ".pdf\t被投保人：" + self.Insured.name)


def get_data_list():
    sql_data = cgx_sql_data.SqlData()
    data_list = sql_data.select_all()
    return data_list


def run_without_multiprocess(policy_number='0', begin_number=0):
    index = 1
    data_list = get_data_list()
    for data in data_list:
        spider = ChinaLifeSpider(data)

        # 根据保单号筛选数据
        if policy_number != '0' and spider.policy_number != policy_number:
            continue

        # 根据个数筛选数据
        if index < begin_number:
            index += 1
            continue
        print(data)
        spider.refresh_cookies()
        spider.get_correct_verify_code()
        if spider.query_policy() is True:
            spider.download_file()
        del spider


def multiprocessing_run(policy_number='0', begin_number=0):
    def run(data):
        spider = ChinaLifeSpider(data)

        print(data)
        spider.refresh_cookies()
        spider.get_correct_verify_code()
        if spider.query_policy() is True:
            spider.download_file()
        del spider
        time.sleep(2)

    # 筛选出真正要循环的数据列表
    index = 1
    data_list = get_data_list()
    real_data_list = []
    for data in data_list:

        # 根据保单号筛选数据
        if policy_number != '0' and data[5].split('_')[0] != policy_number:
            continue

        # 根据个数筛选数据
        if index < begin_number:
            index += 1
            continue
        real_data_list.append(data)

    # 创建线程池
    p = multiprocessing.Pool(2)
    p.map(run, real_data_list)
    p.close()
    p.join()


def run(data):
    spider = ChinaLifeSpider(data)

    spider.refresh_cookies()
    spider.get_correct_verify_code()
    if spider.query_policy() is True:
        spider.download_file()

    del spider
    # time.sleep(2)


def multi_run(policy_number='0', begin_number=0, processing_cnt=4):
    # 筛选出真正要循环的数据列表
    index = 1
    data_list = get_data_list()
    real_data_list = []
    for data in data_list:

        # 根据保单号筛选数据
        if policy_number != '0' and data[5].split('_')[0] != policy_number:
            continue

        # 根据个数筛选数据
        if index < begin_number:
            index += 1
            continue
        real_data_list.append(data)

    # 创建线程池
    p = multiprocessing.Pool(processing_cnt)
    p.map(run, real_data_list)
    p.close()
    p.join()


if __name__ == '__main__':
    # run('2020350425689400026176', 11)
    # multiprocessing_run()

    multi_run(begin_number=0,
              processing_cnt=8,
              policy_number='2020350425689400026176',
              )
