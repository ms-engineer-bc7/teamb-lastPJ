"use client";

import React, { useState } from 'react';
import axios, { AxiosError } from 'axios';

// 位置情報を含む駅情報の型定義
interface StationInfo {
  name: string;
  location: {
      lat: number;
      lng: number;
  };
}

// フォームで使用するプロップスの型定義が必要な場合はここに追加します
interface PlaceFormProps {}


const PlaceForm: React.FC<PlaceFormProps> = () => {
  const [stationName, setStationName] = useState<string>('');
  const [visitType, setVisitType] = useState<string>('');
  const [stationInfo, setStationInfo] = useState<StationInfo | null>(null);
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');

  const fetchRandomStation = async () => {
      try {
          const response = await axios.get(`http://localhost:8000/find-station/`, { params: { address: stationName } });
          console.log('Random station response:', response.data); // 追加：ランダムに選ばれた駅のレスポンスをログに出力
          setStationInfo({
              name: response.data.random_station,
              location: { lat: response.data.latitude, lng: response.data.longitude }
          });
      } catch (error: any) {
          console.error('Error fetching random station:', error); // 追加：エラー時のログを出力
          setError('駅情報の取得に失敗しました');
      }
  };

  const fetchPlacesRecommendation = async () => {
      if (!stationInfo) {
          setError('駅情報が設定されていません');
          return;
      }
      try {
          const { lat, lng } = stationInfo.location;
          const response = await axios.post('http://localhost:8000/places/', {
              language: 'ja',
              station_name: stationInfo.name,
              visit_type: visitType,
              radius: 2000,
              latitude: lat,
              longitude: lng
          });
          console.log('Places recommendation response:', response.data); // 追加：おすすめ情報のレスポンスをログに出力

          setMessage(response.data.message);
      } catch (error: any) {
          setError('おすすめ情報の取得に失敗しました');
      }
  };

  return (
    <div>
    <div>
      最寄り駅入力：
      <form onSubmit={(e) => { e.preventDefault(); fetchRandomStation(); }}>
        <input
          type="text"
          value={stationName}
          onChange={(e) => setStationName(e.target.value)}
          placeholder="最寄り駅を入力してください"
        />
        <button type="submit">送信</button>
      </form>
    </div>
    <div>
      {stationInfo && <p>あなたにおすすめの駅：{stationInfo.name}</p>}
    </div>
    <div>
      <select value={visitType} onChange={(e) => setVisitType(e.target.value)}>
        <option value="">誰と一緒に行きますか？</option>
        <option value="一人">一人</option>
        <option value="子連れ">子連れ</option>
        <option value="カップル">カップル</option>
      </select>
      <button onClick={fetchPlacesRecommendation}>recommend</button>
    </div>
    <div>
      {message && <ul>{message.split(', ').map((place, index) => <li key={index}>{place}</li>)}</ul>}
      {error && <p>{error}</p>}
    </div>
  </div>
);
};

export default PlaceForm;





