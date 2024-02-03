"use client"
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { onAuthStateChanged, auth } from "@/utils/firebase";
import Loading from "@/components/loading";

export default function Home() {
  const [loading, setLoading] = useState(true);

  const router = useRouter();

  const getToken = async () => {
    if (auth.currentUser) {
      return auth.currentUser.getIdToken();
    } else {
      router.push('/sign-in');
      throw new Error('User not signed in');
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, () => {
        if (auth.currentUser) {
          router.push('/home');
        }
        else {
          router.push('/sign-in');
        }
      });
    return () => unsubscribe();
  }, [router]);


  return (<Loading />);
}
