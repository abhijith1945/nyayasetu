import os
content = open(os.path.join(os.path.dirname(__file__), '_justice_content.txt'), 'r', encoding='utf-8').read()
path = os.path.join('c:/Users/abhij/techashy_hack/frontend/src/pages', 'JusticeLinkPage.jsx')
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done: JusticeLinkPage.jsx")
