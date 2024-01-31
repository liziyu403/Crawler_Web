import requests
from bs4 import BeautifulSoup
import csv

def crawl_page(url):
    response = requests.get(url)
    results = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有符合条件的 bloc
        blocs = soup.find_all('tr', {'data-toggle-target': True, 'data-toggle-group': 'laureate-details'})

        # 遍历每个 bloc
        for bloc in blocs:
            # 找到 a 标签
            a_tag = bloc.find('a', class_='tw-cursor-pointer')

            # 获取学校名称和链接
            school_name = a_tag.text.strip()
            school_url = a_tag['href']

            # 请求学校页面
            school_response = requests.get(school_url)

            if school_response.status_code == 200:
                school_soup = BeautifulSoup(school_response.text, 'html.parser')

                # 找到包含 "Moyenne au bac des intégrés" 的 span
                moyenne_span = school_soup.find('span', class_='tw-font-medium', string='Moyenne au bac des intégrés')

                if moyenne_span:
                    # 找到评分信息所在的块
                    score_block = moyenne_span.find_next('div', class_='tw-w-full tw-pt-3 sm:tw-pr-4 sm:tw-w-auto sm:tw-pt-0 tw-font-medium tw-text-right')

                    # 获取评分信息
                    score = score_block.text.strip()

                    # 将逗号替换为点
                    score = score.replace(',', '.')

                    # 将结果添加到列表中
                    results.append([school_name, score, school_url])
                else:
                    print(f'在学校 {school_name} 的页面中找不到 "Moyenne au bac des intégrés" 信息。')
            else:
                print(f'无法获取学校 {school_name} 的页面。状态码:', school_response.status_code)

    else:
        print('无法获取页面。状态码:', response.status_code)

    return results

# 自定义排序函数，处理带斜杠的评分
def custom_sort(score):
    try:
        return float(score.split('/')[0])
    except ValueError:
        return 0

# 要爬取的多个页面
urls = [
    'https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html?page=1',
    'https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html?page=2',
    'https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html?page=3'
    'https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html?page=4'
]

# 创建一个 CSV 文件，并写入表头
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['工程师学校名称', '高考BAC录取均分', '学校评分网址'])

    # 遍历每个页面的结果，将数据写入 CSV 文件
    all_results = []
    for url in urls:
        page_results = crawl_page(url)
        all_results.extend(page_results)

    # 按照分数从高到低排序
    # all_results.sort(key=lambda x: custom_sort(x[1]), reverse=True)

    csvwriter.writerows(all_results)

print('爬取完成，已生成 output.csv 文件。')
