import Link from 'next/link';


export default function Home() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Link href="/places">
        <div style={{ padding: '10px 20px', background: 'blue', color: 'white', borderRadius: '5px' }}>Start</div>
      </Link>
    </div>
    );
}
