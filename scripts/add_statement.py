import sys
import requests
from bs4 import BeautifulSoup
import os
import re
import os

def clean_latex(text):
    if not text:
        return ""
    
    # Handle subscripts and superscripts before removing braces
    sub_map = str.maketrans('0123456789aehijklmnoprstuvx', '₀₁₂₃₄₅₆₇₈₉ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ')
    super_map = str.maketrans('0123456789+-=()n', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ')
    
    def sub_repl(match):
        content = match.group(1) or match.group(2)
        if all(c in '0123456789aehijklmnoprstuvx' for c in content):
            return content.translate(sub_map)
        return match.group(0)
    
    def super_repl(match):
        content = match.group(1) or match.group(2)
        if all(c in '0123456789+-=()n' for c in content):
            return content.translate(super_map)
        return match.group(0)

    # _i or _{123}
    text = re.sub(r'_\{([^}]*)\}|_([0-9a-zA-Z])', sub_repl, text)
    # ^9 or ^{9+7}
    text = re.sub(r'\^\{([^}]*)\}|\^([0-9a-zA-Z])', super_repl, text)

    # LaTeX symbol replacements
    replacements = [
        (r'\\le', '<='),
        (r'\\leq', '<='),
        (r'\\ge', '>='),
        (r'\\geq', '>='),
        (r'\\ne', '!='),
        (r'\\neq', '!='),
        (r'\\dots', '...'),
        (r'\\ldots', '...'),
        (r'\\cdots', '...'),
        (r'\\vdots', '...'),
        (r'\\times', '×'),
        (r'\\pm', '±'),
        (r'\\infty', '∞'),
        (r'\\oplus', 'xor'),
        (r'\\text\{([^}]*)\}', r'\1'),
        (r'\$+', ''), # Remove dollar signs ($, $$)
        (r'\\', ''),   # Remove remaining backslashes
        (r'\{', ''),   # Remove remaining braces
        (r'\}', ''),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()

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
                        # 入出力例などのコードブロックは、サンプルセクション以外ならクリーンアップ
                        if not any(t in header for t in ['入力例', '出力例']):
                            text = clean_latex(text)
                        lines.append(text)
                elif child.name in ['p', 'div', 'blockquote']:
                    for br in child.find_all('br'):
                        br.replace_with('\n')
                    text = child.get_text().strip()
                    if text:
                        lines.append(clean_latex(text))
                elif child.name in ['ul', 'ol']:
                    for li in child.find_all('li'):
                        lines.append('- ' + clean_latex(li.get_text()))
                elif child.name is None and child.string and child.string.strip():
                    lines.append(clean_latex(child.string))
            
            if not lines:
                text = section.get_text().strip()
                if text.startswith(header):
                    text = text[len(header):].strip()
                lines.append(clean_latex(text))
            
            section_content = '\n'.join(lines)
            # 連続する改行を調整
            section_content = re.sub(r'\n{3,}', '\n\n', section_content)
            collected_text.append(section_content)
            collected_text.append("") # セクション間の空行
            
        return '\n'.join(collected_text).strip()
    except Exception as e:
        return f"Error fetching statement: {e}"

def add_statement_to_file(file_path, url, comment_char):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # すでにURLがある場合は追加しない
    if f"URL: {url}" in content:
        return

    header = f"{comment_char} URL: {url}\n"
    new_content = header + content
    
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
    
    # URLのみを追加
    add_statement_to_file(file_path, url, comment_char)

if __name__ == '__main__':
    main()
