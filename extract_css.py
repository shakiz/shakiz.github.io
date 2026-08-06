import re

with open('guides/learn_flutter_nextjs_way.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find all <style>...</style> blocks
style_blocks = re.findall(r'<style>(.*?)</style>', html_content, flags=re.DOTALL)

# Concatenate all CSS
all_css = ""
for block in style_blocks:
    all_css += block + "\n"

# Write to css/learn_flutter_nextjs_way.css
with open('css/learn_flutter_nextjs_way.css', 'w', encoding='utf-8') as f:
    f.write(all_css)

# Remove all <style> blocks and replace the first one with a <link>
def replace_style(match):
    global first_replaced
    if not first_replaced:
        first_replaced = True
        return '<link rel="stylesheet" href="../css/learn_flutter_nextjs_way.css">'
    return ''

first_replaced = False
new_html = re.sub(r'[ \t]*<style>.*?</style>[ \t]*\n?', replace_style, html_content, flags=re.DOTALL)

with open('guides/learn_flutter_nextjs_way.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Extracted CSS and updated HTML.")
