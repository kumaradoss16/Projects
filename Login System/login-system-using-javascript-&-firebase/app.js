// Import the functions you need from the SDKs you need
// import { initializeApp } from "firebase/app";
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
  signOut
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// SIGN UP 
const signupBtn = document.getElementById("signup-btn");

if (signupBtn) {
    signupBtn.addEventListener("click", () => {
        const email = document.getElementById("email-signup").value.trim();
        const password = document.getElementById("password-signup").value.trim();

        createUserWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                console.log("User Created:", userCredential.user.email);
                alert("Account created successfully! Redirecting to login...");
                window.location.href = "index.html";
            }).catch((error) => {
            handleError(error);
        });
    });
}

// LOGIN 
const loginBtn = document.getElementById("login-btn");

if (loginBtn) {
    loginBtn.addEventListener("click", () => {
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                console.log("Logged in as:", userCredential.user.email);
                alert("Signed in successfully! Redirecting to dashboard...");
                window.location.href = "dashboard.html";
            }).catch((error) => {
            handleAuthError(error);
        });
    });
}

// AUTH STATE LISTENER 
onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in 
        console.log("Active User:", user.email);
        // Optional: auto-redirect logged-in users away from login page 
        if (window.location.pathname.includes("index.html")) {
            window.location.href = "dashboard.html";
        }
    } else {
        console.log("No active session.");
    }
});

// SIGN OUT
const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        signOut(auth)
            .then(() => {
                alert("You have been signed out.");
                window.location.href = "index.html";
            }).catch((error) => {
                console.error("Sign-out error:", error.message);
            });
    });
}

// ERROR HANDLER 
function handleAuthError(error) {
    const errorMessages = {
        "auth/email-already-in-use": "This email is already registered. Try logging in.",
        "auth/invalid-email": "Please enter a valid email address.",
        "auth/weak-password": "Password must be at least 6 characters.",
        "auth/user-not-found": "No account found with this email.",
        "auth/wrong-password": "Incorrect password. Please try again.",
        "auth/too-many-requests": "Too many attempts. Please try again later."
    };

    const message = errorMessages[error.code] || "Something went wrong. Please try again.";
    alert(message);
    console.error(error.code, error.message);
}
