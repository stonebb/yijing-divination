import json

with open('易经六十四卦完整库.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hexagrams = data['hexagrams']
print(f'Total hexagrams: {len(hexagrams)}')
print('---')
for h in hexagrams:
    yao_count = len(h.get('yao_ci', []))
    issues = []
    if yao_count != 6:
        issues.append(f'yao_ci={yao_count}')
    if not h.get('judgment'):
        issues.append('no_judgment')
    if not h.get('image'):
        issues.append('no_image')
    if '??' in str(h.get('unicode_symbol','')):
        issues.append('bad_unicode')
    issue_str = ','.join(issues) if issues else 'OK'
    print(f"{h['id']:2d}: {h['name']} ({h['short_name']}) binary={h['binary']} {issue_str}")
