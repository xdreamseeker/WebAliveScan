import requests
import urllib3
import yaml

import rules
from concurrent.futures import ThreadPoolExecutor
from lib.utils.FileUtils import *
from lib.utils.tools import *
urllib3.disable_warnings()

def list_file(path):
    """
    列出目录下的所有文件
    @param path: 路径
    @return: 文件列表
    """
    file_list = list()
    for root, dirs, files in os.walk(path):
        [file_list.append(os.path.join(root, i)) for i in files]
    return file_list

def load_pocs(poc=''):
    """
    加载pocs
    @param poc: poc路径
    @return: poc列表
    """
    pocs = dict()
    if os.path.isdir(poc):
        pocs_file = list_file(poc)
    elif os.path.isfile(poc):
        pocs_file = [poc]
    else:
        pocs_file = list_file(poc)
    for i in pocs_file:
        poc = yaml.load(open(i, encoding='utf-8'), Loader=yaml.Loader)
        if poc and poc.get('name'):
            name = poc.get('name')
            pocs[name] = dict()
            pocs[name]['scan_rule'] = poc.get('scan_rule')
            pocs[name]['check_expression'] = poc.get('check_expression')
    print(pocs)
    return pocs

class DirbruteComp:
    def __init__(self, target, output, brute_result_list):
        self.target = target
        self.output = output
        self.output.bruteTarget(target)
        self.all_rules = []
        self.brute_result_list = brute_result_list

    def format_url(self, path):
        url = self.target
        if url.endswith('/'):
            url = url.strip('/')
        if not path.startswith('/'):
            path = '/' + path
        return url + path

    def init_rules(self):
        self.all_rules = load_pocs("C:\\Users\\itmain\\PycharmProjects\\WebAliveScan\\pocs")

    def compare_rule(self, rule, response_status, response_html, response_content_type):
        rule_status = [200, 206, rule.get('status')]
        if rule.get('status') and (response_status not in rule_status):
            return
        if rule.get('tag') and (rule['tag'] not in response_html):
            return
        if rule.get('type_no') and (rule['type_no'] in response_content_type):
            return
        if rule.get('type') and (rule['type'] not in response_content_type):
            return
        return True

    def brute(self, name,rule):
        user_agent = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        headers = {'User-Agent': user_agent, 'Connection': 'Keep-Alive', 'Range': 'bytes=0-102400'}
        for sub_url in rule['scan_rule']['path']:
            print(sub_url)
            url = self.format_url(sub_url)

            try:
                r = requests.get(url, headers=headers, verify=False, timeout=3)
            except Exception as e:
                return e
            size = FileUtils.sizeHuman(len(r.text))
            response_status = r.status_code
            response_html = r.text
            response_content_type = r.headers['Content-Type']
            # for white_rule in rules.white_rules:
            #     if self.compare_rule(white_rule, response_status, response_html, response_content_type):
            #         self.output.statusReport(url, response_status, size)
            # if not self.compare_rule(rule, response_status, response_html, response_content_type):
            #     return
            url_info = {'url': url, 'status': response_status, 'size': size.strip(),'component':rule.get("component", "")}
            self.brute_result_list.append(url_info)
            self.output.statusReport(url_info)
            # return [url, rule]

    def run(self):
        self.init_rules()

        for (name,rule) in self.all_rules.items():
            self.brute(name,rule)
        # with ThreadPoolExecutor(30) as pool:
        #     for rule in self.all_rules:
        #         pool.submit(self.brute, rule)

if __name__ == "__main__":
    brute_result_list = []
    output = Output()
    dirbrute = DirbruteComp("http://107.173.146.28", output, brute_result_list)
    dirbrute.run()