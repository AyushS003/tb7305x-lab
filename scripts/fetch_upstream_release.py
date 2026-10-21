import urllib.request, json

url = 'https://api.github.com/repos/mlm-games/twrp_lenovo_7305x_m7_mt8765_P/releases/tags/10829364374'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Release Name:', data.get('name'))
        print('Tag:', data.get('tag_name'))
        print('Created at:', data.get('created_at'))
        print('Body:\n', data.get('body'))
        print('Assets:')
        for a in data.get('assets', []):
            print(f"  {a['name']}: {a['size']} bytes, url: {a['browser_download_url']}")
except Exception as e:
    print('Error:', e)
