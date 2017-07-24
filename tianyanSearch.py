# coding: utf-8
'''
    题目：用python实现从天眼查提取指定公司的所有股东。如：

    1.http://www.tianyancha.com/search 这个页面是搜索入口
    2.输入一个天眼查中唯一存在的公司名，如：深圳市腾讯计算机系统有限公司
    3.从结果页面中提取股东信息，如：http://www.tianyancha.com/company/9519792 中展示的"许晨晔"等姓名

    思考：如果在短时间内抓取很多公司，可能会触发对方的限制，请问有哪些手段应对，让爬虫正常工作。
    答：（1）伪装成浏览器（2）使用代理IP（3）操作速度不要太快（4）使用不同的账号操作

    created by yangpan 2017.7.22
'''

import requests
from selenium import webdriver
import time
from lxml import etree
import pandas as pd

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.933.400 QQBrowser/9.4.8699.400'}

def create_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificatie-errors')
    driver = webdriver.Chrome(chrome_options = options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    return driver

if __name__ == '__main__':
    # 加载driver
    driver = create_chrome_driver()
    # 入口url
    url = 'http://www.tianyancha.com/search'
    try:
        # （1）获得response——由于入口页面需要点击“搜索”触发事件，所以用selenium的ChromeDriver实现比较方便
        driver.get(url)
        # 输入一个天眼查中唯一存在的公司名，如：深圳市腾讯计算机系统有限公司
        company_name = '北京百度网讯科技有限公司'
        # 获取操作对象（搜索框）
        search_element = driver.find_element_by_css_selector('input#live-search')
        click_element = driver.find_element_by_css_selector('div.input-group-addon.input-search-v1')
        # 向搜索框输入内容
        company_input = search_element.send_keys(company_name)
        # （2）提交搜索请求
        click_element.click()
        # 等待一会
        time.sleep(5)

        # （3）解析结果页面的url
        elements = driver.find_elements_by_css_selector('div.col-xs-10.search_repadding2.f18 > a')
        for element in elements:
            if element.find_element_by_css_selector('span').text == company_name:
                res_url = element.get_attribute('href')
                break
        # 获取结果页面内容
        res_data = requests.get(res_url, headers = headers)
        # 使用lxml方式解析股东信息
        selector = etree.HTML(res_data.text)
        stockholders = selector.xpath('//*[@id="_container_holder"]/div/table/tbody/tr')
        users = []
        ratios = []
        paid_times = []
        for stockholder in stockholders:
            user = stockholder.xpath('./td[1]/a')[0].text.strip()
            ratio = stockholder.xpath('./td[2]/div/div/span')[0].text.strip()
            paid_time = ''
            for i, pt in enumerate( stockholder.xpath('./td[3]/div/span') ):
                if i == 0:
                    paid_time += pt.text.strip()
                else:
                    paid_time += ',' + pt.text.strip()

            users.append(user)
            ratios.append(ratio)
            paid_times.append(paid_time)

        # 借助pandas实现数据可视化
        stockholder_dict = {'股东': users,
                            '出资比例': ratios,
                            '认缴出资': paid_times}
        stockholder_df = pd.DataFrame(stockholder_dict)
        print(stockholder_df)

    except Exception as e:
        print('Raise exception:{}'.format(e))
    finally:
        if driver:
            driver.quit()
