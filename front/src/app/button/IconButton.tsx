import React from 'react';
import { FiUser, FiSearch } from 'react-icons/fi';
import { useRouter } from 'next/navigation';

// アイコンの種類を拡張しやすいようにenum型を使用
enum IconType {
  User = 'user',
  Search = 'search',
}

// Propsの型を定義
interface IconButtonProps {
  icon: 'user' | 'search';
  to: string;
  className?: string;
  onClick?: () => void;  // onClick プロパティをオプショナルで追加
}
// アイコンボタンのコンポーネント
const IconButton: React.FC<IconButtonProps> = ({ icon, to, className }) => {
  const router = useRouter();
  const handleNavigate = () => {
    router.push(to);
  };

  const iconSize = 'w-5 h-5'; // アイコンのサイズを指定するクラス

  // アイコンタイプに基づいて表示するアイコンを選択
  const Icon = () => {
    switch (icon) {
      case IconType.User:
        return <FiUser className={iconSize} />;
      case IconType.Search:
        return <FiSearch className={iconSize} />;
      default:
        return null;
    }
  };

  return (
    <button
      onClick={handleNavigate}
      className={`inline-flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-full hover:bg-blue-700 focus:outline-none focus:ring ${className || ''}`}
    >
      <Icon />
    </button>
  );
};

export default IconButton;
export { IconType }; // 他のコンポーネントでも使用できるようにexportします
