# ベースイメージとしてPythonイメージを選択
FROM python:3.9

# Pythonアプリケーションの作業ディレクトリを設定
WORKDIR /app

# Pythonアプリケーションの依存関係ファイルをコピー
COPY requirements.txt ./

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# langchain-openaiとlangchainのインストールを追加
RUN pip install langchain-openai langchain

# テストに必要なパッケージインストール
RUN pip install pytest

# Node.jsのインストール (Prismaが必要とするため)
# RUN apt-get update && \
    # apt-get install -y curl netcat-openbsd && \
    # curl -sL https://deb.nodesource.com/setup_lts.x | bash - && \
    # apt-get install -y nodejs && \
    # npm install -g prisma @prisma/client && \
    # rm -rf /var/lib/apt/lists/*

# アプリケーションのファイルをコピー
COPY . .

# エントリポイントスクリプトのコピーと実行権限を付与
# COPY entrypoint.sh /usr/local/bin/

# 実行権限を付与
# RUN chmod +x /usr/local/bin/entrypoint.sh

# 8000番ポートをコンテナの外に公開
EXPOSE 8000

# エントリポイントとして設定
# ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# prisma generateを起動する
RUN ["/bin/bash", "-c", "prisma generate"]
# アプリケーションの起動コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]