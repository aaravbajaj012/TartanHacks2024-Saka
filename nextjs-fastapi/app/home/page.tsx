"use client"
import Loading from "@/components/loading";
import { auth, onAuthStateChanged, signOut } from "@/utils/firebase";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import useWebSocket from "@/utils/websocket";
import LoadingIcon from "@/components/loadingIcon";
import Header from "@/components/header";
// const ReactRotatingText =  require('react-rotating-text');
import { RotatingText } from 'react-simple-rotating-text';

export default function Home() {
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const ws = useWebSocket();

    const [matchLoading, setMatchLoading] = useState(false);
    const [isInitialScreenVisible, setIsInitialScreenVisible] = useState(false);
    const [isMatchPreviewVisible, setIsMatchPreviewVisible] = useState(false);
    const [isDirectionsVisible, setIsDirectionsVisible] = useState(false);
    const [isMatchScreenVisible, setIsMatchScreenVisible] = useState(false);

    const [playerInfo, setPlayerInfo] = useState(null);
    const [opponentInfo, setOpponentInfo] = useState(null);

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
        const splitFirstColon = (s: string) => {
            let i = s.indexOf(':');
            return i === -1 ? [s] : [s.slice(0, i), s.slice(i + 1)];
        }

        let message_split = splitFirstColon(message);

        let message_prefix = message_split[0];

        let message_body = message_split.length > 1 ? message_split[1] : null;

        switch (message_prefix) {
            case "match_found":
                if (message_body) {
                    // parse message_body into JSON object from string
                    let message = JSON.parse(message_body);

                    setPlayerInfo(message["player_info"]);
                    setOpponentInfo(message["oppponent_info"]);

                    setIsInitialScreenVisible(false);
                    setIsMatchPreviewVisible(true);

                    // setTimeout(() => {
                    //     setIsMatchPreviewVisible(false);
                    //     setIsDirectionsVisible(true);
                    // }, 2000);
                }
                break;
            case "start_match":
                setIsDirectionsVisible(false);
                setIsMatchScreenVisible(true);
                break;
            case "finding_match":
                break;
            case "match_prepared":
                setIsMatchPreviewVisible(false);
                setIsDirectionsVisible(true);
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
        // ws!.sendText("add_to_queue");
        parseMessage("match_found:{\"player_info\": {\"name\": \"Arjun Dixit\", \"profile_pic\": \"\", \"elo\": \"1190\"}, \"oppponent_info\": {\"name\": \"John Doe\", \"profile_pic\": \"\", \"elo\": \"1210\"}}");
        // confirmed = match_found: {match_id (UUID)}
        // pending = finding_match
    }

    const readyPlayer = () => {
        ws!.sendText("player_ready");
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
            <div className={"w-full grow flex flex-col justify-center items-center "  + (isInitialScreenVisible ? "visible" : "hidden")}
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
                            <LoadingIcon width={"w-8"}/>
                        </div>
                    }
                </button>
            </div>
            <div className={"w-full grow flex flex-col justify-center items-center " + (isMatchPreviewVisible ? "visible" : "hidden")}
                style={isMatchPreviewVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <span className="text-5xl font-bold text-slate-800">Match Found</span>
                <div className="mt-24 flex flex-row justify-center items-center">
                    <div className="bg-white shadow-card px-10 py-8 rounded-lg">
                        <div className="flex flex-col items-center">
                            <img src={(playerInfo && playerInfo['profile_pic'] ? playerInfo['profile_pic'] : null) ?? "/pfp-default.png"} className="w-32 h-32 rounded-full" alt="Player Profile Pic"/> 
                            <span className="mt-4 text-xl font-bold text-slate-800">{playerInfo ? playerInfo['name'] : "Player"}</span>
                            <span className="mt-2 text-lg font-medium text-slate-600">{playerInfo ? playerInfo['elo'] : "1200"}</span>
                        </div>
                    </div>

                    <img src="/swords.png" className="mx-10 w-[128px]" alt="VS Icon"/>

                    <div className="bg-white shadow-card px-10 py-8 rounded-lg">
                        <div className="flex flex-col items-center">
                            <img src={(opponentInfo && opponentInfo['profile_pic'] ? opponentInfo['profile_pic'] : null) ?? "/pfp-default.png"} className="w-32 h-32 rounded-full" alt="Player Profile Pic"/> 
                            <span className="mt-4 text-xl font-bold text-slate-800">{opponentInfo ? opponentInfo['name'] : "Player"}</span>
                            <span className="mt-2 text-lg font-medium text-slate-600">{opponentInfo ? opponentInfo['elo'] : "1200"}</span>
                        </div>
                    </div>
                </div>

                <div className="mt-12 flex flex-col justify-center items-center text-slate-500">
                    <LoadingIcon width={"w-10"}/>
                    <div style={{marginLeft: "-170px", marginTop: "10px"}}>
                        <RotatingText className="text-lg font-bold text-slate-500 mt-4" texts={['Brainstorming ideas...', 'Generating scenario...', 'Setting up the stage...']}/>
                    </div>
                </div>
            </div>

            <div className={"w-full grow flex flex-col justify-center items-center " + (isDirectionsVisible ? "visible" : "hidden")}
                style={isDirectionsVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <span className="text-lg font-medium w-5/12 text-center text-slate-700">
                    You will be given a scenario to improvise. You will have 30 seconds to prepare and 1 minute to speak. Let us know when you're ready!
                </span>

                <button className="mt-12 flex flex-row rounded-full text-md font-semibold px-6 py-4 bg-cyan-500 hover:bg-cyan-600 text-slate-100"
                    onClick={() => {
                        readyPlayer();
                    }}
                >
                    I'm Ready
                </button>
            </div>
        </div>
    )
}