"use client";
import React, { useState } from 'react';
import axios from 'axios';
import IconButton, { IconType } from '../button/IconButton';// IconButton コンポーネントをインポート


// 位置情報を含む駅情報の型定義
interface StationInfo{ 
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
  const [visitType, setVisitType] = useState<string>('');// デフォルト値入力もできます
  const [howToSpendTime, setHowToSpendTime] = useState<string>('');// デフォルト値入力もできます
  const [stationInfo, setStationInfo] = useState<StationInfo | null>(null);
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');

  const fetchRandomStation = async () => {
    if (!stationName) {
        setError('最寄り駅の名前を入力してください。');
        return;
    }
    console.log(`Requesting data for address: ${stationName}`);  // デバッグ情報の出力
    try {
        const response = await axios.get(`http://localhost:8000/find-station/`, { params: { address: stationName } });
        console.log('Random station response:', response.data); // 追加：ランダムに選ばれた駅のレスポンスをログに出力
        setStationInfo({
            name: response.data.random_station,
            location: { lat: response.data.latitude, lng: response.data.longitude }
        });
        setError('');
    } catch (error: any) {
        console.error('Error fetching random station:', error);// 追加：エラー時のログを出力
        setError('駅情報の取得に失敗しました。');
    }
};

  const fetchPlacesRecommendation = async () => {
    if (!stationInfo) {
      setError('駅情報を先に取得してください。');
      return;
    }
    console.log(`Requesting data for address: ${stationName}`);  // デバッグ情報の出力
    try{
        const { lat, lng } = stationInfo.location; // Extract lat and lng from stationInfo
        const response = await axios.post('http://localhost:8000/places/', {
        language: 'ja',
        station_name: stationInfo.name,
        visit_type: visitType,
        radius: 2000,
        latitude: lat,
        longitude: lng,
        how_to_spend_time: howToSpendTime  // POSTリクエストに時間の使い方を追加
      });
      console.log('Places recommendation response:', response.data); // 追加：おすすめ情報のレスポンスをログに出力
      setMessage(response.data.message);
    } catch (error: any) {
      setError('おすすめ情報の取得に失敗しました。');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-md">最寄り駅入力：
      <form onSubmit={(e) => { e.preventDefault(); fetchRandomStation(); }}>
        <input
          type="text"
          value={stationName}
          onChange={(e) => setStationName(e.target.value)}
          placeholder="最寄り駅を入力してください"
          className="w-full p-3 mb-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
         {/* <button type="submit">送信</button> */}
        <IconButton icon={IconType.Search} to="#" onClick={fetchRandomStation} className="mb-4" />
        </form>
        {stationInfo && <p className="text-sm text-gray-600 mb-2">おすすめの駅：{stationInfo.name}</p>}
        
        <div>
          <label className="text-gray-700">誰と一緒に行きますか？</label>
          <select
            value={visitType}
            onChange={(e) => setVisitType(e.target.value)}
            className="w-full p-3 mt-1 mb-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">選択してください</option>
            <option value="一人">一人</option>
            <option value="子連れ">子連れ</option>
            <option value="カップル">カップル</option>
          </select>
        </div>

        <div>
          <label className="text-gray-700">どんな時間を過ごしますか？</label>
          <select
            value={howToSpendTime}
            onChange={(e) => setHowToSpendTime(e.target.value)}
            className="w-full p-3 mt-1 mb-4 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">選択してください</option>
            <option value="leisurely">のんびりとした</option>
            <option value="active">アクティブな</option>
            <option value="brief">少しの限られた</option>
          </select>
        </div>

        <button onClick={fetchPlacesRecommendation} className="w-full p-3 text-white bg-blue-500 hover:bg-blue-600 rounded-md focus:outline-none">
          おすすめを探す
        </button>

        {message && <div className="mt-4 p-3 bg-green-100 text-green-700 rounded-md">{message}</div>}
        {error && <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">{error}</div>}
      </div>
    </div>
  );
};

export default PlaceForm;

