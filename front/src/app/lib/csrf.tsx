// export function getCSRFToken(): string | null {
//     if (typeof document !== 'undefined') {
//       const cookies = document.cookie.split('; ');
//       const csrfTokenCookie = cookies.find((cookie) => cookie.startsWith('csrf_token='));
//       if (csrfTokenCookie) {
//         return csrfTokenCookie.split('=')[1];
//       }
//     }
//     return null;
//   }
  
//   export async function fetchCSRFToken(): Promise<string | null> {
//     try {
//       const response = await fetch('http://localhost:8000/csrf-token', {
//         method: 'GET',
//       });
//       if (!response.ok) {
//         throw new Error('Failed to fetch CSRF token');
//       }
//       const data = await response.json();
//       return data.csrf_token;
//     } catch (error) {
//       console.error('Failed to fetch CSRF token:', error);
//       return null;
//     }
//   }