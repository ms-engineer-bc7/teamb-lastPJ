"use client"

import React, { useState, FormEvent } from 'react';
import axios from 'axios';


const Pages: React.FC = () => {
  const [station, setStation] = useState<string>('');

  const handleSubmit = async(event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();  // デフォルトのフォーム送信を防ぐ

    const payload = {
      station: station
    };
    try {
      // `axios.post` を使用して POST リクエストを送信
      const response = await axios.post('http://localhost:8000/nearest-station', payload);
      console.log('Success:', response.data);  // response.data にはサーバーからの応答が含まれています
      // 送信に成功した場合の処理
      setStation('');
    } catch (error) {
      if (error.response) {
        console.error('API Error:',error.response.data);
      } else if (error.request){
        console.error('No response:', error.request);
      }else {
        // エラー設定時の問題
        console.error('Error setting up request:', error.message);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        最寄り駅:
        <input
          type="text"
          value={station}
          onChange={e => setStation(e.target.value)}
          placeholder="駅名を入力してください"
        />
      </label>
      <button type="submit">送信</button>
    </form>
  );
};

export default Pages;

