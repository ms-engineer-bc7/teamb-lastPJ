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
    setError('');
    try {
      const response = await axios.get(`http://localhost:8000/find-station`, { params: { address: stationName } });
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
    try {
      const { lat, lng } = stationInfo.location;
      const response = await axios.post('http://localhost:8000/places/', {
        station_name: stationInfo.name,
        visit_type: visitType,
        latitude: lat,
        longitude: lng,
        how_to_spend_time: howToSpendTime
      });
      console.log(response.data); 
      setRecommendations(response.data.message);
      setLoadMap(true);  // Trigger the map to load with new marker
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      setError('おすすめ情報の取得に失敗しました');
    }
  };

  return (
    <div>
      <input
        type="text"
        value={stationName}
        onChange={e => setStationName(e.target.value)}
        placeholder="最寄り駅を入力してください"
      />
      <button onClick={fetchStation}>送信</button>
      <div>
        {stationInfo && (
          <>
            <p>あなたにおすすめの駅: {stationInfo.name}</p>
            <div>
            誰と一緒に行きますか？
            <select value={visitType} onChange={e => setVisitType(e.target.value)}>
              <option value="">Who…?</option>
              <option value="alone">一人</option>
              <option value="family">子連れ</option>
              <option value="friends">カップル</option>
            </select>
            どんな時間を過ごしますか？
            <select value={howToSpendTime} onChange={e => setHowToSpendTime(e.target.value)}>
              <option value="">How…?</option>
              <option value="relax">のんびりとした</option>
              <option value="explore">アクティブな</option>
              <option value="shop">少しの限られた</option>
            </select>
            <button onClick={fetchRecommendations}>recommend</button>
            </div>
          </>
        )}
        {loadMap && (
          <Script
            src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&callback=initMap`}
            strategy="afterInteractive"
          />
        )}
        <div id="map" style={{ height: '500px', width: '100%' }}></div>
        {recommendations && <p>おすすめ: {recommendations}</p>}
        {error && <p>エラー: {error}</p>}
      </div>
    </div>
  );
};

export default Home;
