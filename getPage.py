from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import time
from pymongo import MongoClient

base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

def get_page(page):
    params = {
        'containerid': '100103type=1&q=肖战',
        'page': page,
        'type':'all',
        'queryVal':'肖战',
        'featurecode':'20000320',
        'luicode':'10000011',
        'lfid':'106003type=1',
        'title':'肖战'
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(page)
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


#解析
def parse_page(json):
    if json:
        items = json.get('data').get('cards')

        for i in items:
            for item in i.get('card_group'):
                item = item.get('mblog')
                if item == None:
                    continue

                weibo = {}
                weibo['id'] = item.get('id')
                weibo['text'] = pq(item.get('text')).text()
                weibo['name'] = item.get('user').get('screen_name')
                if item.get('longText') != None :       #要注意微博分长文本与文本，较长的文本在文本中会显示不全，故我们要判断并抓取。
                    weibo['longText'] = item.get('longText').get('longTextContent')
                else:weibo['longText'] =None
                print(weibo['name'])
                print(weibo['longText'])
                weibo['attitudes'] = item.get('attitudes_count')
                weibo['comments'] = item.get('comments_count')
                weibo['reposts'] = item.get('reposts_count')
                weibo['time'] = item.get('created_at')

                yield weibo

if __name__ == '__main__':
    client = MongoClient()  # 连接mongodb
    db = client['weibo_1']  # 建立数据库
    collection = db['weibo_1']  # 建立表

    def save_to_mongo(result):  # 存入数据库
        if collection.insert(result):
            print('Saved to Mongo')

    for page in range(21, 200):  # 循环页面
        time.sleep(1)  # 设置睡眠时间，防止被封号
        json = get_page(page)
        results = parse_page(json)

        for result in results:
            save_to_mongo(result)
            print(result['time'])