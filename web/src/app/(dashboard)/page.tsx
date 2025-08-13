import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to characters page
  redirect('/characters');
}
