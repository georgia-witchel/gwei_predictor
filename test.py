import requests, json, csv

url = 'https://etherscan.io/chart/gasprice\?output\=csv'
res = requests.get(url)

with requests.Session() as s:
    download = s.get(url)

    decoded_content = download.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    for row in my_list:
        print(row)