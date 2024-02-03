

export default function LoadingIcon({ width, borderColor }: { width: string, borderColor: string }) {
    return <div className={`loader ${width} ${borderColor}`}/>;
}