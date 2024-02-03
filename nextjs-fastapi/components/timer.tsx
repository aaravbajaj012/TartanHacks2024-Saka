
export default function Timer({secondsLeft}: {secondsLeft: number}) {
    return (
        <div className="time-roundel">
            <svg viewBox="0 0 24 24" className="circle-svg">
            <circle cx="50%" cy="50%" r="50%"/>
            <path
            d="M12 2.450703414486279
                a 9.549296585513721 9.549296585513721 0 0 1 0 19.098593171027442
                a 9.549296585513721 9.549296585513721 0 0 1 0 -19.098593171027442"
            className="circle-path countdown-circle--seconds"
            stroke-dasharray={`${secondsLeft} 60`}
            />
        </svg>
            <div className="time-display">
            <p className="countdown-time--secs">{secondsLeft}</p>
            <p className="time--text">SECS</p>
            </div>
        </div> 
    );
}