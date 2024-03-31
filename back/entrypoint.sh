#!/bin/sh

# データベースが起動するのを待つ
echo "Waiting for DB to be ready..."
while ! nc -z db 5432; do   
  sleep 1
done
echo "DB started."

# マイグレーションとシーディングを実行
echo "Running migrations..."
npx prisma migrate deploy
echo "Seeding database..."
npx prisma db seed

# アプリケーションを起動
echo "Starting application..."
exec "$@"
