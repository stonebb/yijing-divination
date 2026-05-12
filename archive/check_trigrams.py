import json
with open('易经六十四卦完整库.json','r',encoding='utf-8') as f:
    data = json.load(f)
print('metadata keys:', list(data['metadata'].keys()))
print('trigrams count:', len(data['trigrams']))
for t in data['trigrams']:
    print(t)
