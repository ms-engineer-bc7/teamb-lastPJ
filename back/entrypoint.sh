#!/bin/sh

# データベースの起動を待つ
echo "Waiting for DB to be ready..."
while ! nc -z db 5432; do   
  sleep 1
done
echo "DB started."

# マイグレーションとシーディングを実行
echo "Running migrations..."
npx prisma migrate deploy

# Pythonによるシーディングを実行
echo "Seeding database..."
python prisma/seed.py
# npx prisma db seed

# アプリケーションを起動
echo "Starting application..."
exec "$@"
