import urllib.request, json

url = 'https://api.github.com/repos/mlm-games/twrp_lenovo_7305x_m7_mt8765_P/actions/runs/10829364374'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Run ID:', data.get('id'))
        print('Status:', data.get('status'))
        print('Conclusion:', data.get('conclusion'))
        print('Created at:', data.get('created_at'))
        print('Updated at:', data.get('updated_at'))
        print('Run URL:', data.get('html_url'))
        print('Jobs URL:', data.get('jobs_url'))
        print('Logs URL:', data.get('logs_url'))
except Exception as e:
    print('Error:', e)
