"use client"

import { useEffect } from 'react';
import type { NextPage } from 'next';
import Script from 'next/script';

const Home: NextPage = () => {
    useEffect(() => {
        console.log('useEffectが実行されました。'); 
        const queryParams = new URLSearchParams(window.location.search);
        const lat = queryParams.get('lat');
        const lng = queryParams.get('lng');

        if (!lat || !lng) {
            console.log('緯度または経度が指定されていません。');
            return; // 緯度または経度がない場合は処理を中止
        }

        window.initMap = function initMap() {
            console.log('initMap 関数が呼ばれました。');
            const mapCenter = new google.maps.LatLng(parseFloat(lat), parseFloat(lng));
            const map = new google.maps.Map(document.getElementById('map') as HTMLElement, {
                center: mapCenter,
                zoom: 16
            });

            // マーカーを追加
            const marker = new google.maps.Marker({
                position: mapCenter,
                map: map,
                title: 'ここです！'
            });

            console.log('マップが初期化されました、マーカーが置かれました。');
        };
    }, []);

    return (
        <div style={{ height: '100vh', width: '100%' }}>
            <div id="map" style={{ height: '100%', width: '100%' }}></div>
            <Script
                id="google-maps"
                src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&callback=initMap`}
                strategy="afterInteractive"
                onError={(e) => console.error('Script failed to load', e)}
            />
        </div>
    );
};

export default Home;

