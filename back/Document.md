# API仕様書

## 概要
ユーザーが入力した最寄り駅や住所をもとに、周辺のおすすめスポットを提案。外部APIとしてGoogle Places APIを使用。

## アクセストークン
なし

## ステータスコード

下記のコードを返却します。

| ステータスコード | 説明 |
| - | - |
| 200 | リクエスト成功 |
| 400 | 不正なリクエストパラメータを指定している |
| 404 | 存在しないURLにアクセス |
| 500 | 不明なエラー |

## 利用制限
APIの利用制限の設定なし

## 駅情報取得API

```
GET /find-station/
```
| パラメータ | 内容                | 必須 | デフォルト値 | 最大値 |
|------------|-------------------|------|-------------|--------|
| address    | 最寄り駅または住所       | ○    | "ja"        | ---    |
## Request
```
{
  "address": "東京都練馬区"
}
```

## Response
```
HTTP/1.1 200 OK
{
  "random_station": "練馬駅",
  "latitude": 35.7356,
  "longitude": 139.6522
}
```
## 処理概要
* find_station関数を呼び出して、入力された住所から最寄り駅と周辺の駅情報を取得。
* 周辺の駅情報からランダムに1つの駅を選択。
* 選択された駅の名前、緯度、経度を含むJSONレスポンスを返却。

## おすすめスポット提案API
```
POST /places/
```

| パラメータ        | 内容                    | 必須 | デフォルト値 | 最大値 |
|-----------------|-----------------------|------|-------------|--------|
| language        | 言語                    | ---  | "ja"        | ---    |
| station_name    | ランダムに選ばれた駅名        | ---  | ---         | ---    |
| visit_type      | 訪問タイプ                | ---  | ---         | ---    |
| radius          | 検索範囲の半径（メートル）    | ---  | 1000        | ---    |
| latitude        | 駅の緯度                  | ---  | ---         | ---    |
| longitude       | 駅の経度                  | ---  | ---         | ---    |
| how_to_spend_time | どんな時間を過ごしたいか   | ---  | ---         | ---    |


## Request
```
{
  "station_name": "練馬駅",
  "visit_type": "一人で",
  "latitude": 35.7356,
  "longitude": 139.6522,
  "how_to_spend_time": "のんびりとした"
}
```
## Response
```
HTTP/1.1 200 OK
{
  "message": "休日の過ごし方について提案させていただきますね。まずは、練馬駅周辺の石神井公園がおすすめです。広々とした公園内を散歩したり、ベンチでゆっくり本を読んだりと、のんびりとした時間を過ごせます。公園の中にある石神井池では、ボート遊びも楽しめますよ。..."
}
```
## 処理概要
* ランダムに選択された駅の緯度、経度、訪問タイプ、過ごし方などのパラメータを受け取る。
* Google Places APIを使用して、受け取ったパラメータに基づき、駅周辺のおすすめスポットを検索。
* 取得したスポット情報をLLM（Language Model）に渡し、訪問タイプや過ごし方に合わせたおすすめプランを生成。
* 生成されたおすすめプランをJSONレスポンスとして返却。
