import sys
import requests
from bs4 import BeautifulSoup
import os
import re

def get_problem_statement(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # AtCoderの問題文は通常 #task-statement の中にある
        # 日本語版を優先的に取得するため span.lang-ja を探す
        statement_element = soup.select_one('span.lang-ja')
        if not statement_element:
            statement_element = soup.select_one('#task-statement')
        
        if not statement_element:
            return ""
        
        sections = statement_element.select('section')
        collected_text = []
        
        for section in sections:
            h3 = section.select_one('h3')
            if not h3:
                continue
            
            header = h3.get_text().strip()
            
            # 抽出対象のセクション見出し
            targets = ['問題文', '制約', '入力', '出力', '入力例', '出力例']
            if not any(t in header for t in targets):
                continue
            
            # セクションの見出しを追加
            collected_text.append(f"--- {header} ---")
            
            # 各行を抽出
            lines = []
            
            for child in section.children:
                if child.name == 'h3':
                    continue
                if child.name == 'pre':
                    text = child.get_text().strip()
                    if text:
                        # 入出力例などのコードブロック
                        lines.append(text)
                elif child.name in ['p', 'div', 'blockquote']:
                    # ブロック要素内の br を改行に置換
                    for br in child.find_all('br'):
                        br.replace_with('\n')
                    text = child.get_text().strip()
                    if text:
                        lines.append(text)
                elif child.name in ['ul', 'ol']:
                    for li in child.find_all('li'):
                        lines.append('- ' + li.get_text().strip())
                elif child.name is None and child.string and child.string.strip():
                    # 素のテキストノード
                    lines.append(child.string.strip())
            
            if not lines:
                # フォールバック
                text = section.get_text().strip()
                if text.startswith(header):
                    text = text[len(header):].strip()
                lines.append(text)
            
            section_content = '\n'.join(lines)
            # 連続する改行を調整
            section_content = re.sub(r'\n{3,}', '\n\n', section_content)
            collected_text.append(section_content)
            collected_text.append("") # セクション間の空行
            
        return '\n'.join(collected_text).strip()
    except Exception as e:
        return f"Error fetching statement: {e}"

def add_statement_to_file(file_path, statement, comment_char):
    if not statement:
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # コメント形式に整形
    commented_statement = "\n".join([f"{comment_char} {line}" for line in statement.split('\n')])
    new_content = f"{comment_char} --- Problem Statement ---\n{commented_statement}\n{comment_char} --------------------------\n\n" + content
    
    with open(file_path, 'w') as f:
        f.write(new_content)

def main():
    if len(sys.argv) < 3:
        print("Usage: python add_statement.py <file_path> <problem_url>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    url = sys.argv[2]
    
    ext = os.path.splitext(file_path)[1]
    comment_char = "//" if ext in ['.cpp', '.hpp'] else "#"
    
    statement = get_problem_statement(url)
    if statement:
        add_statement_to_file(file_path, statement, comment_char)

if __name__ == '__main__':
    main()
