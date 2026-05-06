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
        statement_element = soup.select_one('#task-statement')
        if not statement_element:
            return ""
        
        # 「問題文」セクションを抽出（日本語）
        sections = statement_element.select('section')
        statement_text = ""
        for section in sections:
            h3 = section.select_one('h3')
            if h3 and '問題文' in h3.get_text():
                h3.extract() # "問題文" という見出し自体は削除
                
                # 各行をきれいに抽出するための処理
                lines = []
                # <p> や <ul> などをブロック単位で処理する
                for child in section.children:
                    if child.name in ['p', 'div']:
                        # ブロック内の <br> は改行に置換
                        for br in child.find_all('br'):
                            br.replace_with('\n')
                        text = child.get_text().strip()
                        if text:
                            lines.append(text)
                    elif child.name in ['ul', 'ol']:
                        for li in child.find_all('li'):
                            lines.append('- ' + li.get_text().strip())
                
                if not lines:
                    # もしブロック要素が取れなかった時のフォールバック
                    lines.append(section.get_text().strip())
                
                raw_text = '\n'.join(lines)
                
                # 連続する余分な改行を1つにまとめる
                statement_text = re.sub(r'\n+', '\n', raw_text)
                break
        
        return statement_text
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
