# Node.js lts image
FROM node:lts

# ワーキングディレクトリを指定
WORKDIR /front/src/app

# package.json と package-lock.json をコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install --save-dev @firebase/app @firebase/auth @firebase/analytics @types/firebase

# Firebase Toolsのインストール
RUN npm install -g firebase-tools

# Firebase SDKのインストール
RUN npm install firebase

# 同一ディレクトリ内のファイルを全てコピー
COPY . .

# 3000番ポートでリッスン
EXPOSE 3000

# React の起動
CMD ["npm", "run", "dev"]

# # アプリケーションを本番環境用にビルド
# RUN npm run build

# # サーバーを起動（本番用）
# CMD ["node", "build/server.js"] # この行は実際のビルド出力とサーバーファイルに基づいて調整してください
