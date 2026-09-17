import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js"
import { getAuth }       from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js"
import { getFirestore }  from "https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore.js"

export const firebaseConfig = {
  apiKey:            "AIzaSyDVWVXKhxg0nEK08D20BOKJKyomf30-5ZE",
  authDomain:        "worecord-e9fe8.firebaseapp.com",
  projectId:         "worecord-e9fe8",
  storageBucket:     "worecord-e9fe8.firebasestorage.app",
  messagingSenderId: "443518548336",
  appId:             "1:443518548336:web:6f9fbad37d319ae9c6b7b5"
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const db   = getFirestore(app)
