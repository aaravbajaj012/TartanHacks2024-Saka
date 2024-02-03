import { initializeApp } from "firebase/app";
import { onAuthStateChanged, signInWithRedirect, getAuth, GoogleAuthProvider, signOut } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyDfD_DoC1VJ23lhgQPfJmkSIynia1O0Lj4",
    authDomain: "tartanhacks-5dc41.firebaseapp.com",
    projectId: "tartanhacks-5dc41",
    storageBucket: "tartanhacks-5dc41.appspot.com",
    messagingSenderId: "230576108419",
    appId: "1:230576108419:web:3c78fc2512e67a0b4f3cb6",
    measurementId: "G-KM9J6K6P21"
  };

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);
auth.useDeviceLanguage();

export { auth, onAuthStateChanged, signInWithRedirect, GoogleAuthProvider, signOut };

