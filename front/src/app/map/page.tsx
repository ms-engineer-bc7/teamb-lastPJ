"use client"

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Script from 'next/script'; // Next.js の Script コンポーネントをインポート

interface StationInfo {
  name: string;
  location: {
      lat: number;
      lng: number;
  };
}

const Home: React.FC = () => {
  const [stationName, setStationName] = useState<string>('');
  const [visitType, setVisitType] = useState<string>('');
  const [howToSpendTime, setHowToSpendTime] = useState<string>('');
  const [stationInfo, setStationInfo] = useState<StationInfo | null>(null);
  const [recommendations, setRecommendations] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loadMap, setLoadMap] = useState<boolean>(false);

  useEffect(() => {
    window.initMap = function initMap() {
      if (stationInfo) {
        const { lat, lng } = stationInfo.location;
        const map = new google.maps.Map(document.getElementById('map'), {
          center: { lat, lng },
          zoom: 15,
        });
        new google.maps.Marker({
          position: { lat, lng },
          map,
          title: stationInfo.name,
        });
      }
    };
  }, [stationInfo]);

  const fetchStation = async () => {
    if (!stationName) {
      setError('駅名を入力してください');
      return;
    }
    console.log(`Requesting data for address: ${stationName}`);  // デバッグ情報の出力
    setError('');
    // console.log(`Requesting data for address: ${stationName}`);  // デバッグ情報の出力
    try {
      const response = await axios.get(`http://localhost:8000/find-station`, { params: { address: stationName } });
      console.log('Random station response:', response.data); // 追加：ランダムに選ばれた駅のレスポンスをログに出力
      setStationInfo({
        name: response.data.random_station,
        location: {
          lat: response.data.latitude,
          lng: response.data.longitude
        }
      });
    } catch (error) {
      console.error('Failed to fetch station data:', error);
      setError('駅情報の取得に失敗しました');
      setStationInfo(null);
    }
  };

  const fetchRecommendations = async () => {
    if (!stationInfo) {
      setError('先に駅を選択してください');
      return;
    }
    console.log(`Requesting data for address: ${stationName}`);  // デバッグ情報の出力
    try {
      const { lat, lng } = stationInfo.location;
      const response = await axios.post('http://localhost:8000/places/', {
        language: 'ja',
        station_name: stationInfo.name,
        visit_type: visitType,
        radius: 2000,
        latitude: lat,
        longitude: lng,
        how_to_spend_time: howToSpendTime // POSTリクエストに時間の使い方を追加s
      });
      console.log('Places recommendation response:',response.data); 
      setRecommendations(response.data.message);
      setLoadMap(true);  // Trigger the map to load with new marker
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      setError('おすすめ情報の取得に失敗しました');
    }
  };

  return  (
    // <div className="max-w-4xl mx-auto p-4 bg-cream"> {/* クリーム色の背景を適用 */}
     <div className="max-w-4xl mx-auto p-4">
        <div className="mb-4">
        <input
          type="text"
          value={stationName}
          onChange={e => setStationName(e.target.value)}
          placeholder="最寄り駅か住所を入力してください"
          className="input bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal"
        />
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mt-4"
          onClick={fetchStation}
        >
          おすすめの駅を探す
        </button>
        </div>
      <div className="flex -mx-2">
        <div className="flex-1 px-2">
          {stationInfo && (
            <>
             <div className="mb-4 p-4 border rounded-lg shadow-lg bg-white"> {/* 白背景を適用 */}
            <div className="flex items-center text-xl font-semibold mb-2">
              <svg className="w-6 h-6 text-pink-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"> {/* アイコン */}
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>  
              {/* <div className="mb-4"> */}
                <p className="text-xl font-semibold mb-2">あなたにおすすめしたい駅はこちら</p>
                </div>
                <p className="text-lg font-bold mb-4">{stationInfo.name}</p>
                <label className="block">誰と一緒に行きますか？</label>
                <select
                  className="block appearance-none w-full bg-white border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline mb-4"
                  value={visitType}
                  onChange={e => setVisitType(e.target.value)}
                >
                  <option value="">選択してください</option>
                  <option value="alone">一人</option>
                  <option value="family">子供と一緒</option>
                  <option value="friends">カップル</option>
                </select>
                <label className="block">どんな時間を過ごしたいですか？</label>
                <select
                  className="block appearance-none w-full bg-white border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline mb-4"
                  value={howToSpendTime}
                  onChange={e => setHowToSpendTime(e.target.value)}
                >
                <option value="">選択してください</option>
                <option value="leisurely">のんびりとしたい</option>
                <option value="active">アクティブに</option>
                <option value="brief">少し限られた</option>
                </select>
                <button
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  onClick={fetchRecommendations}
                >
                  おすすめプランを提案
                </button>
              </div>
            </>
          )}
        </div>
        {loadMap && (
          <div className="flex-1 px-2">
            <Script
              src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&callback=initMap`}
              strategy="afterInteractive"
            />
            <div id="map" className="w-full h-96 border-2 border-gray-300 mt-4 rounded-lg shadow-lg"></div>
          </div>
        )}
      </div>
      {recommendations && (
        <div className="mt-4 p-4 border-2 border-gray-300 rounded-lg shadow-lg bg-light-blue-50">
          <p className="font-semibold">今回のおすすめプランです：</p>
          <p>{recommendations}</p>
        </div>
      )}
      {error && <p className="text-red-500 mt-4">エラー: {error}</p>}
      </div>
    // </div>
  );
};

  export default Home;  


