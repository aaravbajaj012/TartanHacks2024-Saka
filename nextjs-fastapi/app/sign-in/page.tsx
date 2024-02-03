"use client"
import Loading from '@/components/loading';
import { signInWithRedirect, auth, GoogleAuthProvider, onAuthStateChanged } from '@/utils/firebase';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Image from 'next/image';

export default function SignIn() {
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, () => {
            if (auth.currentUser) {
              router.push('/home');
            }
            else {
                setLoading(false);
            }
          });
        return () => unsubscribe();
    }, [router]);

    if (loading) {
        return <Loading/>;
    }
    
    return (
        <div className='w-full h-full flex flex-col items-center justify-center'>
            <h1
                className={'text-4xl font-bold text-slate-800 mb-14'}
            >Sign In</h1>

            <button
                onClick={() => {signInWithRedirect(auth, new GoogleAuthProvider())}}
                className={'bg-white font-medium text-slate-800 py-4 px-6 rounded-lg flex-row flex'}
            >
                {/* <Image src='/google-icon.png' alt='G' width="16" height="16" className='mr-4'/> */}
                Sign in with Google
            </button>
        </div>
    );
    }
