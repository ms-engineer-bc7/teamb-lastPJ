"use client";
import Image from "next/image";
import Link from "next/link";
import titleLogo from "../../public/titleLogo1.png";
import React from "react";

export default function Home(): JSX.Element {
  return (
      <div className="min-h-screen flex flex-col items-center">
       <div className="mt-20">
        <Image
          src={titleLogo}
          alt="My Image"
          width={640}
          height={360}
          className="rounded-[30px]"
          priority
          unoptimized
        />
       </div>
       <div className="mt-12">
        <Link href="/mains">
        <div className="px-10 py-4 bg-orange-500 text-white text-2xl font-bold rounded-lg cursor-pointer transition duration-300 
        ease-in-out hover:bg-orange-600">お出掛けしてみる？</div>
        </Link>
       </div>
       <div className="text-center mt-6">
         <div className="border-2 border-dotted border-gray-400 p-4 rounded">
          <p>休日のちょっとした外出先に困っていませんか？  一人でゆっくりしたい、お子さんと出かけたい、恋人とアクティブに活動したい等</p>
          <p>Bu.Ra.Ri-さんぽっと-は、あなたの家の近くの駅をランダムに選び、あなたが選んだ条件から休日のお出掛けの提案をしてくれるアプリです</p>
         </div>
       </div>
      </div>
  );
}
