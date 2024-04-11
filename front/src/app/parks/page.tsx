"use client";
import { useState } from 'react';
import axios from 'axios';

// LLMが返すレスポンスの型定義
type PlaceResponse = {
  message: string;
};

export default function PlacesPage() {
  const [location, setLocation] = useState('35.7356,139.6522');
  const [query, setQuery] = useState(''); //初期値を空の文字列で設定
  const [radius, setRadius] = useState(2000);
  const [placesMessage, setPlacesMessage] = useState<string>("");

  // POSTリクエストで場所を取得する関数
  const fetchPlaces = async () => {
    try {
      // リクエストボディの作成
      const requestBody = {
        location,
        query, // これはユーザーの入力から取得した値
        radius,
        language: 'ja',
      };

      // POSTリクエストの送信
      const response = await axios.post('http://localhost:8000/places/', requestBody);

      // レスポンスの受け取りと状態の更新
      const data: PlaceResponse = response.data;
      setPlacesMessage(data.message);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', paddingTop: '20px' }}>
      {/* テキスト入力フォーム */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="行きたい場所を入力してください"
      />
      <button onClick={fetchPlaces}>場所を取得する</button>
      
      {/* 取得したデータを表示 */}
      <ul>
        {placesMessage.split(', ').map((name, index) => (
          <li key={index}>{name}</li>
        ))}
      </ul>
    </div>
  );
}
