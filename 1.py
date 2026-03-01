import requests

base_url = "https://yjs.job1001.com/job/index.htm?web_type=rensheju"
headers = {
    'cookie': 'SESSION=cc2cfdce-0188-4789-af58-3db433442589; _abfpc=f5cfab7898fc2c85739924dd04122395f2ee434d_2.0; cna=bd9822c9740ed993dcd01daef436a1d6; aliyungf_tc=6afd16353c5ae83b60140d2cfa865fda1e68fc1b52ee4404ad62869bfd3240ee; XSRF-CCKTOKEN=aa18ade3dd4d017bcd1684a4afb5869f; CHSICC_CLIENTFLAGNCSS=6ec443fdbc43496007bbc5e11cc2f250; Hm_lvt_378ff17a1ac046691cf78376632d1ed4=1772288323; HMACCOUNT=9076C4B1BCD7AA82; CHSICC01=!4JAHdJZSwaG/Hh3zYxYLahOzddj6YwKM6F13kOXUHgr9lPy9Gx7rmV4McG4JO4zV+2r4QthdWJ1M; CHSICC_CLIENTFLAGSTUDENT=d95ec280c3d6e85e31526e7d065c89d7; _gid=GA1.2.1828845838.1772288324; _ga=GA1.1.1462377412.1767772369; acw_tc=2f6fc15117722938012897882e00a08024b341da9dc37ff79783acab121486; _ga_6CXWRD3K0D=GS2.1.s1772293804$o4$g0$t1772293804$j60$l0$h0; Hm_lpvt_378ff17a1ac046691cf78376632d1ed4=1772293805',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}

response = requests.get(base_url, headers=headers, verify=False)
response.encoding = response.apparent_encoding
text = response.text

def write_html(html_file, html):
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
        print(f'文件{html_file}写入成功')

write_html('1.html', text)