"use client"

import { useEffect, useState } from 'react';
import type { NextPage } from 'next';
import Script from 'next/script';
import axios from 'axios';

interface Station {
    name: string;
    location: {
        lat: number;
        lng: number;
    };
}

const Home: NextPage = () => {
    const [stations, setStations] = useState<Station[]>([]);
    const [loadMap, setLoadMap] = useState(false);

    useEffect(() => {
        const fetchStations = async () => {
            try {
                const res = await axios.get('http://localhost:8000/find-station/?address=練馬駅');
                setStations(res.data.nearby_stations);
                setLoadMap(true);  // ステーションがロードされたらマップをロードするためのフラグを立てる
                console.log('駅データを取得しました:', res.data.nearby_stations);
            } catch (error) {
                console.error('駅データの取得に失敗しました:', error);
            }
        };

        fetchStations();
    }, []);

    useEffect(() => {
        window.initMap = () => {
            if (!stations.length) return;
            const { lat, lng } = stations[0].location;
            console.log('initMap 関数が呼ばれました。');
            const mapCenter = new google.maps.LatLng(lat, lng);
            const map = new google.maps.Map(document.getElementById('map') as HTMLElement, {
                center: mapCenter,
                zoom: 16
            });

            stations.forEach(station => {
                new google.maps.Marker({
                    position: new google.maps.LatLng(station.location.lat, station.location.lng),
                    map: map,
                    title: station.name
                });
            });

            console.log('マップが初期化されました、駅のマーカーが置かれました。');
        };
    }, [stations]);  // stations が更新されたら initMap を再設定

    return (
        <div style={{ height: '100vh', width: '100%' }}>
            <div id="map" style={{ height: '100%', width: '100%' }}></div>
            {loadMap && (
                <Script
                    id="google-maps"
                    src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&callback=initMap`}
                    strategy="afterInteractive"
                    onError={(e) => console.error('Google Maps script failed to load', e)}
                />
            )}
        </div>
    );
};

export default Home;
