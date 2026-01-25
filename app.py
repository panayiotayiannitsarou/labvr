"""
VR School Library - Βιβλιοθήκη Εικονικής Πραγματικότητας
Για μαθητές 15-18 ετών με smartphone + VR headset case

Εκτέλεση:
    pip install streamlit qrcode pillow
    streamlit run vr_library.py

Features:
- Εκπαιδευτικό περιεχόμενο (Φυσική, Ιστορία, Βιολογία, Χημεία)
- Χαλάρωση/Ψυχαγωγία (Φύση, Περιπέτειες, Χόμπι)
- Mobile-responsive interface
- QR codes για instant VR launch
- Favorites & Search
- Admin panel για προσθήκη περιεχομένου
"""
import streamlit as st
import sqlite3
import io
import base64
from typing import Optional, List, Dict, Any
from datetime import datetime
from urllib.parse import quote

try:
    import qrcode
    from PIL import Image
    HAS_QR = True
except ImportError:
    HAS_QR = False


# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db() -> None:
    """Initialize SQLite database with schema."""
    conn = sqlite3.connect('vr_library.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Experiences table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            subcategory TEXT,
            duration_min INTEGER,
            difficulty TEXT,
            youtube_url TEXT NOT NULL,
            thumbnail_url TEXT,
            learning_goals TEXT,
            key_concepts TEXT,
            discussion_questions TEXT,
            safety_notes TEXT,
            views_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Favorites table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            experience_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experience_id) REFERENCES experiences(id),
            UNIQUE(session_id, experience_id)
        )
    ''')
    
    # Seed data if empty
    count = conn.execute('SELECT COUNT(*) as c FROM experiences').fetchone()[0]
    if count == 0:
        seed_data(conn)
    
    conn.commit()
    conn.close()


def seed_data(conn: sqlite3.Connection) -> None:
    """Seed initial VR experiences."""
    experiences = [
        # ======== ΕΚΠΑΙΔΕΥΤΙΚΑ - ΦΥΣΙΚΗ ========
        (
            'Διαστημικός Σταθμός ISS 360°',
            'Εξερεύνησε τον Διεθνή Διαστημικό Σταθμό και μάθε πώς ζουν οι αστροναύτες',
            'Εκπαιδευτικό',
            'Φυσική',
            15,
            'Εύκολο',
            'https://www.youtube.com/watch?v=QvTmdIhYnes',
            'https://img.youtube.com/vi/QvTmdIhYnes/maxresdefault.jpg',
            'Κατανόηση ζωής σε συνθήκες μηδενικής βαρύτητας',
            'Βαρύτητα, Όρμηση, Διαστημική Τεχνολογία',
            '1. Πώς κινούνται οι αστροναύτες;\n2. Τι τρώνε και πώς;\n3. Πώς λειτουργεί η τουαλέτα;',
            'Καθιστή θέση συνιστάται. Κανένα motion sickness.'
        ),
        (
            'Πυρηνικός Αντιδραστήρας - Μέσα στο Ατομικό Εργοστάσιο',
            'Δες από μέσα πώς λειτουργεί ένας πυρηνικός σταθμός',
            'Εκπαιδευτικό',
            'Φυσική',
            12,
            'Μέτριο',
            'https://www.youtube.com/watch?v=tyDbq5HRs0o',
            'https://img.youtube.com/vi/tyDbq5HRs0o/maxresdefault.jpg',
            'Κατανόηση πυρηνικής ενέργειας και ασφάλειας',
            'Σχάση, Ενέργεια, Ραδιενέργεια',
            '1. Πώς παράγεται ενέργεια;\n2. Τι είναι η σχάση;\n3. Ποια μέτρα ασφαλείας;',
            'Εκπαιδευτική προσομοίωση, όχι πραγματικός κίνδυνος'
        ),
        (
            'Ηλιακό Σύστημα - Ταξίδι στους Πλανήτες',
            'Πέταξε από πλανήτη σε πλανήτη και εξερεύνησε το σύστημά μας',
            'Εκπαιδευτικό',
            'Φυσική',
            18,
            'Εύκολο',
            'https://www.youtube.com/watch?v=D8pnmwOXhoY',
            'https://img.youtube.com/vi/D8pnmwOXhoY/maxresdefault.jpg',
            'Γνωριμία με πλανήτες και τα χαρακτηριστικά τους',
            'Πλανήτες, Τροχιές, Βαρύτητα',
            '1. Ποιος πλανήτης είναι μεγαλύτερος;\n2. Γιατί ο Πλούτωνας δεν είναι πλανήτης;\n3. Τι είναι οι δακτύλιοι του Κρόνου;',
            'Αργή κίνηση, κατάλληλο για όλους'
        ),
        
        # ======== ΕΚΠΑΙΔΕΥΤΙΚΑ - ΙΣΤΟΡΙΑ ========
        (
            'Μάχη της Σαλαμίνας - Ναυμαχία 480 π.Χ.',
            'Ζήσε την ιστορική ναυμαχία που άλλαξε την Ευρώπη',
            'Εκπαιδευτικό',
            'Ιστορία',
            20,
            'Μέτριο',
            'https://www.youtube.com/watch?v=nWz5JVRobCg',
            'https://img.youtube.com/vi/nWz5JVRobCg/maxresdefault.jpg',
            'Κατανόηση στρατηγικής σημασίας της μάχης',
            'Αρχαία Ελλάδα, Περσικοί Πόλεμοι, Ναυτική Στρατηγική',
            '1. Ποιος ηγήθηκε των Ελλήνων;\n2. Γιατί νίκησαν;\n3. Τι συνέπειες είχε;',
            'Ήρεμη παρακολούθηση, χωρίς βία'
        ),
        (
            'Ακρόπολη Αθηνών - Εικονική Περιήγηση',
            'Περπάτησε στην αρχαία Ακρόπολη και δες τον Παρθενώνα',
            'Εκπαιδευτικό',
            'Ιστορία',
            15,
            'Εύκολο',
            'https://www.youtube.com/watch?v=VUiTp8oTzWM',
            'https://img.youtube.com/vi/VUiTp8oTzWM/maxresdefault.jpg',
            'Εκτίμηση αρχαίας αρχιτεκτονικής',
            'Κλασική Αθήνα, Αρχιτεκτονική, Γλυπτική',
            '1. Πότε χτίστηκε;\n2. Ποιος θεός τιμούνταν;\n3. Τι υλικό χρησιμοποιήθηκε;',
            'Στατική θέαση, χωρίς κίνηση'
        ),
        (
            'Β\' Παγκόσμιος Πόλεμος - Απόβαση στη Νορμανδία',
            'Βίωσε την ιστορική ημέρα D-Day από κοντά',
            'Εκπαιδευτικό',
            'Ιστορία',
            25,
            'Δύσκολο',
            'https://www.youtube.com/watch?v=EGW0R2rgeVI',
            'https://img.youtube.com/vi/EGW0R2rgeVI/maxresdefault.jpg',
            'Κατανόηση μεγαλύτερης στρατιωτικής επιχείρησης',
            'Β\' ΠΠ, Σύμμαχοι, Στρατηγική',
            '1. Πότε έγινε η απόβαση;\n2. Πόσες χώρες συμμετείχαν;\n3. Γιατί ήταν κρίσιμη;',
            'Περιέχει ιστορικό υλικό πολέμου. Προαιρετική θέαση.'
        ),
        
        # ======== ΕΚΠΑΙΔΕΥΤΙΚΑ - ΒΙΟΛΟΓΙΑ ========
        (
            'Ανθρώπινη Καρδιά - Μέσα στο Κυκλοφορικό',
            'Εξερεύνησε την καρδιά και τα αιμοφόρα αγγεία',
            'Εκπαιδευτικό',
            'Βιολογία',
            12,
            'Εύκολο',
            'https://www.youtube.com/watch?v=gcgBhIz5MKU',
            'https://img.youtube.com/vi/gcgBhIz5MKU/maxresdefault.jpg',
            'Κατανόηση λειτουργίας κυκλοφορικού συστήματος',
            'Καρδιά, Αίμα, Κυκλοφορικό',
            '1. Πόσες κοιλίες έχει η καρδιά;\n2. Πώς κυκλοφορεί το αίμα;\n3. Τι κάνουν οι βαλβίδες;',
            'Εκπαιδευτική animation, όχι πραγματικό όργανο'
        ),
        (
            'Κύτταρο & DNA - Μοριακή Βιολογία',
            'Ταξίδεψε μέσα στο κύτταρο και δες το DNA',
            'Εκπαιδευτικό',
            'Βιολογία',
            16,
            'Μέτριο',
            'https://www.youtube.com/watch?v=yqESR7E4b_8',
            'https://img.youtube.com/vi/yqESR7E4b_8/maxresdefault.jpg',
            'Κατανόηση δομής DNA και κυττάρου',
            'DNA, Χρωμοσώματα, Πυρήνας',
            '1. Τι είναι το DNA;\n2. Πώς αντιγράφεται;\n3. Τι ρόλο έχουν τα ριβοσώματα;',
            '3D animation, ήρεμη προσέγγιση'
        ),
        (
            'Υποβρύχιος Κόσμος - Κοραλλιογενής Ύφαλος',
            'Κατάδυση στον κοραλλιογενή ύφαλο και τη θαλάσσια ζωή',
            'Εκπαιδευτικό',
            'Βιολογία',
            20,
            'Εύκολο',
            'https://www.youtube.com/watch?v=BaoHJN4SG7w',
            'https://img.youtube.com/vi/BaoHJN4SG7w/maxresdefault.jpg',
            'Εκτίμηση θαλάσσιας βιοποικιλότητας',
            'Οικοσυστήματα, Θαλάσσια Ζωή, Κοράλλια',
            '1. Τι είναι κοράλλι;\n2. Ποια ζώα είδες;\n3. Γιατί απειλούνται;',
            'Ήρεμη κολύμβηση, χωρίς έντονη κίνηση'
        ),
        
        # ======== ΕΚΠΑΙΔΕΥΤΙΚΑ - ΧΗΜΕΙΑ ========
        (
            'Περιοδικός Πίνακας - Τα Στοιχεία σε 3D',
            'Εξερεύνησε τα χημικά στοιχεία διαδραστικά',
            'Εκπαιδευτικό',
            'Χημεία',
            14,
            'Μέτριο',
            'https://www.youtube.com/watch?v=qm0IfG1GyZU',
            'https://img.youtube.com/vi/qm0IfG1GyZU/maxresdefault.jpg',
            'Κατανόηση δομής περιοδικού πίνακα',
            'Άτομα, Ηλεκτρόνια, Περίοδοι',
            '1. Τι είναι άτομο;\n2. Πώς οργανώνονται τα στοιχεία;\n3. Ποιο το πιο κοινό;',
            'Στατική παρουσίαση'
        ),
        
        # ======== ΧΑΛΑΡΩΣΗ - ΦΥΣΗ ========
        (
            'Ήρεμη Παραλία - Ηλιοβασίλεμα στα Κύματα',
            'Χαλάρωσε δίπλα στη θάλασσα με τον ήχο των κυμάτων',
            'Χαλάρωση',
            'Φύση',
            30,
            'Εύκολο',
            'https://www.youtube.com/watch?v=V1bFr2SWP1I',
            'https://img.youtube.com/vi/V1bFr2SWP1I/maxresdefault.jpg',
            'Μείωση άγχους, ηρεμία',
            'Mindfulness, Διαλογισμός, Χαλάρωση',
            '',
            'Ιδανικό για διάλειμμα. Καθιστή θέση.'
        ),
        (
            'Βουνό - Κορυφή Έβερεστ Sunrise',
            'Απόλαυσε την ανατολή από την κορυφή του κόσμου',
            'Χαλάρωση',
            'Φύση',
            25,
            'Μέτριο',
            'https://www.youtube.com/watch?v=oHg5SJYRHA0',
            'https://img.youtube.com/vi/oHg5SJYRHA0/maxresdefault.jpg',
            'Αίσθημα επιτυχίας, ηρεμία',
            'Φύση, Βουνά, Ύψος',
            '',
            'Όχι για ακροφοβία. Ύψη απεικονίζονται.'
        ),
        (
            'Δάσος Φθινοπώρου - Περίπατος στη Φύση',
            'Περπάτησε σε ένα ήρεμο δάσος γεμάτο χρώματα',
            'Χαλάρωση',
            'Φύση',
            20,
            'Εύκολο',
            'https://www.youtube.com/watch?v=d0tU18Ybcvk',
            'https://img.youtube.com/vi/d0tU18Ybcvk/maxresdefault.jpg',
            'Σύνδεση με φύση, ηρεμία',
            'Φύση, Δάσος, Εποχές',
            '',
            'Αργή κίνηση, ιδανικό για όλους'
        ),
        (
            'Βόρειο Σέλας - Φινλανδία Night Sky',
            'Παρακολούθησε το μαγικό φαινόμενο του σέλας',
            'Χαλάρωση',
            'Φύση',
            18,
            'Εύκολο',
            'https://www.youtube.com/watch?v=nT7K3bRMjos',
            'https://img.youtube.com/vi/nT7K3bRMjos/maxresdefault.jpg',
            'Θαυμασμός φυσικού φαινομένου',
            'Μαγνητικό Πεδίο, Ατμόσφαιρα',
            '',
            'Στατική θέαση, χωρίς κίνηση'
        ),
        
        # ======== ΧΑΛΑΡΩΣΗ - ΠΕΡΙΠΕΤΕΙΕΣ ========
        (
            'Ζούγλα Αμαζονίου - Εξερεύνηση Βροχόδασους',
            'Περπάτησε στην πιο πυκνή ζούγλα του κόσμου',
            'Χαλάρωση',
            'Περιπέτειες',
            22,
            'Μέτριο',
            'https://www.youtube.com/watch?v=kXfvN4JaWGY',
            'https://img.youtube.com/vi/kXfvN4JaWGY/maxresdefault.jpg',
            'Σύνδεση με άγρια φύση',
            'Ζούγλα, Βιοποικιλότητα, Περιπέτεια',
            '',
            'Ήρεμη εξερεύνηση, όχι επικίνδυνα ζώα'
        ),
        (
            'Αναρρίχηση - Yosemite Rock Climbing',
            'Σκαρφάλωσε σε κάθετο βράχο (ασφαλής προσομοίωση)',
            'Χαλάρωση',
            'Περιπέτειες',
            15,
            'Δύσκολο',
            'https://www.youtube.com/watch?v=Cyya23MPoAI',
            'https://img.youtube.com/vi/Cyya23MPoAI/maxresdefault.jpg',
            'Ενίσχυση αυτοπεποίθησης',
            'Αθλητισμός, Ύψος, Δύναμη',
            '',
            'ΟΧΙ για ακροφοβία. Έντονη κατακόρυφη κίνηση.'
        ),
        (
            'Safari Αφρική - Λιοντάρια & Ελέφαντες',
            'Πλησίασε άγρια ζώα από απόσταση ασφαλείας',
            'Χαλάρωση',
            'Περιπέτειες',
            25,
            'Εύκολο',
            'https://www.youtube.com/watch?v=gpJHZzlTiAw',
            'https://img.youtube.com/vi/gpJHZzlTiAw/maxresdefault.jpg',
            'Γνωριμία με άγρια πανίδα',
            'Ζώα, Σαβάνα, Αφρική',
            '',
            'Ήρεμη παρατήρηση από safari jeep'
        ),
        
        # ======== ΧΑΛΑΡΩΣΗ - ΧΟΜΠΙ ========
        (
            'Ποδόσφαιρο - Camp Nou Stadium Tour',
            'Επισκέψου το θρυλικό γήπεδο της Μπαρτσελόνα',
            'Χαλάρωση',
            'Χόμπι',
            18,
            'Εύκολο',
            'https://www.youtube.com/watch?v=lJLIbg_tB4Q',
            'https://img.youtube.com/vi/lJLIbg_tB4Q/maxresdefault.jpg',
            'Σύνδεση με αγαπημένο άθλημα',
            'Ποδόσφαιρο, Γήπεδα, Αθλητισμός',
            '',
            'Στατική περιήγηση γηπέδου'
        ),
        (
            'Μουσική - Virtual Concert Philharmonic',
            'Ακούσε συμφωνική ορχήστρα από την πρώτη σειρά',
            'Χαλάρωση',
            'Χόμπι',
            30,
            'Εύκολο',
            'https://www.youtube.com/watch?v=Zi8vJ_lMxQI',
            'https://img.youtube.com/vi/Zi8vJ_lMxQI/maxresdefault.jpg',
            'Εκτίμηση κλασικής μουσικής',
            'Μουσική, Ορχήστρα, Πολιτισμός',
            '',
            'Καθιστή ακρόαση, χρειάζεται ακουστικά'
        ),
        (
            'Διάστημα - Περίπατος Αστροναύτη (Spacewalk)',
            'Κάνε spacewalk έξω από το ISS',
            'Χαλάρωση',
            'Χόμπι',
            20,
            'Μέτριο',
            'https://www.youtube.com/watch?v=KaOC9danxNo',
            'https://img.youtube.com/vi/KaOC9danxNo/maxresdefault.jpg',
            'Εμπειρία μηδενικής βαρύτητας',
            'Διάστημα, Τεχνολογία, Αστροναύτες',
            '',
            'Αργή κίνηση, μπορεί να προκαλέσει ίλιγγο'
        ),
    ]
    
    conn.executemany('''
        INSERT INTO experiences 
        (title, description, category, subcategory, duration_min, difficulty, 
         youtube_url, thumbnail_url, learning_goals, key_concepts, 
         discussion_questions, safety_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', experiences)


def get_db() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect('vr_library.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# QR CODE GENERATION
# ============================================================================

def generate_qr_code(url: str) -> Optional[str]:
    """Generate QR code and return base64 image."""
    if not HAS_QR:
        return None
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        img_base64 = base64.b64encode(buf.read()).decode()
        return f"data:image/png;base64,{img_base64}"
    except Exception:
        return None


# ============================================================================
# SESSION STATE INIT
# ============================================================================

if 'session_id' not in st.session_state:
    st.session_state.session_id = base64.b64encode(
        datetime.now().isoformat().encode()
    ).decode()[:16]

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'library'

if 'selected_exp_id' not in st.session_state:
    st.session_state.selected_exp_id = None


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="VR School Library 📚",
    page_icon="🥽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-responsive design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .exp-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .exp-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .educational {
        background: #e3f2fd;
        color: #1976d2;
    }
    .relaxation {
        background: #f3e5f5;
        color: #7b1fa2;
    }
    .qr-container {
        text-align: center;
        padding: 1rem;
        background: #f5f5f5;
        border-radius: 10px;
    }
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        .exp-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_experiences(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get experiences with filters."""
    conn = get_db()
    
    query = 'SELECT * FROM experiences WHERE 1=1'
    params = []
    
    if category and category != 'Όλα':
        query += ' AND category = ?'
        params.append(category)
    
    if subcategory and subcategory != 'Όλα':
        query += ' AND subcategory = ?'
        params.append(subcategory)
    
    if difficulty and difficulty != 'Όλα':
        query += ' AND difficulty = ?'
        params.append(difficulty)
    
    if search:
        query += ' AND (title LIKE ? OR description LIKE ? OR key_concepts LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    query += ' ORDER BY views_count DESC, title ASC'
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_experience_by_id(exp_id: int) -> Optional[Dict[str, Any]]:
    """Get single experience by ID."""
    conn = get_db()
    row = conn.execute('SELECT * FROM experiences WHERE id = ?', (exp_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def increment_views(exp_id: int) -> None:
    """Increment view count."""
    conn = get_db()
    conn.execute(
        'UPDATE experiences SET views_count = views_count + 1 WHERE id = ?',
        (exp_id,)
    )
    conn.commit()
    conn.close()


def is_favorite(session_id: str, exp_id: int) -> bool:
    """Check if experience is favorited."""
    conn = get_db()
    result = conn.execute(
        'SELECT 1 FROM favorites WHERE session_id = ? AND experience_id = ?',
        (session_id, exp_id)
    ).fetchone()
    conn.close()
    return result is not None


def toggle_favorite(session_id: str, exp_id: int) -> bool:
    """Toggle favorite status. Returns new state (True = favorited)."""
    conn = get_db()
    
    if is_favorite(session_id, exp_id):
        conn.execute(
            'DELETE FROM favorites WHERE session_id = ? AND experience_id = ?',
            (session_id, exp_id)
        )
        conn.commit()
        conn.close()
        return False
    else:
        conn.execute(
            'INSERT INTO favorites (session_id, experience_id) VALUES (?, ?)',
            (session_id, exp_id)
        )
        conn.commit()
        conn.close()
        return True


def get_favorites(session_id: str) -> List[Dict[str, Any]]:
    """Get all favorites for session."""
    conn = get_db()
    rows = conn.execute('''
        SELECT e.* FROM experiences e
        JOIN favorites f ON e.id = f.experience_id
        WHERE f.session_id = ?
        ORDER BY f.created_at DESC
    ''', (session_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header() -> None:
    """Render main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🥽 VR School Library</h1>
        <p>Βιβλιοθήκη Εικονικής Πραγματικότητας για Μαθητές 15-18 ετών</p>
        <p style="font-size: 0.9rem; opacity: 0.9;">
            Χρησιμοποίησε το smartphone σου + VR headset case για μοναδικές εμπειρίες!
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_navigation() -> None:
    """Render navigation buttons."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📚 Βιβλιοθήκη", use_container_width=True):
            st.session_state.current_view = 'library'
            st.rerun()
    
    with col2:
        if st.button("⭐ Αγαπημένα", use_container_width=True):
            st.session_state.current_view = 'favorites'
            st.rerun()
    
    with col3:
        if st.button("ℹ️ Οδηγίες", use_container_width=True):
            st.session_state.current_view = 'help'
            st.rerun()
    
    with col4:
        if st.button("🔧 Admin", use_container_width=True):
            st.session_state.current_view = 'admin'
            st.rerun()


def render_experience_card(exp: Dict[str, Any], show_details_btn: bool = True) -> None:
    """Render experience card."""
    category_class = 'educational' if exp['category'] == 'Εκπαιδευτικό' else 'relaxation'
    
    st.markdown(f"""
    <div class="exp-card">
        <span class="category-badge {category_class}">{exp['category']}</span>
        <span class="category-badge" style="background: #fff3e0; color: #e65100;">
            {exp['subcategory']}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {exp['title']}")
        st.write(exp['description'])
        st.caption(f"⏱️ {exp['duration_min']} λεπτά | 🎯 {exp['difficulty']} | 👁️ {exp['views_count']} προβολές")
    
    with col2:
        if exp['thumbnail_url']:
            st.image(exp['thumbnail_url'], use_container_width=True)
    
    if show_details_btn:
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📖 Λεπτομέρειες", key=f"details_{exp['id']}", use_container_width=True):
                st.session_state.selected_exp_id = exp['id']
                st.session_state.current_view = 'experience'
                st.rerun()
        
        with col_btn2:
            is_fav = is_favorite(st.session_state.session_id, exp['id'])
            fav_icon = "⭐" if is_fav else "☆"
            if st.button(f"{fav_icon} Αγαπημένο", key=f"fav_{exp['id']}", use_container_width=True):
                toggle_favorite(st.session_state.session_id, exp['id'])
                st.rerun()


# ============================================================================
# PAGES
# ============================================================================

def library_page() -> None:
    """Main library page."""
    
    # First-time welcome screen
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    
    if st.session_state.first_visit:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 3rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h1>👋 Καλώς ήρθες στη VR School Library!</h1>
            <p style="font-size: 1.2rem; margin-top: 1rem;">
                Εξερεύνησε 48 εμπειρίες VR για μάθηση και χαλάρωση
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 📱 Πώς Λειτουργεί:
            
            **1️⃣ Επίλεξε Εμπειρία**  
            Διάλεξε από εκπαιδευτικά ή χαλάρωση
            
            **2️⃣ Κάνε Κλικ "Λεπτομέρειες"**  
            Δες πληροφορίες και ερωτήσεις
            
            **3️⃣ Σάρωσε QR Code**  
            Με την κάμερα του smartphone σου
            
            **4️⃣ Φόρεσε VR Headset**  
            Τοποθέτησε το smartphone και enjoy!
            
            **5️⃣ Συζήτηση**  
            Απάντησε τις ερωτήσεις με την τάξη
            """)
            
            st.markdown("---")
            
            if st.button("✅ Κατάλαβα! Ας Ξεκινήσουμε", type="primary", use_container_width=True):
                st.session_state.first_visit = False
                st.rerun()
        
        st.stop()
    
    st.markdown("## 📚 Βιβλιοθήκη Εμπειριών")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.selectbox(
            "Κατηγορία",
            ["Όλα", "Εκπαιδευτικό", "Χαλάρωση"]
        )
    
    with col2:
        # Get unique subcategories
        conn = get_db()
        subcat_query = 'SELECT DISTINCT subcategory FROM experiences WHERE subcategory IS NOT NULL'
        if category_filter != 'Όλα':
            subcat_query += f" AND category = '{category_filter}'"
        subcats = [row[0] for row in conn.execute(subcat_query).fetchall()]
        conn.close()
        
        subcategory_filter = st.selectbox(
            "Υποκατηγορία",
            ["Όλα"] + sorted(subcats)
        )
    
    with col3:
        difficulty_filter = st.selectbox(
            "Δυσκολία",
            ["Όλα", "Εύκολο", "Μέτριο", "Δύσκολο"]
        )
    
    with col4:
        search_term = st.text_input("🔍 Αναζήτηση", placeholder="π.χ. διάστημα")
    
    st.markdown("---")
    
    # Get filtered experiences
    experiences = get_all_experiences(
        category=category_filter if category_filter != 'Όλα' else None,
        subcategory=subcategory_filter if subcategory_filter != 'Όλα' else None,
        difficulty=difficulty_filter if difficulty_filter != 'Όλα' else None,
        search=search_term if search_term else None
    )
    
    if not experiences:
        st.info("Δεν βρέθηκαν εμπειρίες με αυτά τα φίλτρα.")
        return
    
    st.caption(f"Βρέθηκαν {len(experiences)} εμπειρίες")
    
    # Render cards
    for exp in experiences:
        render_experience_card(exp)
        st.markdown("---")


def experience_page() -> None:
    """Detailed experience page."""
    if not st.session_state.selected_exp_id:
        st.warning("Δεν επιλέχθηκε εμπειρία.")
        if st.button("← Επιστροφή στη Βιβλιοθήκη"):
            st.session_state.current_view = 'library'
            st.rerun()
        return
    
    exp = get_experience_by_id(st.session_state.selected_exp_id)
    if not exp:
        st.error("Η εμπειρία δεν βρέθηκε.")
        return
    
    # Track views once per session per experience
    if 'viewed_experiences' not in st.session_state:
        st.session_state.viewed_experiences = set()
    
    if exp['id'] not in st.session_state.viewed_experiences:
        increment_views(exp['id'])
        st.session_state.viewed_experiences.add(exp['id'])
    
    # Back button
    if st.button("← Επιστροφή", key="back_btn"):
        st.session_state.current_view = 'library'
        st.rerun()
    
    st.markdown("---")
    
    # Title & Category
    category_class = 'educational' if exp['category'] == 'Εκπαιδευτικό' else 'relaxation'
    st.markdown(f"""
    <span class="category-badge {category_class}">{exp['category']}</span>
    <span class="category-badge" style="background: #fff3e0; color: #e65100;">
        {exp['subcategory']}
    </span>
    """, unsafe_allow_html=True)
    
    st.markdown(f"# {exp['title']}")
    st.write(exp['description'])
    
    col_info1, col_info2, col_info3 = st.columns(3)
    col_info1.metric("Διάρκεια", f"{exp['duration_min']} λεπτά")
    col_info2.metric("Δυσκολία", exp['difficulty'])
    col_info3.metric("Προβολές", exp['views_count'])
    
    st.markdown("---")
    
    # Main content columns
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Thumbnail
        if exp['thumbnail_url']:
            st.image(exp['thumbnail_url'], use_container_width=True)
        
        # Educational info
        if exp['learning_goals']:
            st.markdown("### 🎯 Μαθησιακοί Στόχοι")
            st.write(exp['learning_goals'])
        
        if exp['key_concepts']:
            st.markdown("### 🔑 Βασικές Έννοιες")
            st.write(exp['key_concepts'])
        
        if exp['discussion_questions']:
            st.markdown("### 💬 Ερωτήσεις Συζήτησης")
            # Format questions as bulleted list
            questions = exp['discussion_questions'].strip()
            if questions:
                # Split by newlines and format each line
                lines = [line.strip() for line in questions.split('\n') if line.strip()]
                for line in lines:
                    # Remove existing numbering if present (e.g., "1. " or "• ")
                    line = line.lstrip('0123456789.• ')
                    st.markdown(f"- {line}")
            else:
                st.write(exp['discussion_questions'])
        
        if exp['safety_notes']:
            st.markdown("### ⚠️ Σημειώσεις Ασφάλειας")
            st.info(exp['safety_notes'])
    
    with col_right:
        # QR Code
        st.markdown("### 📱 Σάρωσε για VR")
        qr_img = generate_qr_code(exp['youtube_url'])
        if qr_img:
            st.markdown(f"""
            <div class="qr-container">
                <img src="{qr_img}" style="width: 100%; max-width: 250px;">
                <p style="font-size: 0.85rem; margin-top: 0.5rem; color: #666;">
                    Σάρωσε με την κάμερα του smartphone σου
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Εγκατάσταση: `pip install qrcode[pil]`")
        
        # Direct link
        st.markdown("### 🔗 Άμεσο Link")
        st.code(exp['youtube_url'], language="text")
        
        st.markdown(f"[Άνοιγμα σε YouTube]({exp['youtube_url']})")
        
        # Favorite button
        st.markdown("---")
        is_fav = is_favorite(st.session_state.session_id, exp['id'])
        fav_text = "⭐ Αφαίρεση από Αγαπημένα" if is_fav else "☆ Προσθήκη στα Αγαπημένα"
        
        if st.button(fav_text, key="fav_detail", use_container_width=True, type="primary"):
            new_state = toggle_favorite(st.session_state.session_id, exp['id'])
            st.success("✓ Προστέθηκε!" if new_state else "✓ Αφαιρέθηκε!")
            st.rerun()


def favorites_page() -> None:
    """Favorites page."""
    st.markdown("## ⭐ Τα Αγαπημένα μου")
    
    favorites = get_favorites(st.session_state.session_id)
    
    if not favorites:
        st.info("Δεν έχεις προσθέσει ακόμα αγαπημένες εμπειρίες.")
        if st.button("📚 Εξερεύνησε τη Βιβλιοθήκη", type="primary"):
            st.session_state.current_view = 'library'
            st.rerun()
        return
    
    st.caption(f"Έχεις {len(favorites)} αγαπημένες εμπειρίες")
    st.markdown("---")
    
    for exp in favorites:
        render_experience_card(exp)
        st.markdown("---")


def help_page() -> None:
    """Help/Instructions page."""
    st.markdown("## ℹ️ Οδηγίες Χρήσης")
    
    st.markdown("""
    ### 📱 Πώς να χρησιμοποιήσεις τη VR Library
    
    #### Βήμα 1: Επίλεξε Εμπειρία
    - Περιηγήσου στη **Βιβλιοθήκη** και βρες κάτι που σε ενδιαφέρει
    - Χρησιμοποίησε φίλτρα (κατηγορία, δυσκολία) για γρηγορότερη αναζήτηση
    - Κάνε κλικ στο "Λεπτομέρειες" για περισσότερες πληροφορίες
    
    #### Βήμα 2: Σάρωσε το QR Code
    - Στη σελίδα λεπτομερειών, θα βρεις ένα **QR Code**
    - Ανοίξε την κάμερα του smartphone σου
    - Σάρωσε το QR code → θα ανοίξει αυτόματα το YouTube
    
    #### Βήμα 3: Φόρεσε το VR Headset
    - Τοποθέτησε το smartphone στο **VR headset case**
    - Φόρεσε το headset
    - Πάτησε Play στο video
    - Κίνησε το κεφάλι σου για να δεις γύρω σου!
    
    #### 💡 Συμβουλές
    - Χρησιμοποίησε **ακουστικά** για καλύτερη εμπειρία
    - Κάθισε σε σταθερό σημείο (καρέκλα, καναπές)
    - Κάνε διάλειμμα κάθε 15-20 λεπτά
    - Αν νιώσεις ζάλη, σταμάτα αμέσως
    
    ### 🎯 Κατηγορίες
    
    **Εκπαιδευτικό**: Μάθε για Φυσική, Ιστορία, Βιολογία, Χημεία
    - Ιδανικό για προετοιμασία μαθημάτων
    - Περιλαμβάνει ερωτήσεις συζήτησης
    
    **Χαλάρωση**: Φύση, Περιπέτειες, Χόμπι
    - Για διάλειμμα από το διάβασμα
    - Μείωση άγχους
    - Διασκέδαση
    
    ### ⚠️ Ασφάλεια
    
    - **Διάβασε πάντα** τις σημειώσεις ασφάλειας
    - **Μην** χρησιμοποιείς VR αν έχεις ακροφοβία (σε εμπειρίες ύψους)
    - **Μην** χρησιμοποιείς VR αν είσαι επιρρεπής σε επιληπτικές κρίσεις
    - **Σταμάτα** αν νιώσεις ναυτία, ζάλη, ή ανησυχία
    
    ### ❓ Συχνές Ερωτήσεις
    
    **Q: Χρειάζομαι ειδικό headset;**
    A: Όχι! Αρκεί ένα Google Cardboard-style case (κοστίζει 5-15€).
    
    **Q: Λειτουργεί σε όλα τα smartphones;**
    A: Ναι, αρκεί να έχει gyroscope (σχεδόν όλα τα σύγχρονα).
    
    **Q: Τι κάνω αν δεν δουλεύει το QR code;**
    A: Αντίγραψε το link και ανοίξτο στο YouTube app.
    
    **Q: Μπορώ να χρησιμοποιήσω ακουστικά Bluetooth;**
    A: Ναι! Θα βελτιώσει την εμπειρία.
    """)


def admin_page() -> None:
    """Admin panel."""
    st.markdown("## 🔧 Admin Panel")
    
    tab1, tab2 = st.tabs(["📊 Στατιστικά", "➕ Προσθήκη Εμπειρίας"])
    
    conn = get_db()
    
    with tab1:
        # Stats
        total_exp = conn.execute('SELECT COUNT(*) as c FROM experiences').fetchone()[0]
        total_edu = conn.execute(
            "SELECT COUNT(*) as c FROM experiences WHERE category = 'Εκπαιδευτικό'"
        ).fetchone()[0]
        total_rel = conn.execute(
            "SELECT COUNT(*) as c FROM experiences WHERE category = 'Χαλάρωση'"
        ).fetchone()[0]
        total_views = conn.execute('SELECT SUM(views_count) as s FROM experiences').fetchone()[0] or 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Σύνολο Εμπειριών", total_exp)
        col2.metric("Εκπαιδευτικά", total_edu)
        col3.metric("Χαλάρωση", total_rel)
        col4.metric("Συνολικές Προβολές", total_views)
        
        st.markdown("---")
        st.markdown("### 🔥 Top 10 Εμπειρίες")
        
        top_exp = conn.execute('''
            SELECT title, category, subcategory, views_count, duration_min
            FROM experiences
            ORDER BY views_count DESC
            LIMIT 10
        ''').fetchall()
        
        for idx, exp in enumerate(top_exp, 1):
            col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 1])
            col1.write(f"**#{idx}**")
            col2.write(exp[0])  # title
            col3.write(exp[1])  # category
            col4.write(exp[2])  # subcategory
            col5.write(f"{exp[3]} 👁️")  # views
    
    with tab2:
        st.markdown("### Προσθήκη Νέας Εμπειρίας")
        
        with st.form("add_experience"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Τίτλος*", placeholder="π.χ. Εξερεύνηση Αρχαίας Ρώμης")
                category = st.selectbox("Κατηγορία*", ["Εκπαιδευτικό", "Χαλάρωση"])
                subcategory = st.text_input(
                    "Υποκατηγορία*",
                    placeholder="π.χ. Ιστορία, Φύση, Περιπέτειες"
                )
                duration = st.number_input("Διάρκεια (λεπτά)*", min_value=1, value=15)
                difficulty = st.selectbox("Δυσκολία*", ["Εύκολο", "Μέτριο", "Δύσκολο"])
            
            with col2:
                youtube_url = st.text_input(
                    "YouTube URL*",
                    placeholder="https://www.youtube.com/watch?v=..."
                )
                thumbnail_url = st.text_input(
                    "Thumbnail URL (προαιρετικό)",
                    placeholder="https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg"
                )
            
            description = st.text_area("Περιγραφή*", placeholder="Σύντομη περιγραφή...")
            learning_goals = st.text_input("Μαθησιακοί Στόχοι", placeholder="Τι θα μάθουν;")
            key_concepts = st.text_input("Βασικές Έννοιες", placeholder="Κύριες έννοιες...")
            discussion_questions = st.text_area(
                "Ερωτήσεις Συζήτησης",
                placeholder="1. ...\n2. ...\n3. ..."
            )
            safety_notes = st.text_input("Σημειώσεις Ασφάλειας", placeholder="π.χ. Όχι για ακροφοβία")
            
            submitted = st.form_submit_button("✅ Προσθήκη Εμπειρίας", type="primary")
            
            if submitted:
                if not all([title, category, subcategory, youtube_url, description]):
                    st.error("Συμπλήρωσε όλα τα υποχρεωτικά πεδία (*)")
                else:
                    # Validate YouTube URL
                    is_valid_youtube = (
                        'youtube.com/watch?v=' in youtube_url or
                        'youtu.be/' in youtube_url or
                        'youtube.com/embed/' in youtube_url
                    )
                    
                    if not is_valid_youtube:
                        st.error("❌ Μη έγκυρο YouTube URL! Χρησιμοποίησε format:\n- youtube.com/watch?v=...\n- youtu.be/...")
                    else:
                        try:
                            conn.execute('''
                                INSERT INTO experiences
                                (title, description, category, subcategory, duration_min, difficulty,
                                 youtube_url, thumbnail_url, learning_goals, key_concepts,
                                 discussion_questions, safety_notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                title, description, category, subcategory, duration, difficulty,
                                youtube_url, thumbnail_url or None, learning_goals or None,
                                key_concepts or None, discussion_questions or None, safety_notes or None
                            ))
                            conn.commit()
                            st.success("✓ Η εμπειρία προστέθηκε επιτυχώς!")
                        except Exception as e:
                            st.error(f"Σφάλμα: {e}")
    
    conn.close()


# ============================================================================
# MAIN ROUTER
# ============================================================================

def main() -> None:
    """Main application router."""
    # Initialize DB
    init_db()
    
    # Render header
    render_header()
    
    # Navigation
    render_navigation()
    
    st.markdown("---")
    
    # Route to correct page
    if st.session_state.current_view == 'library':
        library_page()
    elif st.session_state.current_view == 'experience':
        experience_page()
    elif st.session_state.current_view == 'favorites':
        favorites_page()
    elif st.session_state.current_view == 'help':
        help_page()
    elif st.session_state.current_view == 'admin':
        admin_page()
    else:
        library_page()


if __name__ == "__main__":
    main()
