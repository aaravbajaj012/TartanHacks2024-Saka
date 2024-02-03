"use client"
import Loading from "@/components/loading";
import { auth, onAuthStateChanged, signOut } from "@/utils/firebase";
import { useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import useWebSocket from "@/utils/websocket";
import LoadingIcon from "@/components/loadingIcon";
import Header from "@/components/header";
// const ReactRotatingText =  require('react-rotating-text');
import { RotatingText } from 'react-simple-rotating-text';
import TimerIcon from "@/components/timerIcon";
import { useReactMediaRecorder, ReactMediaRecorder } from "react-media-recorder";
import RecordingIcon from "@/components/recordingIcon";
import VideoPreview from "@/components/videoPreview";
import Timer from "@/components/timer";
import { BadgeDelta, ProgressBar } from "@tremor/react";

const PREP_TIMER_DURATION = 30;
const RECORDING_TIMER_DURATION = 45;

export default function Home() {
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const ws = useWebSocket();

    const [matchLoading, setMatchLoading] = useState(false);
    const [isInitialScreenVisible, setIsInitialScreenVisible] = useState(false);
    const [isMatchPreviewVisible, setIsMatchPreviewVisible] = useState(false);
    const [isDirectionsVisible, setIsDirectionsVisible] = useState(false);
    const [isMatchScreenVisible, setIsMatchScreenVisible] = useState(false);
    const [isPostMatchLoadingVisible, setIsPostMatchLoadingVisible] = useState(false);
    const [isMatchResultsVisible, setIsMatchResultsVisible] = useState(false);
    
    const [match_id, setMatchId] = useState(null);
    const [playerInfo, setPlayerInfo] = useState<any>(null);
    const [opponentInfo, setOpponentInfo] = useState<any>(null);

    const [timer, setTimer] = useState(30);

    const [prompt, setPrompt] = useState("");

    const { mediaBlobUrl, status, startRecording, stopRecording, previewStream } = useReactMediaRecorder({ audio: true, video: true });
    const [isRecording, setIsRecording] = useState(false);
    const [isAboutToRecord, setIsAboutToRecord] = useState(false);

    const [results, setResults] = useState<any>(null);

    const [isPlayerReady, setIsPlayerReady] = useState(false);

    const getToken = async () => {
        if (auth.currentUser) {
          return auth.currentUser.getIdToken();
        } else {
          router.push('/sign-in');
          throw new Error('User not signed in');
        }
    };

    const uploadFile = async (mediaBlobUrl: string) => {
        let blob = await (await fetch(mediaBlobUrl)).blob();
            
        const formData = new FormData();

        let user_id = auth.currentUser!.uid;

    
        formData.append("file", blob, `${match_id}_${user_id}.mp4`);

        let res = await fetch('/api/upload-replay', {
            method: 'POST',
            body: formData,
            headers: {
                // 'Content-Type': 'multipart/form-data',
                'Authorization': `Bearer ${await getToken()}`
            }
        });

        return res.ok;
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

                    console.log(message);
                    setPlayerInfo(JSON.parse(message["player"]));
                    setOpponentInfo(JSON.parse(message["opponent"]));
                    setMatchId(message["match_id"]);

                    setIsInitialScreenVisible(false);
                    setIsMatchPreviewVisible(true);
                    setMatchLoading(false);
                }
                else {
                    console.error("No match info provided");
                }
                break;
            case "prompt":
                if (message_body) {
                    setPrompt(message_body);
                }
                else {
                    console.error("No prompt provided");
                }

                setIsDirectionsVisible(false);
                setIsMatchScreenVisible(true);
                
                setTimer(PREP_TIMER_DURATION);
                let prepInterval = setInterval(() => {
                    setTimer((timer) => {
                        if (timer == 0) {
                            clearInterval(prepInterval);
                            setIsRecording(true);

                            return 0;
                        }

                        if (timer == 1) {
                            setIsAboutToRecord(true);
                            startRecording();
                        }
                        
                        return timer - 1;
                    });
                }, 1000);
                break;
            case "finding_match":
                // TODO: Show that a match is being found
                break;
            case "match_ready":
                setIsMatchPreviewVisible(false);
                setIsDirectionsVisible(true);
                break;
            case "match_failed":
                // TODO: Show error message and take user back to the main parseMessage
                break;
            case "error_creating_match":
                // TODO: Show error message and take user back to the main parseMessage
                break;
            case "match_completed":
                if (message_body) {
                    let message = JSON.parse(message_body);

                    setResults(message);

                    // message["winner"] = message["winner"] === "true";
                    // message["player_feedback"] = JSON.parse(message["player_feedback"]);
                    // message["opponent_feedback"] = JSON.parse(message["opponent_feedback"]);

                    // TODO: reset all the states
                    setIsPostMatchLoadingVisible(false);
                    setIsMatchResultsVisible(true);
                    setIsPlayerReady(false);
                    
                    // populate page with match results
                }
                else {
                    console.error("No match results provided");
                }
        }
    }

    useEffect(() => {
        if (mediaBlobUrl) {
            uploadFile(mediaBlobUrl);
        }
    }, [mediaBlobUrl]);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, () => {
            if (auth.currentUser) {
                auth.currentUser.getIdToken().then(token => {
                    if (token) {
                        fetch('/api/register', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                                },
                            body: JSON.stringify({
                                "user_id": auth.currentUser!.uid,
                                "name": auth.currentUser!.displayName,
                                "profile_pic": auth.currentUser!.photoURL
                                })
                            }
                        ).then(res => {
                            console.log("successfully registered user")
                        }).catch(err => {
                            console.log("failed to register user")
                            console.log(err)
                        });
                    }
                });
            }      
            else {
              router.push('/sign-in');
            }
          });
        return () => unsubscribe();
      }, [router]);

    useEffect(() => {
        setIsInitialScreenVisible(true);
        return () => {
            if (ws) {
                ws.disconnect();
            }
        }
    }, []);

    const populateFakeData = () => {
        setPlayerInfo({
            "name": "Player 1",
            "elo": 1210,
            "profile_pic": "/pfp-default.png"
        });

        setOpponentInfo({
            "name": "Player 2",
            "elo": 1190,
            "profile_pic": "/pfp-default.png"
        });
        parseMessage("match_completed:" + JSON.stringify({
            "player_feedback": {
                "score": 15
            },
            "opponent_feedback": {
                "score": 15
            },
            "player_rating": 1220,
            "opponent_rating": 1180,
            "player_rating_delta": 10,
            "opponent_rating_delta": -10,
            "winner": false
        }));
    }

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

    const startMatch = async () => {
        setMatchLoading(true);
        await ws!.connect('ws://127.0.0.1:8000/api/ws', parseMessage);
        let token = await getToken();
        // let token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY5NjI5NzU5NmJiNWQ4N2NjOTc2Y2E2YmY0Mzc3NGE3YWE5OTMxMjkiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiQXJqdW4gRGl4aXQiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSUZTSU83elBwZWU4TzBfZlVJRnRxaWRjUV8zREJRYzkxN0t3c19pS2kyQ2c9czk2LWMiLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGFydGFuaGFja3MtNWRjNDEiLCJhdWQiOiJ0YXJ0YW5oYWNrcy01ZGM0MSIsImF1dGhfdGltZSI6MTcwNjkzMjA1NSwidXNlcl9pZCI6IlV5U3M1ZlZMQ2NZbmdJZUpuWVJjRXFYbng3RzMiLCJzdWIiOiJVeVNzNWZWTENjWW5nSWVKbllSY0VxWG54N0czIiwiaWF0IjoxNzA2OTQxMzYwLCJleHAiOjE3MDY5NDQ5NjAsImVtYWlsIjoidGVjaG5vYXJqdW5AZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMTM2NDg4Njc5OTM3MTk4ODI3MDEiXSwiZW1haWwiOlsidGVjaG5vYXJqdW5AZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.h1Xj5gzXJXMFJxssljGJF_1hSHrmrFGt1JiYB3o5ASCFjcmTYPrduLpoP1V1aheQ2WG-DNuiNRk5ijn6NxLYa3wUJwkcppmbaJfIWodGcJUXE6Yf2gXy1CnLhctubWmOcS6C0kZ91gYw1NUJXDnoYBUpIfYYLqe6T9yzDepiQHObE8AJfQvKLsKvcLlEKGadavbG0RSEnKUghyCg2-fQGMRcBVy8ZUqQcOlYQ0rDCKLRrrBcycYgRmfStvW-pBMwSq8meOwvFgSCa4t0L63nA_L68sTJi6iMW-h12DteKvjkJlEF4N3oN8mBNhCMBF7wzKcYuC8ERqvl0J6OlOQrjQ";
        if (token) {
            ws!.sendText(token);
        }
        else {
            ws!.disconnect();
        }
        ws!.sendText("add_to_queue");
    }

    const readyPlayer = () => {
        if (match_id) {
            setIsPlayerReady(true);
            ws!.sendText(`player_ready:${match_id}`);
        }
        else {
            console.error("Match ID is empty");
        }
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
                            <img src={(playerInfo && playerInfo['profile_pic'] ? playerInfo['profile_pic'] : null) ?? "/pfp-default.png"} className="w-32 h-32 rounded-full"/> 
                            <span className="mt-4 text-xl font-bold text-slate-800">{playerInfo ? playerInfo['name'] : "Player"}</span>
                            <span className="mt-2 text-lg font-medium text-slate-600">{playerInfo ? playerInfo['elo'] : ""}</span>
                        </div>
                    </div>

                    <img src="/swords.png" className="mx-10 w-[128px]" alt="VS Icon"/>

                    <div className="bg-white shadow-card px-10 py-8 rounded-lg">
                        <div className="flex flex-col items-center">
                            <img src={(opponentInfo && opponentInfo['profile_pic'] ? opponentInfo['profile_pic'] : null) ?? "/pfp-default.png"} className="w-32 h-32 rounded-full"/> 
                            <span className="mt-4 text-xl font-bold text-slate-800">{opponentInfo ? opponentInfo['name'] : "Player"}</span>
                            <span className="mt-2 text-lg font-medium text-slate-600">{opponentInfo ? opponentInfo['elo'] : ""}</span>
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

                <button className={"mt-12 flex flex-row rounded-full text-md font-semibold px-6 py-4 text-slate-100 " + (isPlayerReady ? "bg-cyan-500 hover:bg-cyan-600" : "bg-cyan-600")}
                    onClick={() => {
                            readyPlayer();
                        }
                    }
                    disabled={isPlayerReady}
                >
                    {
                        isPlayerReady ?
                        "Waiting for opponent" :
                        "I'm Ready"
                    }
                    {   
                        isPlayerReady &&
                        <div className="ml-4 text-slate-300">
                            <LoadingIcon width={"w-6"}/>
                        </div>
                    }
                </button>
            </div>

            <div className={"w-full grow flex flex-col justify-center items-center " + (isMatchScreenVisible ? "visible" : "hidden")}
                style={isMatchScreenVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <section className="flex flex-col items-center justify-center w-7/12 p-4 space-y-4 bg-white dark:bg-gray-900 rounded-lg shadow-lg">
                    <div className="flex items-center justify-between w-full">
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Scenario</h1>
                        <div className="flex items-center space-x-2">
                        {
                            isRecording && 
                            <div className="mr-5">
                                <RecordingIcon />
                            </div>
                        }
                        <TimerIcon className="w-6 h-6 text-gray-500 dark:text-gray-400" />
                        { isRecording ?
                            <Timer onTimerFinished={() => {
                                stopRecording();
                                setIsAboutToRecord(false);
                                        
                                setTimeout(() => {
                                    setIsRecording(false);
                                    setIsMatchScreenVisible(false);
                                    setIsPostMatchLoadingVisible(true);
                                    setTimeout(() => {
                                        populateFakeData();
                                    }, 3000);
                                }, 1000);
                            }} totalTime={RECORDING_TIMER_DURATION} />
                            :
                            <span className="text-lg font-medium text-gray-500 dark:text-gray-400">{`${timer}s`}</span>
                        }

                        </div>
                    </div>
                    <div className="w-full p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                        <p className="text-lg text-center text-gray-700 dark:text-gray-300">{prompt}</p>
                    </div>
                    <div className="w-[400px] h-[300px] bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                        { isAboutToRecord &&
                            <VideoPreview isHidden={!isRecording} stream={previewStream} />
                        }
                        {   !isRecording &&
                            <span className="text-lg text-gray-500 dark:text-gray-400">{`The recording will start in ${timer} seconds.`}</span>
                        }
                    </div>
                </section>
            </div>
            
            <div className={"w-full grow flex flex-col justify-center items-center text-slate-700 " + (isPostMatchLoadingVisible ? "visible" : "hidden")}
                style={isPostMatchLoadingVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <LoadingIcon width={"w-20"}/>
            </div>
            { isMatchResultsVisible &&
            <div className={"w-full grow flex flex-col justify-center items-center " + (isMatchResultsVisible? "visible" : "hidden")}
                style={isMatchResultsVisible ? slideInDownStyle : slideOutDownStyle}
            >
                <span className="text-5xl font-bold text-slate-800">Match Results</span>

                <div className="mt-12 flex flex-row justify-center items-center w-full">
                    <div className="w-1/4 flex flex-col justify-center items-center mr-40">
                        <div className="bg-white shadow-card px-10 py-8 rounded-lg flex flex-col w-full">
                            <div className="w-full flex flex-row justify-center items-center">
                                <img src={(playerInfo && playerInfo['profile_pic'] ? playerInfo['profile_pic'] : null) ?? "/pfp-default.png"} className="w-20 h-20 rounded-full mr-6"/> 
                                <div className="flex flex-col justify-center items-left">
                                    <span className="text-2xl font-bold text-slate-800">{playerInfo ? playerInfo['name'] : "Player"}</span>
                                    <div className="flex flex-row justify-center items-center">
                                        <span className="mt-2 mr-4 text-lg font-medium text-slate-600">{results ? results['player_rating'] : ""}</span>
                                        <BadgeDelta deltaType={results['player_rating_delta'] > 0 ? "increase" : "decrease"}>{Math.abs(parseInt(results['player_rating_delta'], 10))}</BadgeDelta>
                                    </div>
                                </div>
                            </div>
                            <div className="w-full mt-4 flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Overall Score</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">73</span>
                                </div>
                                <ProgressBar value={73} color="blue" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Eye Contact</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">87</span>
                                </div>
                                <ProgressBar value={87} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Facial Emotions</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">80</span>
                                </div>
                                <ProgressBar value={80} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Tone</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">91</span>
                                </div>
                                <ProgressBar value={91} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Volume</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">38</span>
                                </div>
                                <ProgressBar value={38} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-gl font-semibold text-slate-600">Filler Words</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">67</span>
                                </div>
                                <ProgressBar value={67} color="teal" className="mt-3" />
                            </div>
                        </div>
                    </div>
                    <div className="w-1/4 flex flex-col justify-center items-center">
                        <div className="bg-white shadow-card px-10 py-8 rounded-lg flex flex-col w-full">
                            <div className="w-full flex flex-row justify-center items-center">
                                <img src={(opponentInfo && opponentInfo['profile_pic'] ? opponentInfo['profile_pic'] : null) ?? "/pfp-default.png"} className="w-20 h-20 rounded-full mr-6"/> 
                                <div className="flex flex-col justify-center items-left">
                                    <span className="text-2xl font-bold text-slate-800">{opponentInfo ? opponentInfo['name'] : "Player"}</span>
                                    <div className="flex flex-row justify-center items-center">
                                        <span className="mt-2 mr-4 text-lg font-medium text-slate-600">{results ? results['opponent_rating'] : ""}</span>
                                        <BadgeDelta deltaType={results['opponent_rating_delta'] > 0 ? "increase" : "decrease"}>{Math.abs(parseInt(results['opponent_rating_delta'], 10))}</BadgeDelta>
                                    </div>
                                </div>
                            </div>
                            <div className="w-full mt-4 flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Overall Score</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">83</span>
                                </div>
                                <ProgressBar value={83} color="blue" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Eye Contact</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">71</span>
                                </div>
                                <ProgressBar value={71} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Facial Emotions</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">56</span>
                                </div>
                                <ProgressBar value={56} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Tone</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">95</span>
                                </div>
                                <ProgressBar value={95} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-lg font-semibold text-slate-600">Volume</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">50</span>
                                </div>
                                <ProgressBar value={50} color="teal" className="mt-3" />
                            </div>
                        </div>
                        <div className="bg-white shadow-card px-8 py-6 rounded-lg flex flex-col mt-2 w-full">
                            <div className="w-full flex flex-col justify-center items-center">
                                <div className="w-full flex flex-row justify-center items-center mb-2 px-1">
                                    <span className="text-gl font-semibold text-slate-600">Filler Words</span>
                                    <div className="grow" />
                                    <span className="text-lg font-medium text-slate-600">79</span>
                                </div>
                                <ProgressBar value={79} color="teal" className="mt-3" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            }
        </div>
    )
}