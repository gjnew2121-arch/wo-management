import { auth, db } from './firebase-config.js'
import { onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js"
import { doc, getDoc }                 from "https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore.js"

const SESSION_KEY = 'wo_login_time'
const SESSION_TTL = 24 * 60 * 60 * 1000  // 24 ώρες σε ms

// ── Session helpers ──
export function recordLogin() {
  localStorage.setItem(SESSION_KEY, Date.now().toString())
}

export function isSessionValid() {
  const t = localStorage.getItem(SESSION_KEY)
  if (!t) return false
  return (Date.now() - parseInt(t)) < SESSION_TTL
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}

// ── requireAuth ──
// Ελέγχει auth + 24h session + επιστρέφει user/role/company
// redirectTo: πού να πάει αν δεν είναι logged in
export function requireAuth(callback, redirectTo = 'index.html') {
  onAuthStateChanged(auth, async (firebaseUser) => {
    if (!firebaseUser || !isSessionValid()) {
      clearSession()
      if (firebaseUser) await signOut(auth)
      window.location.href = redirectTo
      return
    }
    const snap = await getDoc(doc(db, 'users', firebaseUser.uid))
    const data = snap.exists() ? snap.data() : {}
    callback(
      { ...firebaseUser, displayName: data.displayName || firebaseUser.email },
      data.role    || 'viewer',
      data.company || 'GAINJET'   // 'GAINJET' | 'GJET' | 'both'
    )
  })
}

// ── setupNav ──
export function setupNav(user, role, company, activePage) {
  const navUser = document.getElementById('nav-user')
  const navRole = document.getElementById('nav-role')
  const navCo   = document.getElementById('nav-company')
  const navAdmin = document.getElementById('nav-admin')

  if (navUser) navUser.textContent = user.displayName
  if (navRole) { navRole.textContent = role; navRole.className = `role-badge role-${role}` }
  if (navCo)   { navCo.textContent = company; navCo.className = `company-badge company-${company.toLowerCase()}` }
  if (navAdmin) navAdmin.style.display = role === 'admin' ? 'flex' : 'none'

  document.querySelectorAll('.nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.page === activePage)
  )

  const signoutBtn = document.getElementById('btn-signout')
  if (signoutBtn) {
    signoutBtn.addEventListener('click', async () => {
      clearSession()
      await signOut(auth)
      window.location.href = 'index.html'
    })
  }
}

// ── Toast ──
export function showToast(msg, type = '') {
  let t = document.getElementById('toast')
  if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t) }
  t.textContent = msg
  t.className = `toast show ${type}`
  setTimeout(() => t.classList.remove('show'), 2800)
}
