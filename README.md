# AtCoder Development Environment

AtCoder での競技プログラミングを効率化するための開発環境です。
Python (`uv`) を使用したシンプルな構成になっています。

## 1. 環境構築

### Python 環境 (uv / online-judge-tools)
このプロジェクトでは Python のパッケージ管理に `uv` を使用しており、`online-judge-tools` (`oj`) も依存関係としてインストールされます。

```bash
# uv のインストール (未インストールの場合)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係の同期 (.venv の作成と online-judge-tools のインストール)
uv sync
```


---

## 2. online-judge-tools のパッチ適用 (MiB 対応)

AtCoder のメモリ制限表記が `MB` から `MiB` に変更されたことに伴い、現時点の `oj` ではエラーが発生する場合があります。以下の手順で手動パッチを適用してください。

1. **対象ファイルの確認**
   `.venv` 内の `onlinejudge/service/atcoder.py` を開きます。
   (パスの例: `.venv/lib/python3.x/site-packages/onlinejudge/service/atcoder.py`)

2. **正規表現の修正**
   `Memory Limit` をパッチしている箇所（通常 `_from_html` メソッド内）の正規表現に `MiB` を追加します。

   ```python
   # 修正前
   r'^(メモリ制限|Memory Limit): ([0-9.]+) (KB|MB)'
   # 修正後
   r'^(メモリ制限|Memory Limit): ([0-9.]+) (KB|KiB|MB|MiB)'
   ```

3. **単位変換ロジックの修正**
   取得した単位をバイトに変換する処理に `MiB` / `KiB` を追加します。

   ```python
   if memory_limit_unit == 'KB':
       memory_limit_byte = int(float(memory_limit_value) * 1000)
   elif memory_limit_unit == 'KiB':
       memory_limit_byte = int(float(memory_limit_value) * 1024)
   elif memory_limit_unit == 'MB':
       memory_limit_byte = int(float(memory_limit_value) * 1000 * 1000)
   elif memory_limit_unit == 'MiB':
       memory_limit_byte = int(float(memory_limit_value) * 1024 * 1024)
   ```

---

## 3. ログインと初期設定

### AtCoder へのログイン
ツールが問題取得や提出を行えるよう、ログイン情報を登録します。

```bash
# online-judge-tools のログイン
uv run oj login https://atcoder.jp/
```

---

## 4. 便利設定 (.bashrc)

どこからでも `ac` コマンドを呼び出せるように、`.bashrc` にエイリアスを追加することをお勧めします。

```bash
# .bashrc に追加
alias ac='uv run /home/mugi2525/atcoder/ac'
```

設定を反映：
```bash
source ~/.bashrc
```

---

## 5. 使い方 (ac コマンド)

エイリアスを設定した後は、`ac` と打つだけで取得・テストをスムーズに行えます。
提出は `oj` コマンドまたはブラウザから行ってください。

```bash
# 問題の取得 (例: ABC 300)
ac fetch abc 300

# テストの実行 (問題ディレクトリ内で実行)
cd abc/300/a
ac test
```

`ac test` は、`main.cpp` と `main.py` のうち、**最後に更新された方**を自動的に判別してテストを実行します。
