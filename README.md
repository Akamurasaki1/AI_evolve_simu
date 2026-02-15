# AI_evolve_simu

AI進化シミュレーション - 遺伝的アルゴリズムを用いた文章進化システム

## 概要

このプロジェクトは、人間の選好を基に遺伝的アルゴリズムを使用して文章を進化させるシミュレーションです。A/Bテストの形式でユーザーが好みの文章を選択することで、世代を重ねるごとにより好まれる文章へと進化していきます。
readme作成、画面構成の作成に関してgithub copilotによるバイブコーディングを試してみました。

## プロジェクト構成

- `evolve_engine.py` - 遺伝的アルゴリズムの中核エンジン
- `evolve_api.py` - API サーバー実装
- `evolve_*.py` - 各種進化シミュレーションの実装
- `chose_api.js` - フロントエンドの選択API
- `index.html` - A/B選好テストのUI

## GitHub Copilot とこのリポジトリ

### GitHub Copilot Chat を有効化する方法

GitHub Copilot Chat のツール（コーディングエージェントなど）を使用するには、以下の手順に従ってください。

#### 1. GitHub Copilot のサブスクリプション

まず、GitHub Copilot のサブスクリプションが必要です：
- 個人アカウント: [GitHub Copilot のサブスクリプションページ](https://github.com/settings/copilot)で有効化
- 組織アカウント: 組織の管理者が GitHub Copilot Business または Enterprise を有効化する必要があります

#### 2. VS Code での設定

**VS Code に GitHub Copilot 拡張機能をインストール：**
1. VS Code を開く
2. 拡張機能ビュー（`Ctrl+Shift+X` / `Cmd+Shift+X`）を開く
3. 「GitHub Copilot」と「GitHub Copilot Chat」を検索してインストール
4. GitHub アカウントでサインインする

**このリポジトリで使用する：**
1. このリポジトリをクローンまたは開く
   ```bash
   git clone https://github.com/Akamurasaki1/AI_evolve_simu.git
   cd AI_evolve_simu
   ```
2. VS Code でプロジェクトフォルダを開く
3. Copilot Chat を開く（`Ctrl+Alt+I` / `Cmd+Alt+I` または サイドバーのチャットアイコン）

#### 3. GitHub Copilot Chat の使い方

Copilot Chat では、以下のようなことができます：

**コードの質問：**
```
このプロジェクトの evolve_engine.py はどのように動作しますか？
```

**コードの生成：**
```
新しい突然変異関数を追加して、文字列の長さも変化できるようにしてください
```

**リファクタリング：**
```
evolve_api.py のコードをより読みやすくリファクタリングしてください
```

**デバッグ：**
```
このエラーを修正してください: [エラーメッセージ]
```

#### 4. コーディングエージェント（GitHub Copilot Workspace）について

**重要な注意事項：**
- コーディングエージェント機能は、GitHub の Web UI または GitHub Copilot Workspace で利用できる機能です
- これらのツールは GitHub 側でホストされており、リポジトリ側から直接「有効化」することはできません
- 利用可能性は GitHub のサブスクリプションとアクセス権限に依存します

**GitHub.com で使用する場合：**
1. https://github.com/Akamurasaki1/AI_evolve_simu にアクセス
2. Issue や Pull Request ページで Copilot アイコンをクリック
3. 「Generate summary」や「Suggest fix」などの機能を使用

**GitHub Copilot Workspace を使用する場合：**
1. https://copilot-workspace.githubnext.com/ にアクセス
2. このリポジトリを開く
3. AI アシスタントに自然言語でタスクを依頼

### よくある質問

**Q: 「ツールが使えない」と表示される場合は？**
A: 以下を確認してください：
- GitHub Copilot のサブスクリプションが有効か
- VS Code の拡張機能が最新版か
- VS Code で GitHub アカウントにサインインしているか
- ネットワーク接続が正常か

**Q: VS Code 以外のエディタでも使えますか？**
A: はい、GitHub Copilot は以下のエディタでも利用できます：
- Visual Studio
- JetBrains IDE（IntelliJ IDEA、PyCharm など）
- Neovim
- Azure Data Studio

**Q: コーディングエージェントの機能にアクセスできません**
A: コーディングエージェント機能は段階的に展開されており、すべてのユーザーにすぐに利用可能とは限りません。GitHub のアナウンスメントをご確認ください。

## 使用方法

### 基本的な実行

```bash
# API サーバーを起動
python evolve_api.py

# ブラウザで index.html を開く
```

### 開発

```bash
# 依存関係のインストール（必要に応じて）
pip install -r requirements.txt  # requirements.txt がある場合
```

## ライセンス

このプロジェクトのライセンスについては、リポジトリのオーナーにお問い合わせください。

## 貢献

このプロジェクトへの貢献を歓迎します。Issue や Pull Request を自由に作成してください。
