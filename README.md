# WO Management System — GainJet & GJet

HTML + Firebase + GitHub Pages

## Αρχεία
```
index.html      ← Login (session 24ωρο)
home.html       ← Επιλογή εταιρίας
gainjet.html    ← GainJet Work Orders
gjet.html       ← GJet SM Work Orders
admin.html      ← User Management (admin only)
css/style.css
js/firebase-config.js  ← ΕΔΩ βάζεις τα credentials
js/auth.js             ← Auth + 24h session
js/status.js           ← Χρώματα status
firestore.rules
import_excel.py        ← Import GainJet Excel
```

## Firestore Collections
```
/gainjet_workOrders    ← GainJet WOs
/gjet_workOrders       ← GJet SM WOs
/users                 ← Users με role + company
```

## User fields στο Firestore
```
displayName: "John Tech"
email:       "john@company.com"
role:        "viewer" | "editor" | "admin"
company:     "GAINJET" | "GJET" | "both"
```

## Access logic
| company | role   | Πρόσβαση |
|---------|--------|----------|
| GAINJET | any    | Μόνο GainJet → redirect αυτόματα |
| GJET    | any    | Μόνο GJet → redirect αυτόματα |
| both    | any    | Home → επιλογή |
| any     | admin  | Home → και τις δύο |

## Session
- Login → αποθηκεύει timestamp στο localStorage
- Κάθε σελίδα ελέγχει αν έχουν περάσει < 24h
- Μετά από 24h → αυτόματο logout + redirect στο login

## Setup
1. Firebase → Auth (Email) + Firestore
2. `js/firebase-config.js` → βάλε credentials
3. Firestore → Rules → paste `firestore.rules`
4. Authentication → Add user → Firestore → `users/{uid}` με `role:admin, company:both`
5. GitHub → push → Settings → Pages → GitHub Actions
6. `python import_excel.py` → import GainJet data
