#!/bin/sh

# データベースが起動するのを待つ
echo "Waiting for DB to be ready..."
while ! nc -z db 5432; do   
  sleep 1
done
echo "DB started."

# マイグレーションとシーディングを実行
echo "Running migrations..."

# npx prisma migrate deploy
# 4/7追加↓
npx prisma migrate deploy --schema /app/prisma/schema.prisma
# Pythonによるシーディングを実行
echo "Seeding database..."
python prisma/seed.py
# npx prisma db seed
# npx prisma db seed --schema /app/prisma/schema.prisma
python /app/prisma/seed.py

# アプリケーションを起動
echo "Starting application..."
exec "$@"
