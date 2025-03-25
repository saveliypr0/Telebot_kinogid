import requests
from bs4 import BeautifulSoup


def escape_markdown_v2(text):
    special_characters = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in special_characters else char for char in text)

def parce_desc(link):
    conn_desc = requests.get(link)
    if conn_desc.status_code == 200:
        html = conn_desc.text
        soup = BeautifulSoup(html, 'lxml')
        info = soup.find(class_='itemExtraFields').text.replace('\n\n', '').strip()
        desc = soup.find(class_='itemFullText').find('p').text
        img = 'https://2016.kinofest.org' + soup.find(class_='itemImageBlock').find('img')['src']

        lines = info.split('\n')
        formatted_lines = []
        for i in range(0, len(lines), 2):
            if i == len(lines) - 1:
                formatted_lines.append(lines[i])
            else:
                formatted_lines.append(f"{lines[i].strip()} {lines[i + 1].strip()}")

        info = escape_markdown_v2('\n'.join(formatted_lines))
        info_format = f"""*{info.replace(': ', ':* ').replace('\n', '\n*')}*"""

        return info_format + f'\n{escape_markdown_v2(desc)}', img
