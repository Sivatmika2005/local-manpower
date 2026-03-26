// firebase-config.js
const firebaseConfig = {
    apiKey: "AIzaSyAiB8UrqNbaYmZldGlcU2T5ZvSVH0bQyz8",
    authDomain: "localservicebooking.firebaseapp.com",
    projectId: "localservicebooking",
    storageBucket: "localservicebooking.firebasestorage.app",
    messagingSenderId: "615400184348",
    appId: "1:615400184348:web:17b61eababac27c9e2ddd9",
    measurementId: "G-NVVEHEWPY5"
};

// Initialize Firebase if not already initialized
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const auth = firebase.auth();
const storage = firebase.storage();
const db = typeof firebase.firestore === 'function' ? firebase.firestore() : null;

window.firebaseAuth = auth;
window.firebaseStorage = storage;
window.firebaseDb = db;
