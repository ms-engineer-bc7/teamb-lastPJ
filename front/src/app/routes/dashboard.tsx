import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace('/login');
  }, [user, loading, router]);

  if (loading) return <p>Loading...</p>;
  if (!user) return null; // or <p>Redirecting to login...</p>

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user.displayName}!</p>
    </div>
  );
};

export default Dashboard;
