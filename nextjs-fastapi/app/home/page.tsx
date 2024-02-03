"use client"
import Loading from "@/components/loading";
import { auth, onAuthStateChanged, signOut } from "@/utils/firebase";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import useWebSocket from "@/utils/websocket";
import LoadingIcon from "@/components/loadingIcon";
import Header from "@/components/header";

export default function Home() {
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const ws = useWebSocket();

    const [matchLoading, setMatchLoading] = useState(false);
    const [isInitialScreenVisible, setIsInitialScreenVisible] = useState(false);
    const [isMatchPreviewVisible, setIsMatchPreviewVisible] = useState(false);

    const getToken = async () => {
        if (auth.currentUser) {
          return auth.currentUser.getIdToken();
        } else {
          router.push('/auth/sign-in');
          throw new Error('User not signed in');
        }
    };

    useEffect(() => {
        setIsInitialScreenVisible(true);
    }, []);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, () => {
            if (!auth.currentUser) {
              router.push('/sign-in');
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

    const parseMessage = (message: string) => {
        let message_prefix = message.split(":")[0];

        let message_body = message.split(":").length > 1 ? message.split(":")[1] : null;

        switch (message_prefix) {
            case "match_found":
                if (message_body) {
                    // parse message_body into JSON object from string
                    let message = JSON.parse(message_body);

                    let player_info = message["player_info"];
                    let opponent_info = message["oppponent_info"];

                    setIsInitialScreenVisible(false);
                }
                break;
            case "finding_match":
                break;
        }
    }

    const startMatch = async () => {
        setMatchLoading(true);
        await ws!.connect('ws://127.0.0.1:8000/api/ws', parseMessage);
        let token = await getToken();
        console.log(token)
        // let token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY5NjI5NzU5NmJiNWQ4N2NjOTc2Y2E2YmY0Mzc3NGE3YWE5OTMxMjkiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiQXJqdW4gRGl4aXQiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSUZTSU83elBwZWU4TzBfZlVJRnRxaWRjUV8zREJRYzkxN0t3c19pS2kyQ2c9czk2LWMiLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGFydGFuaGFja3MtNWRjNDEiLCJhdWQiOiJ0YXJ0YW5oYWNrcy01ZGM0MSIsImF1dGhfdGltZSI6MTcwNjkzMjA1NSwidXNlcl9pZCI6IlV5U3M1ZlZMQ2NZbmdJZUpuWVJjRXFYbng3RzMiLCJzdWIiOiJVeVNzNWZWTENjWW5nSWVKbllSY0VxWG54N0czIiwiaWF0IjoxNzA2OTQxMzYwLCJleHAiOjE3MDY5NDQ5NjAsImVtYWlsIjoidGVjaG5vYXJqdW5AZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMTM2NDg4Njc5OTM3MTk4ODI3MDEiXSwiZW1haWwiOlsidGVjaG5vYXJqdW5AZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.h1Xj5gzXJXMFJxssljGJF_1hSHrmrFGt1JiYB3o5ASCFjcmTYPrduLpoP1V1aheQ2WG-DNuiNRk5ijn6NxLYa3wUJwkcppmbaJfIWodGcJUXE6Yf2gXy1CnLhctubWmOcS6C0kZ91gYw1NUJXDnoYBUpIfYYLqe6T9yzDepiQHObE8AJfQvKLsKvcLlEKGadavbG0RSEnKUghyCg2-fQGMRcBVy8ZUqQcOlYQ0rDCKLRrrBcycYgRmfStvW-pBMwSq8meOwvFgSCa4t0L63nA_L68sTJi6iMW-h12DteKvjkJlEF4N3oN8mBNhCMBF7wzKcYuC8ERqvl0J6OlOQrjQ";
        if (token) {
            ws!.sendText(token);
        }
        else {
            ws!.disconnect();
        }
        ws!.sendText("add_to_queue");
        // confirmed = match_found: {match_id (UUID)}
        // pending = finding_match
    }

    const slideInDownStyle = {
        animation: 'slideInDown 0.5s forwards'
    };

    const slideOutDownStyle = {
        animation: 'slideOutDown 0.5s forwards'
    };

    return (
        <div className="h-full w-full flex flex-col">
            <Header />
            <div className="w-full grow flex flex-col justify-center items-center"
                style={isInitialScreenVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <span className="text-7xl font-bold text-slate-800">Improv Arena</span>
                <span className="m-10 text-xl font-medium text-slate-600">Improve your improv skills through head-to-head competition!</span>
                <button 
                    className={"mt-12 flex flex-row rounded-full text-xl font-bold px-8 py-6 " + (ws === null || matchLoading ? "bg-cyan-600 text-slate-300" : "bg-cyan-500 hover:bg-cyan-600 text-slate-100")}
                    onClick={async () => {await startMatch()}}
                    disabled={matchLoading || ws === null}
                >
                    {
                        matchLoading ? "Finding a match" : "Start a match"
                    }
                    {
                        matchLoading && 
                        <div className="ml-5">
                            <LoadingIcon borderColor={"border-slate-200"} width={"w-8"}/>
                        </div>
                    }
                </button>
            </div>
            <div className="w-full grow flex flex-col justify-center items-center"
                style={isMatchPreviewVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <span className="text-7xl font-bold text-slate-800">Match Found</span>
                <div>
                    
                </div>
            </div>
        </div>
    )
}