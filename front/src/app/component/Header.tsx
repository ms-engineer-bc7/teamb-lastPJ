
import React from 'react';
import { FiSearch, FiMapPin, FiUser } from 'react-icons/fi'; // Feather アイコンをインポートします

const Header: React.FC = () => {
  return (
    <div className="bg-yellow-200 p-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        <div className="rounded-full h-12 w-12 flex items-center justify-center bg-pink-200">
          <img src="/negamon.png" className="h-8 w-8" />
        </div>
        <span className="text-2xl font-bold">Bu.Ra.Ri</span>
      </div>
      <div className="flex space-x-6">
        <button>
          <FiSearch className="text-2xl"/> {/* 検索アイコン */}
        </button>
        <button>
          <FiMapPin className="text-2xl"/> {/* ピンアイコン */}
        </button>
        <button>
          <FiUser className="text-2xl"/> {/* ユーザーアイコン */}
        </button>
        
        {/* 他のアイコンやコンポーネント */}
      </div>
    </div>
  );
};

export default Header;
