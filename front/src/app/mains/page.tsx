'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Script from 'next/script';
import Link from "next/link";
import { auth } from "../../../firebase"; // Firebaseの設定ファイルをインポート
import { User, onAuthStateChanged } from 'firebase/auth';

interface StationInfo {
  name: string;
  location: {
      lat: number;
      lng: number;
  };
}
  
    // ユーザーの認証状態と情報を管理するカスタムフック
    const useAuth = () => {
        const [user, setUser] = useState<User | null>(null);
        const [userType, setUserType] = useState(''); // 'free', 'member', or 'premium'

        useEffect(() => {
            const unsubscribe = onAuthStateChanged(auth, async (authUser) => {
                if (authUser) {
                    setUser(authUser); // ユーザー情報をセット
                    const idTokenResult = await authUser.getIdTokenResult();
                    const subscriptionType = idTokenResult.claims.subscriptionType; // カスタムクレームを使用
    
                    if (subscriptionType === 'paid') {
                        setUserType('premium');
                    } else {
                        setUserType('member');
                    }
                } else {
                    setUser(null);
                    setUserType('free');
                }
            });
    
            return () => unsubscribe();
        }, []);
    
        return { user, userType };
    };


  const Home2: React.FC = () => {
  const [stationName, setStationName] = useState<string>('');
  const [visitType, setVisitType] = useState<string>('');
  const [howToSpendTime, setHowToSpendTime] = useState<string>('');
  const [stationInfo, setStationInfo] = useState<StationInfo | null>(null);
  const [recommendations, setRecommendations] = useState<string>('');
  const [error, setError] = useState<string | JSX.Element>('');
  const [loadMap, setLoadMap] = useState<boolean>(false);
  const [recommendationCount, setRecommendationCount] = useState(0);
  const router = useRouter();
  const { user, userType } = useAuth(); // useAuth フックを使用
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  
  useEffect(() => {
    let map: google.maps.Map | undefined;

    const initMap = () => {
      if (stationInfo) {
        const { lat, lng } = stationInfo.location;
        const mapDiv = document.getElementById('map');
        if (mapDiv) {
          mapDiv.innerHTML = ''; // Clear any existing map
          const map = new google.maps.Map(mapDiv, {
            center: { lat, lng },
            zoom: 15,
          });
          new google.maps.Marker({
            position: { lat, lng },
            map,
            title: stationInfo.name,
          });
        } else {
          console.error("Failed to initialize map: map container not found");
        }
      }
    };
  
    const loadGoogleMapsScript = () => {
      const existingScript = document.querySelector(`script[src^="https://maps.googleapis.com/maps/api/js"]`);
      if (!existingScript) {
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places`;
        script.async = true;
        // window.initMap = window.initMap;
        script.onload = initMap;
        document.body.appendChild(script);
      } else {
        initMap();
      }
    };
  
    if (typeof window.google === 'object' && typeof window.google.maps === 'object') {
      initMap(); // If Google Maps is already loaded, just initialize the map
    } else {
      loadGoogleMapsScript(); // Otherwise, load the Google Maps script
    }
  
    return () => {
      // Clean up event listener when component unmounts
      if (map) {
        map.unbindAll();
        map = undefined;
      }
    };
  }, [stationInfo]); // Dependencies array ensures this effect runs only when stationInfo changes
  

  const fetchStation = async () => {
    if (!stationName) {
      setError('駅名を入力してください');
      return;
    }

    setError('');
    try {
      const response = await axios.get(`http://localhost:8000/find-station`, { params: { address: stationName } });
      console.log('ランダムに選択された駅:', response.data); // 追加：ランダムに選ばれた駅のレスポンスをログに出力
      setStationInfo({
        name: response.data.random_station,
        location: {
          lat: response.data.latitude,
          lng: response.data.longitude
        }
      });
      setLoadMap(true); // 追加: 駅情報の取得に成功したら、地図を表示する
    } catch (error) {
      setError('駅情報の取得に失敗しました');
      setStationInfo(null);
    }
  };
  // console.log('Random station response:', setStationInfo); // 追加：ランダムに選ばれた駅のレスポンスをログに出力

  const handleRecommendationsClick = async () => {
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
        how_to_spend_time: howToSpendTime
      });
      console.log('提案レスポンス:',response.data);
      const message = response.data.message;
      console.log('提案レスポンスメッセージ:',message);

    if (userType === 'free') {
        // ③freeユーザーの場合、レスポンスを100文字までに制限
        if (message.length > 100) {
          setRecommendations(message.substring(0, 100) + '...');
          setError(
            <span>
            おすすめプランを全て見るには{' '}
            <Link href="/logins" className="text-blue-500 hover:underline">
              無料メンバー登録
            </Link>
            ・
            <Link href="/stripes" className="text-blue-500 hover:underline">
              有料プランにアップグレード
            </Link>{' '}
            してください。
          </span>
          );
        } else {
          setRecommendations(message);
        }
      } else if (userType === 'member') {
        // ④memberユーザーの場合、3回までレスポンスを使用可能
        if (recommendationCount >= 3) {
          setError(
          <span>
              3回目以降は{' '}
            <Link href="/stripes" className="text-blue-500 hover:underline">
              有料プランにアップグレード
            </Link>{' '}
              してください
          </span>
          );
          setRecommendations('');
        } else {
          setRecommendations(message);
           // この関数が呼び出されるたびにおすすめ回数をインクリメント
          // 注：このロジックは有効なおすすめ情報が取得された後に配置でも可
          setRecommendationCount(prev => prev + 1);
        }
      } else if (userType === 'premium') {
        // premiumユーザーの場合、制限なし
        setRecommendations(message);
      }
    } catch (error) {
      console.error('Recommendation fetch failed:', error);
      setError('おすすめ情報の取得に失敗しました');
    }
  };


  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="ml-4">
          {userType === 'premium' && (
            <div className="text-pink-500">
              有料メンバーは、このアプリを制限なく利用できます
            </div>
          )}
          {userType === 'member' && (
            <div className="text-pink-500">
              ログインメンバーは、３回までこのアプリの全ての機能がお試し頂けます
            </div>
          )}
          {userType === 'free' && (
            <div className="text-pink-500">
              無料ユーザーは、<Link href="/logins">ログイン</Link>していない場合に制限があります
            </div>
          )}
        </div>
      <div className="mb-4">
        <input
          type="text"
          value={stationName}
          onChange={e => setStationName(e.target.value)}
          placeholder="最寄り駅か住所を入力してください"
          className="input bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal"
        />
        <button
          className="bg-orange-400 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mt-4"
          onClick={fetchStation}
        >
          おすすめの駅を探す
        </button>
        
      </div>
      <div className="flex -mx-2">
        {stationInfo && (
          <div className="flex-1 px-2">
            <div className="mb-4 p-4 border rounded-lg shadow-lg bg-white">
              <div className="flex items-center text-xl font-semibold mb-2">
                <svg className="w-6 h-6 text-pink-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
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
                <option value="一人で">一人で</option>
                <option value="子連れで">子どもと</option>
                <option value="カップルで">カップルで</option>
                <option value="家族と">家族と</option>
                <option value="友達と">友達と</option>
              </select>
              <label className="block">どんな時間を過ごしたいですか？</label>
              <select
                className="block appearance-none w-full bg-white border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline mb-4"
                value={howToSpendTime}
                onChange={e => setHowToSpendTime(e.target.value)}
              >
                <option value="">選択してください</option>
                <option value="のんびりとした">のんびり</option>
                <option value="アクティブに">アクティブ</option>
                <option value="少しの限られた">サクッと</option>
              </select>
              <button
                className="bg-orange-400 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                onClick={handleRecommendationsClick}
              >
                おすすめプランを提案
              </button>
            </div>
          </div>
        )}
        {loadMap && (
          <div className="flex-1 px-2">
            <div id="map" className="w-full h-96 border-2 border-gray-300 mt-1 rounded-lg shadow-lg"></div>
          </div>
        )}
      </div>
      {recommendations && (
        <div className="mt-4 p-4 border-2 border-gray-300 rounded-lg shadow-lg bg-light-blue-50">
          <p className="font-semibold">今回のおすすめプランです：</p>
          <p>{recommendations}</p>
        </div>
      )}
      <div>
      </div>
      <div className="error-message mt-4 p-4 bg-ight-blue-5 rounded-lg ">
      {error && <p className="text-red-500 mt-4">気に入りましたか？: {error}</p>}
      </div>
    </div>
  );
};

export default Home2;

