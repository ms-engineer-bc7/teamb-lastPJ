'use client';
import React from "react";
import StripeBuyButton from "./stripebuybutton";

import Head from 'next/head';

export default function PaymentPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <Head>
        <title>Payment</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <h1 className="text-2xl font-bold">
          Bu.Ra.Ri -さんぽっと- 
        </h1>
        <p className="mt-3 text-base">
          Bu.Ra.Ri-さんぽっと　お支払いページ
        </p>

        <div className="mt-6">
          <StripeBuyButton />
        </div>
      </main>
    </div>
  );
}
