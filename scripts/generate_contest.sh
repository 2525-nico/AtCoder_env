#!/bin/bash

# Usage: ./generate_contest.sh abc 300
TYPE=$1
NUMBER=$2

if [ -z "$TYPE" ] || [ -z "$NUMBER" ]; then
    echo "Usage: $0 <type(abc/arc/agc)> <number>"
    exit 1
fi

CONTEST_ID="${TYPE}${NUMBER}"
BASE_DIR="/home/mugi2525/atcoder/${TYPE}/${NUMBER}"

# すでにディレクトリが存在する場合は確認
if [ -d "$BASE_DIR" ]; then
    echo "Directory ${BASE_DIR} already exists."
    read -p "Overwrite? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[yY]$ ]]; then
        exit 1
    fi
    rm -rf "$BASE_DIR"
fi

mkdir -p "/home/mugi2525/atcoder/${TYPE}"
cd "/home/mugi2525/atcoder/${TYPE}"

# acc new
acc new "$CONTEST_ID"
# acc new が作成するのは contest_id 名のディレクトリなのでリネーム
mv "$CONTEST_ID" "$NUMBER"
cd "$NUMBER"

# aからgまで（存在するもの）に対して追加処理
for problem in */; do
    problem=$(basename "$problem")
    echo "Processing Problem ${problem}..."
    
    cd "$problem"
    
    # Pythonテンプレートを追加でコピー
    cp "/home/mugi2525/.config/atcoder-cli-nodejs/python/main.py" "main.py"
    
    # 問題URLの取得 (acc-config等から推測可能だが、基本は atcoder.jp/contests/CONTEST_ID/tasks/CONTEST_ID_problem)
    PROBLEM_URL="https://atcoder.jp/contests/${CONTEST_ID}/tasks/${CONTEST_ID}_${problem}"
    
    # 問題文の挿入
    /home/mugi2525/atcoder/.venv/bin/python /home/mugi2525/atcoder/scripts/add_statement.py "main.cpp" "$PROBLEM_URL"
    /home/mugi2525/atcoder/.venv/bin/python /home/mugi2525/atcoder/scripts/add_statement.py "main.py" "$PROBLEM_URL"
    
    cd ..
done

echo "Done! Contest ${CONTEST_ID} environment created at ${BASE_DIR}"
