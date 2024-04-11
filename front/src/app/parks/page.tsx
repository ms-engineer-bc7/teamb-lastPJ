"use client";
import { useState } from 'react';
import axios from 'axios';

// LLMが返すレスポンスの型定義
type PlaceResponse = {
  message: string;
};

export default function PlacesPage() {
  const [location, setLocation] = useState('35.7356,139.6522');// デフォルトの座標を設定
  const [query, setQuery] = useState(''); //初期値を空の文字列で設定
  const [radius, setRadius] = useState(2000);
  const [placesMessage, setPlacesMessage] = useState<string>("");
  const [age, setAge] = useState<number | undefined>(undefined); // 年齢を数値またはundefinedで管理
  const [station, setStation] = useState(''); // 新しい状態
  const [childAge, setChildAge] = useState<number | undefined>(undefined);  // 子供の年齢もundefinedで管理
  // const [employment, setEmployment] = useState('');
  // const [maritalStatus, setMaritalStatus] = useState('');
  // const [lifestyle, setLifestyle] = useState('');

  // POSTリクエストで場所を取得する関数
  const fetchPlaces = async () => {
    try {
      // リクエストボディの作成
      const requestBody = {
        location,
        query, // これはユーザーの入力から取得した値
        radius,
        language: 'ja',
        age: age || undefined, // 空の場合は undefined を設定 (バックエンドでの処理の改善が必要)
        station, 
        child_age: childAge,
      };

      console.log('Request Body:', requestBody);
      // POSTリクエストの送信
      const response = await axios.post('http://localhost:8000/places/', requestBody);

      // レスポンスの受け取りと状態の更新
      const data: PlaceResponse = response.data;
      setPlacesMessage(response.data.message);
    } catch (error: any) {
      console.error('Error posting data:', error?.response?.data ?? "No error data");
      console.error('Detailed error:', JSON.stringify(error?.response?.data, null, 2));  // JSON形式でエラー詳細を出力
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', paddingTop: '20px' }}>
      <select value={query} onChange={e => setQuery(e.target.value)}>
        <option value="">行きたい場所を選択してください</option>
        <option value="公園">公園</option>
        <option value="美術館">美術館</option>
        <option value="図書館">図書館</option>
      </select>
      <input
        type="text"
        value={age === undefined ? '' : age.toString()}
        onChange={e => {
          const parsedAge = parseInt(e.target.value, 10);
          if (!isNaN(parsedAge)) {
             setAge(parsedAge);
          } else {
             setAge(undefined);
          }
        }}
        placeholder="年代を入力（例: 20）"
      />
      <input
        type="number"
        value={childAge === undefined ? '' : childAge.toString()}
        onChange={e => {
        const parsedAge = parseInt(e.target.value, 10);
        setChildAge(!isNaN(parsedAge) ? parsedAge : undefined);
        }}
        placeholder="子供の年齢を入力"
      />
      <input
        type="text"
        value={station}
        onChange={e => setStation(e.target.value)}
        placeholder="最寄り駅を入力"
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
      {/* <select value={childAge} onChange={(e) => setChildAge(e.target.value)}>
        <option value="">子供の年齢を選択</option>
        <option value="0-5">0-5歳</option>
        <option value="6-12">6-12歳</option>
        <option value="13-18">13-18歳</option>
      </select>
      <select value={employment} onChange={(e) => setEmployment(e.target.value)}>
        <option value="">雇用形態を選択</option>
        <option value="full-time">フルタイム勤務</option>
        <option value="part-time">パートタイム勤務</option>
      </select>
      <select value={maritalStatus} onChange={(e) => setMaritalStatus(e.target.value)}>
        <option value="">結婚状態を選択</option>
        <option value="single">独身</option>
        <option value="married">既婚</option>
      </select>
      <select value={lifestyle} onChange={(e) => setLifestyle(e.target.value)}>
        <option value="">選択してください</option>
        <option value="active">アクティブ</option>
        <option value="homebody">インドア派</option>
      </select> */}
//       <button onClick={fetchPlaces}>場所を取得する</button>
      
//       {/* 取得したデータを表示 */}
//       <ul>
//         {placesMessage.split(', ').map((name, index) => (
//           <li key={index}>{name}</li>
//         ))}
//       </ul>
//     </div>
//   );
// }
