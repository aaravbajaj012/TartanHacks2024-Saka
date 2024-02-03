import { useEffect, useState } from "react";

export default function Timer({ onTimerFinished, totalTime }: { onTimerFinished: () => void, totalTime: number }) {
    const [timer, setTimer] = useState(totalTime);

    useEffect(() => {
        if (timer === 0) {
            onTimerFinished();
            return;
        }
        const interval = setInterval(() => {
            setTimer(timer - 1);
        }, 1000);
        return () => clearInterval(interval);
    });

    return (
        <span className="text-lg font-medium text-gray-500 dark:text-gray-400">{`${timer}s`}</span>
    );
}