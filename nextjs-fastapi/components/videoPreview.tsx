import { useEffect, useRef } from "react";
import React from "react";

const VideoPreview = React.memo(function VideoPreview({ stream, isHidden }: { stream: MediaStream | null, isHidden: boolean }) {
    const videoRef = useRef<HTMLVideoElement>(null);
  
    useEffect(() => {
      if (videoRef.current && stream) {
        videoRef.current.srcObject = stream;
      }
    }, [stream]);
    if (!stream) {
      return null;
    }
    return <video ref={videoRef} width={400} height={300} autoPlay className={"rounded-lg " + (isHidden ? "opacity-0" : "")} />;
});

export default VideoPreview;
  