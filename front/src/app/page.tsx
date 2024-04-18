"use client";
import Image from "next/image";
import Link from "next/link";
import titleLogo from "../../public/titleLogo1.png";
import React from "react";

export default function Home(): JSX.Element {
  return (
    <div>
      <div className="image-container">
        <Image
          src={titleLogo}
          alt="My Image"
          width={640}
          height={360}
          className="rounded-image"
          priority
          unoptimized
        />
      </div>
      <div className="button-container">
        <Link href="/mains">
          <div className="start-button">Start</div>
        </Link>
      </div>
      <style jsx>{`
        .image-container {
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .rounded-image {
          border-radius: 30px;
        }

        .button-container {
          display: flex;
          justify-content: center;
          margin-top: 20px;
        }

        .start-button {
          padding: 10px 20px;
          background-color: #ff9800;
          color: white;
          border-radius: 5px;
          cursor: pointer;
          transition: background-color 0.3s ease;
        }

        .start-button:hover {
          background-color: #f57c00;
        }
      `}</style>
    </div>
  );
}
