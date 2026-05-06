#!/bin/bash

# ===== ユーザー依存のパス設定 =====
PROJECT_ROOT="/home/natsuko/AtCoder_env"
VENV_PYTHON="${PROJECT_ROOT}/.venv/bin/python"
SCRIPTS_DIR="${PROJECT_ROOT}/scripts"
# ===============================

# Usage: ./generate_contest.sh abc 300
TYPE=$1
NUMBER=$2

if [ -z "$TYPE" ] || [ -z "$NUMBER" ]; then
    echo "Usage: $0 <type(abc/arc/agc)> <number>"
    exit 1
fi

CONTEST_ID="${TYPE}${NUMBER}"
BASE_DIR="${PROJECT_ROOT}/${TYPE}/${NUMBER}"

# すでにディレクトリが存在する場合は確認
if [ -d "$BASE_DIR" ]; then
    echo "Directory ${BASE_DIR} already exists."
    read -p "Overwrite? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[yY]$ ]]; then
        exit 1
    fi
    rm -rf "$BASE_DIR"
fi

mkdir -p "$BASE_DIR"
cd "$BASE_DIR"

# Python スクリプトでコンテスト情報を取得・問題ディレクトリを作成
cat > /tmp/setup_contest.py << 'PYSCRIPT'
import sys
import os
import json
from pathlib import Path

contest_id = sys.argv[1]
base_dir = Path(sys.argv[2])

# contest.acc.json を作成
contest_info = {
    "name": "",
    "tasks": []
}

with open(base_dir / 'contest.acc.json', 'w') as f:
    json.dump(contest_info, f)

# 各問題のディレクトリを作成（a～g）
for problem_label in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'ex']:
    problem_dir = base_dir / problem_label
    problem_dir.mkdir(exist_ok=True)
    
    # main.cpp と main.py を作成
    cpp_template = '''#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    return 0;
}
'''
    
    py_template = '''def solve():
    pass

if __name__ == "__main__":
    solve()
'''
    
    (problem_dir / 'main.cpp').write_text(cpp_template)
    (problem_dir / 'main.py').write_text(py_template)
    
    # tests ディレクトリを作成
    tests_dir = problem_dir / 'tests'
    tests_dir.mkdir(exist_ok=True)

print(f"Created problem directories for {contest_id}")
PYSCRIPT

# Python スクリプトを実行
$VENV_PYTHON /tmp/setup_contest.py "$CONTEST_ID" "$BASE_DIR"

# 問題文をコメントとして各ファイルに追加
echo "Adding problem statements..."
for problem_label in a b c d e f g ex; do
    problem_dir="$BASE_DIR/$problem_label"
    if [ -d "$problem_dir" ]; then
        PROBLEM_URL="https://atcoder.jp/contests/${CONTEST_ID}/tasks/${CONTEST_ID}_${problem_label}"
        
        # main.cpp と main.py に問題文を追加
        $VENV_PYTHON "${SCRIPTS_DIR}/add_statement.py" "$problem_dir/main.cpp" "$PROBLEM_URL" 2>/dev/null || true
        $VENV_PYTHON "${SCRIPTS_DIR}/add_statement.py" "$problem_dir/main.py" "$PROBLEM_URL" 2>/dev/null || true
    fi
done

# サンプルテストをダウンロード
echo "Downloading sample test cases..."
$VENV_PYTHON -m oj dl "https://atcoder.jp/contests/${CONTEST_ID}" 2>/dev/null || true

echo "Done! Contest ${CONTEST_ID} environment created at ${BASE_DIR}"


