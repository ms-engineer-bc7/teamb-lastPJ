"use client";
import { useState } from 'react';
import axios from 'axios';

// 場所の型を定義
type Place = {
    name: string;
    location: string;
  };

//LLMが返すレスポンスの型定義
type PlaceResponse = {
    message: string;
  };


export default function PlacesPage() {
  const [placesMessage, setPlacesMessage] = useState<string>("");
  const [location, setLocation] = useState('35.7356,139.6522');
  const [query, setQuery] = useState('公園');
  const [radius, setRadius] = useState(2000);

  const fetchPlaces = async () => {
    try {
      const response = await axios.get('http://localhost:8000/places/', {
        params: { location, query, radius, language: 'ja' },
      });

      // 型アサーションを使用してレスポンスの型を明示
      const data = response.data as PlaceResponse;
      setPlacesMessage(data.message); // ここでmessageをセット
    } catch (error) {
      console.error(error);
    }
  };
    // messageからplacesの配列を作成
    const places = placesMessage.split(', ').map((name, index) => ({ name, id: index }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', paddingTop: '20px' }}>
      {/* プルダウン式の入力フォーム */}
      <div>
        <select value={location} onChange={(e) => setLocation(e.target.value)}>
          <option value="35.7356,139.6522">今いる場所を教えてください</option>
          {/* 他の場所を追加 */}
        </select>
        <select value={query} onChange={(e) => setQuery(e.target.value)}>
          <option value="公園">誰と行きたいですか？</option>
          {/* 他のクエリを追加 */}
        </select>
        <select value={radius} onChange={(e) => setRadius(Number(e.target.value))}>
          <option value={2000}>どのように過ごしたい？</option>
          {/* 他の半径を追加 */}
        </select>
      </div>
      <button onClick={fetchPlaces}>場所を取得</button>
      
      {/* 取得したデータを表示 */}
      <ul>
        {places.map((place) => (
          <li key={place.id}>{place.name}</li>
        ))}
      </ul>
    </div>
  );
}