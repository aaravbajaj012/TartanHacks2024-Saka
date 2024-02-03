import { auth, signOut } from "@/utils/firebase";
import { ChevronDownIcon } from "@heroicons/react/24/outline";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Header() {
    const [profileMenuExpanded, setProfileMenuExpanded] = useState(false); 
    const router = useRouter();

    return (
        <div className="w-full flex flex-row pt-6 px-12">
            <div className="grow"/>
            <div 
                className="relative flex flex-row items-center justify-center"
                onClick={() => setProfileMenuExpanded(!profileMenuExpanded)}
            >
                <>
                    <img 
                        src={auth.currentUser?.photoURL ?? 'public/pfp_default.png'} 
                        alt="profile picture" 
                        className="rounded-full h-8 w-8"
                    />
                    <span className="text-base font-semibold m-4">{auth.currentUser?.displayName}</span>
                    <ChevronDownIcon className="w-5 h-5" />
                </>
                {profileMenuExpanded && (
                <div className="absolute right-0 top-full flex flex-row">
                    <div className="rounded-lg bg-white shadow-lg z-10 mr-1">
                        <button 
                            className="text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
                            onClick={async () => {
                                await signOut(auth);
                                router.push('/sign-in');
                            }}
                        >
                            Sign out
                        </button>
                    </div>
                </div>
            )}
            </div>
        </div>
    )

}