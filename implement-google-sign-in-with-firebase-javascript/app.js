import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,        // ← Google provider
  signInWithPopup,            // ← Popup method
  signInWithRedirect,         // ← Redirect method (optional)
  getRedirectResult,          // ← To retrieve redirect result
  onAuthStateChanged,
    signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword

} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCO9MfMhs73FIRAWAxW2S5Pt0_hQiNRgE0",
  authDomain: "login-app-d9e9f.firebaseapp.com",
  projectId: "login-app-d9e9f",
  storageBucket: "login-app-d9e9f.firebasestorage.app",
  messagingSenderId: "196676906536",
  appId: "1:196676906536:web:2182b0d5294eac84840f1d"
};

const app      = initializeApp(firebaseConfig);
const auth     = getAuth(app);

const googleBtn = document.getElementById("google-signin-btn");

if (googleBtn) {
    googleBtn.addEventListener("click", async () => {
        try {
            const result = await signInWithPopup(auth, provider);

            // Get the Goole OAuth access token
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential.accessToken;

            // Get the signed-in user's profile info
            const user = result.user;
            console.log("Name:", user.displayName);
            console.log("Email:", user.email);
            console.log("Photo:", user.photoURL);
            console.log("UID:", user.uid);

            window.location.href = "dashboard.html";
        } catch (error) {
            handleGoogleAuthError(error);
        }
    });
}

// ---- GOOGLE SIGN-IN (REDIRECT) ----
async function signInWithGoogleRedirect() {
    try {
        await signInWithRedirect(auth, provider);
    } catch (error) {
        console.log("Redirect initiation error:", error.message);
    }
}

// ---- HANDLE REDIRECT RESULT (on page load) ----
getRedirectResult(auth) 
    .then((result) => {
        if (result) {
            const user = result.user;
            console.log("Redirect sign-in successful:", user.email);
            window.location.href = "dashboard.html";
        }
    })
    .catch((error) => {
        handleGoogleAuthError(error);
    })


// ---- SHOW GOOGLE USER PROFILE ON DASHBOARD ----
onAuthStateChanged(auth, (user) => {
    if (user) {
        const nameEl = document.getElementById("user-name");
        const emailEl = document.getElementById("user-email");
        const photoEl = document.getElementById("user-photo");

        if (nameEl) nameEl.textContent = "Hello, " + (user.displayName) || "User";
        if (emailEl) emailEl.textContent = user.email;
        if (photoEl && user.photoURL) {
            photoEl.src = user.photoURL;
            photoEl.style.display = "block";
        }
    } else {
        if (window.location.pathname.includes("dashboard.html")) {
            window.location.href = "index.html";
        }
    }
});


// ---- LOGOUT (works for Google + Email/Password users) ----
const logoutBtn = document.getElementById("logout-btn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            await signOut(auth);
            window.location.href = "index.html";
        } catch (error) {
            alert("Logout failed: " + error.message);
        }
    });
}

const provider = new GoogleAuthProvider(); // Initialize the Google provider
// Request access to the user's Google Calendar (optional scope)
provider.addScope("https://www.googleapis.com/auth/calendar.readonly");

provider.setCustomParameters({
    prompt: "select_account"
});

// ---- GOOGLE AUTH ERROR HANDLER ----
function handleGoogleAuthError(error) {
    const msgs = {
        "auth/popup-closed-by-user":       "Sign-in popup was closed. Please try again.",
        "auth/popup-blocked":              "Popup was blocked by your browser. Allow popups and retry.",
        "auth/account-exists-with-different-credential": "An account already exists with this email using a different sign-in method.",
        "auth/cancelled-popup-request":    "Another popup is already open.",
        "auth/network-request-failed":     "Network error. Please check your connection.",
        "auth/unauthorized-domain":        "This domain is not authorized. Add it in Firebase Console → Authentication → Settings."
  };

    const message = msgs[error.code] || "Google Sign-In failed. Please try again.";
    alert(message);
    console.log(error.code, error.message);
    
}
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
            handleAuthError(error);
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

