# -*- coding: utf-8 -*-
import scrapy
import re
from ndbg.items import NdbgItem

class NbSpider(scrapy.Spider):
    name = 'nb'
    allowed_domains = ['money.163.com']
    # 从 stkcd.txt 中读取公司代码列表
    with open('stkcd.txt', 'r') as fp:
        stkcds = fp.readlines()
    # 设定要爬取的报告类型和年份
    year_list = ['2013年年度报告', '2014年年度报告', '2015年年度报告', '2016年年度报告', '2017年年度报告', '2018年年度报告']

    # 发起加载首页的请求
    def start_requests(self):
        for stkcd in self.stkcds:
            stkcd = re.sub(r'\s', '', stkcd)
            url = 'http://quotes.money.163.com/f10/gsgg_{},dqbg,0.html'.format(stkcd)
            yield scrapy.Request(url, callback=self.parse_first_page)

    # 处理首页
    def parse_first_page(self, response):
        # 构建待处理的报告字典
        report_to_parse = {}
        # 处理当前页面列表的每一行
        trs = response.xpath('//table[@class="table_bg001 border_box limit_sale"]//tr')[1:]
        # 发现待处理的报告，则加入字典
        for tr in trs:
            title = tr.xpath('.//td[1]/a/@title').get()
            if title[-9:] in self.year_list:
                report_url = response.urljoin(tr.xpath('.//td[1]/a/@href').get())
                report_to_parse[title] = report_url
        # 发现报告被更新，则更新字典
        for tr in trs:
            if title[-5:] == '（更新后）':
                title = title[:-5]
                if title[-9:] in self.year_list:
                    report_url = response.urljoin(tr.xpath('.//td[1]/a/@href').get())
                    report_to_parse[title] = report_url
        # 发起加载待处理报告的请求
        for item in report_to_parse.items():
            title = item[0]
            report_url = item[1]
            yield scrapy.Request(report_url, meta={'title': title}, callback=self.parse_report)
        # 判断是否有下一页
        pages = response.xpath('//div[@class="mod_pages"]//a')[:-1]
        # 13年之后的报表差不多在前四页，没必要查看更多页
        if len(pages) > 3:
            next_pages_list = pages[:3]
        else:
            next_pages_list = pages
        for next_page in next_pages_list:
            next_url = response.urljoin(next_page.xpath('./@href').get())
            yield scrapy.Request(next_url, callback=self.parse_next_pages)

    def parse_next_pages(self, response):
        # 构建待处理的报告字典
        report_to_parse = {}
        # 处理当前页面列表的每一行
        trs = response.xpath('//table[@class="table_bg001 border_box limit_sale"]//tr')[1:]
        # 发现待处理的报告，则加入字典
        for tr in trs:
            title = tr.xpath('.//td[1]/a/@title').get()
            if title[-9:] in self.year_list:
                report_url = response.urljoin(tr.xpath('.//td[1]/a/@href').get())
                report_to_parse[title] = report_url
        # 发现报告被更新，则更新字典
        for tr in trs:
            if title[-5:] == '（更新后）':
                title = title[:-5]
                if title[-9:] in self.year_list:
                    report_url = response.urljoin(tr.xpath('.//td[1]/a/@href').get())
                    report_to_parse[title] = report_url
        # 发起加载待处理报告的请求
        for item in report_to_parse.items():
            title = item[0]
            report_url = item[1]
            yield scrapy.Request(report_url, meta={'title': title}, callback=self.parse_report)

    def parse_report(self, response):
        # 获取标题
        title = '{}附注'.format(response.meta['title'])
        # 获取公司代码
        code = response.url.split('/')[-1].split('_')[1]
        # 获取年份
        year = re.search(r'[0-9]{4}', title).group(0)
        # 获取纯文字的报告全文
        text = ''.join(response.xpath('//div[@class="report_detail"]//text()').getall())
        # 删除空字符
        text = re.sub('\s', '', text)
        #-------------------------#
        # 爬取全文请解除这部分注释
        # item = NdbgItem(code=code, year=year, title=title, content=text)
        # yield item
        # 爬取全文请解除这部分注释并删除之后的内容
        #-------------------------#
        # 选取报表附注，这部分的逻辑并不是很好
        pattern11 = re.compile('、公司基本情况(.+)节备查文件')
        pattern12 = re.compile('公司的基本情况(.+)节备查文件')
        pattern13 = re.compile('公司基本情况(.+)节备查文件')
        pattern14 = re.compile('、基本情况(.+)节备查文件')
        pattern15 = re.compile('集团的基本情况(.+)节备查文件')
        pattern16 = re.compile('集团基本情况(.+)节备查文件')
        pattern17 = re.compile('财务报表附注(.+)节备查文件')
        pattern18 = re.compile('公司概况(.+)节备查文件')
        pattern19 = re.compile('的基本情况(.+)节备查文件')
        pattern21 = re.compile('、公司基本情况(.+)关闭窗口')
        pattern22 = re.compile('公司的基本情况(.+)关闭窗口')
        pattern23 = re.compile('公司基本情况(.+)关闭窗口')
        pattern24 = re.compile('、基本情况(.+)关闭窗口')
        pattern25 = re.compile('集团的基本情况(.+)关闭窗口')
        pattern26 = re.compile('集团基本情况(.+)关闭窗口')
        pattern27 = re.compile('财务报表附注(.+)关闭窗口')
        pattern28 = re.compile('公司概况(.+)关闭窗口')
        pattern29 = re.compile('的基本情况(.+)关闭窗口')
        
        patterns = [pattern11, pattern12, pattern13, pattern14, pattern15, 
                    pattern16, pattern17, pattern18, pattern19, 
                    pattern21, pattern22, pattern23, pattern24, pattern25, 
                    pattern26, pattern27, pattern28, pattern29]
        for pattern in patterns:
            notes = re.search(pattern, text)
            if notes!=None:
                break 
        content = notes.group(1)
        # 生成item
        item = NdbgItem(code=code, year=year, title=title, content=content)
        yield item
