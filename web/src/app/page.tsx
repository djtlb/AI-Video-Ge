import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to characters page as that's our main entry point
  redirect('/characters');
}
