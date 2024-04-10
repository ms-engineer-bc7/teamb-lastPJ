# Node.js lts image
FROM node:lts

# ワーキングディレクトリを指定
WORKDIR /front/src/app

# アプリケーションの依存関係をインストール
# package.json と package-lock.json をコピー
COPY package*.json ./

# パッケージをインストール
RUN npm install

# 同一ディレクトリ内のファイルを全てコピー
COPY . .

# 3000番ポートでリッスン
EXPOSE 3000

# React の起動
CMD ["npm", "run", "dev"]