"""
XR Portal - Streamlit Edition (Standalone)
Innovation with Care VR/AR

Ολοκληρωμένο αρχείο για GitHub - περιλαμβάνει ΟΛΑ σε ένα αρχείο.

Εκτέλεση:
    pip install streamlit
    streamlit run app.py

Demo Codes:
    TEACHER-DEMO2024
    STUDENT-DEMO2024
    GIFT-DEMO2024

Admin: http://localhost:8501/?admin=true
"""
import streamlit as st
import sqlite3
import secrets
from urllib.parse import quote
import os

# ============================================================================
# SEED DATA (Ενσωματωμένα)
# ============================================================================

DEMO_CODES = [
    ('TEACHER-DEMO2024', 'TEACHER'),
    ('STUDENT-DEMO2024', 'STUDENT'),
    ('GIFT-DEMO2024', 'GIFT'),
]

EXPERIENCES = [
    # TEACHER (10)
    ('teach01', 'ISS - Διαστημικός Σταθμός 360', 'Εξερεύνηση του Διεθνούς Διαστημικού Σταθμού', 'VR360', '10-16', 5, 
     'Φυσική, Διάστημα', 'Κατανόηση ζωής στο διάστημα', '1. Πώς λειτουργεί η βαρύτητα;\n2. Τι τρώνε οι αστροναύτες;\n3. Πώς κοιμούνται;',
     'Χωρίς έντονη κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT'),
    
    ('teach02', 'Ανθρώπινο Σώμα - Καρδιά VR', 'Εξερεύνηση καρδιάς και κυκλοφορικού', 'VR360', '12-16', 6,
     'Βιολογία, Ανατομία', 'Κατανόηση λειτουργίας καρδιάς', '1. Πόσες κοιλίες έχει;\n2. Πώς κυκλοφορεί το αίμα;\n3. Τι είναι οι βαλβίδες;',
     'Ήρεμη παρουσίαση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT'),
    
    ('teach03', 'Πυραμίδες Αιγύπτου AR', 'Αρχιτεκτονική και κατασκευή πυραμίδων', 'AR', '10-18', 7,
     'Ιστορία, Αρχαιολογία', 'Κατασκευή πυραμίδων', '1. Πώς κατασκευάστηκαν;\n2. Πόσο χρόνο πήρε;\n3. Τι ρόλο είχαν;',
     'Απαιτεί χώρο', 'Μέτριο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER'),
    
    ('teach04', 'Ηλιακό Σύστημα VR', 'Ταξίδι στους πλανήτες', 'VR360', '8-14', 6,
     'Φυσική, Αστρονομία', 'Γνωριμία με πλανήτες', '1. Ποιος είναι ο μεγαλύτερος;\n2. Πόσοι είναι;\n3. Γιατί ο Πλούτωνας δεν είναι πλανήτης;',
     'Αργή κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT,GIFT'),
    
    ('teach05', 'Φωτοσύνθεση AR', 'Πώς τα φυτά παράγουν οξυγόνο', 'AR', '10-14', 5,
     'Βιολογία, Φυτά', 'Κατανόηση φωτοσύνθεσης', '1. Τι χρειάζονται τα φυτά;\n2. Τι παράγουν;\n3. Γιατί είναι σημαντική;',
     'Στατική', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT'),
    
    ('teach06', 'Μεγάλο Τείχος Κίνας 360', 'Ιστορική περιήγηση', 'VR360', '12-18', 6,
     'Ιστορία', 'Ιστορία τείχους', '1. Πόσο μακρύ;\n2. Πότε χτίστηκε;\n3. Γιατί το έφτιαξαν;',
     'Ύψος - όχι ακροφοβία', 'Μέτριο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,GIFT'),
    
    ('teach07', 'Ηφαίστειο VR', 'Εσωτερικό Γης', 'VR360', '11-16', 7,
     'Γεωλογία', 'Ηφαιστειακή δραστηριότητα', '1. Τι είναι το μάγμα;\n2. Πώς εκρήγνυται;\n3. Τι στρώματα έχει η Γη;',
     'Έντονες εικόνες', 'Μέτριο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT'),
    
    ('teach08', 'DNA & Κύτταρο AR', 'Μέσα στο κύτταρο', 'AR', '14-18', 6,
     'Βιολογία, Γενετική', 'Δομή DNA', '1. Τι είναι το DNA;\n2. Πώς λειτουργεί το κύτταρο;\n3. Τι είναι χρωμοσώματα;',
     'Στατική 3D', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER'),
    
    ('teach09', 'Αρχαία Ολυμπία VR', 'Αναπαράσταση Ολυμπίας', 'VR360', '10-16', 7,
     'Ιστορία', 'Ολυμπιακοί Αγώνες', '1. Τι αγωνίσματα;\n2. Ποιοι συμμετείχαν;\n3. Γιατί σταμάτησαν;',
     'Ήρεμη περιήγηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT'),
    
    ('teach10', 'Κύκλος Νερού 360', 'Υδρολογικός κύκλος', 'VR360', '8-12', 5,
     'Γεωγραφία', 'Κύκλος νερού', '1. Πώς εξατμίζεται;\n2. Τι είναι τα σύννεφα;\n3. Πώς βρέχει;',
     'Χωρίς κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'TEACHER,STUDENT,GIFT'),
    
    # STUDENT (10)
    ('stud01', 'Υποβρύχιος Κόσμος VR', 'Βουτιά στον ωκεανό', 'VR360', '8-14', 7,
     'Βιολογία, Θαλάσσια Ζωή', 'Θαλάσσιοι οργανισμοί', '1. Ποια ζώα είδες;\n2. Σε τι βάθος;\n3. Τι τρώνε;',
     'Ήρεμη κολύμβηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud02', 'Δεινόσαυροι AR', 'Δεινόσαυροι ζωντανεύουν', 'AR', '7-13', 6,
     'Παλαιοντολογία', 'Εποχή δεινοσαύρων', '1. Πόσο μεγάλοι;\n2. Τι έτρωγαν;\n3. Πότε έζησαν;',
     'Χρειάζεται χώρος', 'Μέτριο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud03', 'Τροπικό Δάσος 360', 'Εξερεύνηση Αμαζονίου', 'VR360', '9-15', 6,
     'Βιολογία, Οικολογία', 'Βιοποικιλότητα', '1. Τι ζώα ζουν;\n2. Γιατί σημαντικό;\n3. Τι κίνδυνοι;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud04', 'Λούβρο VR', 'Εικονική περιήγηση', 'VR360', '12-18', 7,
     'Τέχνη, Ιστορία', 'Διάσημα έργα', '1. Ποιος έφτιαξε Μόνα Λίζα;\n2. Πόσο παλιά;\n3. Τι άλλο είδες;',
     'Στατική', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud05', 'Ανανεώσιμες Πηγές AR', 'Ηλιακά & ανεμογεννήτριες', 'AR', '11-16', 6,
     'Φυσική, Περιβάλλον', 'Ανανεώσιμες πηγές', '1. Πώς λειτουργούν ηλιακά;\n2. Τι είναι αιολική;\n3. Γιατί σημαντικές;',
     'Στατική', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT'),
    
    ('stud06', 'Αρχαία Ρώμη VR', 'Ταξίδι στην Ρώμη', 'VR360', '12-18', 7,
     'Ιστορία', 'Ρωμαϊκός πολιτισμός', '1. Πώς ζούσαν;\n2. Τι έτρωγαν;\n3. Πώς ντύνονταν;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud07', 'Μέλισσες AR', 'Ρόλος μελισσών', 'AR', '8-13', 5,
     'Βιολογία', 'Επικονίαση', '1. Τι είναι επικονίαση;\n2. Τι κάνουν μέλισσες;\n3. Γιατί σημαντικές;',
     'Χωρίς κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud08', 'Βόρειο Σέλας 360', 'Παρακολούθηση σέλας', 'VR360', '10-18', 6,
     'Φυσική', 'Φαινόμενο σέλας', '1. Πώς δημιουργείται;\n2. Πού βλέπουμε;\n3. Πότε εμφανίζεται;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud09', 'Μουσικά Όργανα AR', 'Πώς λειτουργούν όργανα', 'AR', '7-14', 6,
     'Μουσική', 'Παραγωγή ήχου', '1. Πώς βγαίνει ήχος;\n2. Τι είναι χορδές;\n3. Ποια σου άρεσαν;',
     'Στατική', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT,GIFT'),
    
    ('stud10', 'Μαγνητικό Πεδίο VR', 'Πεδίο Γης', 'VR360', '12-16', 6,
     'Φυσική', 'Μαγνητικό πεδίο', '1. Τι είναι;\n2. Πώς προστατεύει;\n3. Σχέση με πυξίδα;',
     'Χωρίς κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'STUDENT'),
    
    # GIFT (10)
    ('gift01', 'Ζώα Σαβάνας 360', 'Safari Αφρική', 'VR360', '6-14', 7,
     'Ζωολογία', 'Άγρια ζώα', '1. Ποια ζώα;\n2. Πού ζουν;\n3. Τι τρώνε;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift02', 'Πεταλούδες AR', 'Πεταλούδες σπίτι', 'AR', '5-12', 5,
     'Βιολογία', 'Μεταμόρφωση', '1. Πώς γίνεται πεταλούδα;\n2. Τι τρώει κάμπια;\n3. Πόσο ζει;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift03', 'Κάστρα VR', 'Μεσαιωνικό κάστρο', 'VR360', '8-15', 7,
     'Ιστορία', 'Μεσαιωνική ζωή', '1. Πώς ζούσαν;\n2. Τι έτρωγαν;\n3. Πώς ήταν κάστρα;',
     'Στατική', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift04', 'Πλανητάριο 360', 'Αστέρια & αστερισμοί', 'VR360', '7-18', 6,
     'Αστρονομία', 'Αστερισμοί', '1. Τι είναι;\n2. Πώς βρίσκουμε Πολική;\n3. Τι είναι Γαλαξίας;',
     'Χωρίς κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift05', 'Κήπος Φαντασίας AR', 'Μαγικός κήπος', 'AR', '5-11', 6,
     'Τέχνη', 'Δημιουργικότητα', '1. Τι έφτιαξες;\n2. Τι χρώματα;\n3. Τι άρεσε;',
     'Απαιτεί χώρο', 'Μέτριο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift06', 'Χριστουγεννιάτικο Χωριό VR', 'Χιονισμένο χωριό', 'VR360', '4-12', 6,
     'Πολιτισμός', 'Χριστούγεννα', '1. Τι είδες;\n2. Τι κάνουν;\n3. Τι άρεσε;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift07', 'Ζωολογικός Κήπος 360', 'Επίσκεψη zoo', 'VR360', '5-13', 7,
     'Ζωολογία', 'Ζώα όλου κόσμου', '1. Ποιο άρεσε;\n2. Από πού;\n3. Τι τρώνε;',
     'Χωρίς έντονη κίνηση', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift08', 'Παγοδρόμιο AR', 'Χόκεϊ σπίτι', 'AR', '8-16', 7,
     'Αθλητισμός', 'Χόκεϊ επί πάγου', '1. Πόσοι παίκτες;\n2. Ποιος στόχος;\n3. Τι εξοπλισμός;',
     'Χώρος για κίνηση', 'Έντονο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift09', 'Παραμύθι Δάσους VR', 'Διαδραστικό παραμύθι', 'VR360', '4-10', 6,
     'Λογοτεχνία', 'Αφηγηματική εμπειρία', '1. Τι έγινε;\n2. Ποιος ήρωας;\n3. Πώς τελείωσε;',
     'Ήρεμη', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
    
    ('gift10', 'Πειραματισμοί AR', 'Απλά πειράματα', 'AR', '9-14', 6,
     'Φυσική', 'Αρχές φυσικής', '1. Τι παρατήρησες;\n2. Πώς βαρύτητα;\n3. Τι άλλο;',
     'Στατικά', 'Ήρεμο', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'GIFT'),
]

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="XR Portal - Innovation with Care",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# DATABASE
# ============================================================================

DB_PATH = 'xr_portal.db'


def get_db():
    """Σύνδεση στη DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Δημιουργία πινάκων."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS access_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            package_type TEXT NOT NULL,
            expires_at TEXT,
            max_uses INTEGER DEFAULT -1,
            current_uses INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'VR360',
            age_range TEXT DEFAULT '8-14',
            duration_min INTEGER DEFAULT 5,
            subjects TEXT,
            learning_goal TEXT,
            questions TEXT,
            safety_note TEXT,
            motion_level TEXT DEFAULT 'Ήρεμο',
            target_url TEXT NOT NULL,
            package_types TEXT DEFAULT 'TEACHER,STUDENT,GIFT',
            opens_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS user_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            experience_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experience_id) REFERENCES experiences(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_codes ON access_codes(code);
        CREATE INDEX IF NOT EXISTS idx_short_code ON experiences(short_code);
        CREATE INDEX IF NOT EXISTS idx_favorites ON user_favorites(session_id);
    ''')
    conn.commit()
    conn.close()


def seed_data():
    """Seed με demo data."""
    conn = get_db()
    
    # Codes
    for code, pkg_type in DEMO_CODES:
        conn.execute(
            'INSERT OR IGNORE INTO access_codes (code, package_type) VALUES (?, ?)',
            (code, pkg_type)
        )
    
    # Experiences
    for exp in EXPERIENCES:
        conn.execute('''
            INSERT OR IGNORE INTO experiences 
            (short_code, title, description, type, age_range, duration_min, subjects, 
             learning_goal, questions, safety_note, motion_level, target_url, package_types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', exp)
    
    conn.commit()
    conn.close()


# ============================================================================
# SESSION STATE
# ============================================================================

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_in = False
    st.session_state.package_type = None
    st.session_state.access_code = None
    st.session_state.session_id = secrets.token_hex(16)
    st.session_state.current_page = 'landing'
    st.session_state.selected_experience = None
    
    # Initialize DB
    if not os.path.exists(DB_PATH):
        init_db()
        seed_data()


# ============================================================================
# CSS
# ============================================================================

st.markdown("""
<style>
    .main {padding: 2rem;}
    .stButton>button {
        width: 100%;
        background: #4F46E5;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {background: #3730A3;}
    .motion-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .motion-hremo {background: #D1FAE5; color: #065F46;}
    .motion-metrio {background: #FEF3C7; color: #92400E;}
    .motion-entono {background: #FEE2E2; color: #991B1B;}
    .hero {text-align: center; padding: 3rem 0;}
    .hero h1 {font-size: 3rem; margin-bottom: 0.5rem;}
    .tagline {font-size: 1.5rem; color: #4F46E5; font-weight: 600;}
    .package-badge {background: #10B981; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# PAGES
# ============================================================================

def landing_page():
    """Landing page."""
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown("# 🌐 XR Portal")
    st.markdown('<p class="tagline">Innovation with Care VR/AR</p>', unsafe_allow_html=True)
    st.markdown("**Ασφαλείς, εκπαιδευτικές εμπειρίες AR/VR για μάθηση**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👨‍🏫 Για Εκπαιδευτικούς")
        st.write("Έτοιμα σενάρια μαθήματος 3-7 λεπτών")
    
    with col2:
        st.markdown("### 🎓 Για Μαθητές")
        st.write("Αποστολές & διεύρυνση ενδιαφερόντων")
    
    with col3:
        st.markdown("### 🎁 Για Οικογένειες")
        st.write("Premium δώρα με ασφαλείς εμπειρίες")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Είσοδος με Κωδικό", type="primary", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()


def login_page():
    """Login page."""
    st.markdown("# 🔐 Είσοδος")
    st.write("Βάλτε τον κωδικό πρόσβασής σας")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        code_input = st.text_input(
            "Κωδικός Πρόσβασης",
            placeholder="π.χ. TEACHER-DEMO2024",
            key="login_code"
        ).upper()
        
        if st.button("Είσοδος", type="primary", use_container_width=True):
            if code_input:
                conn = get_db()
                access_code = conn.execute(
                    'SELECT * FROM access_codes WHERE code = ? AND status = "active"',
                    (code_input,)
                ).fetchone()
                conn.close()
                
                if access_code:
                    st.session_state.logged_in = True
                    st.session_state.package_type = access_code['package_type']
                    st.session_state.access_code = code_input
                    st.session_state.current_page = 'library'
                    st.success(f"✓ Καλωσήρθες στο {access_code['package_type']} Package!")
                    st.rerun()
                else:
                    st.error("❌ Μη έγκυρος κωδικός")
            else:
                st.warning("Παρακαλώ βάλε κωδικό")
        
        st.markdown("---")
        st.info("""
        **Demo κωδικοί:**
        - `TEACHER-DEMO2024`
        - `STUDENT-DEMO2024`
        - `GIFT-DEMO2024`
        """)
        
        if st.button("← Πίσω στην αρχική"):
            st.session_state.current_page = 'landing'
            st.rerun()


def library_page():
    """Library page."""
    package_type = st.session_state.package_type
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# 📚 Βιβλιοθήκη")
        st.markdown(f'<span class="package-badge">{package_type} Package</span>', unsafe_allow_html=True)
    
    with col2:
        if st.button("⭐ My Library"):
            st.session_state.current_page = 'my_library'
            st.rerun()
        if st.button("🚪 Έξοδος"):
            st.session_state.logged_in = False
            st.session_state.current_page = 'landing'
            st.rerun()
    
    st.markdown("---")
    
    conn = get_db()
    experiences = conn.execute('''
        SELECT * FROM experiences 
        WHERE package_types LIKE ?
        ORDER BY created_at DESC
    ''', (f'%{package_type}%',)).fetchall()
    conn.close()
    
    if not experiences:
        st.info("Δεν υπάρχουν διαθέσιμες εμπειρίες για αυτό το πακέτο.")
        return
    
    cols_per_row = 3
    for i in range(0, len(experiences), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(experiences):
                exp = experiences[idx]
                
                with col:
                    with st.container():
                        st.markdown(f"**{exp['type']}**")
                        st.markdown(f"### {exp['title']}")
                        st.write(exp['description'])
                        st.caption(f"🎯 {exp['age_range']} | ⏱️ {exp['duration_min']} λεπτά")
                        
                        motion_class = exp['motion_level'].lower().replace('ή', 'h').replace('έ', 'e')
                        st.markdown(
                            f'<span class="motion-badge motion-{motion_class}">'
                            f'{exp["motion_level"]}</span>',
                            unsafe_allow_html=True
                        )
                        
                        st.caption(exp['subjects'])
                        
                        if st.button("Άνοιγμα →", key=f"open_{exp['id']}", use_container_width=True):
                            st.session_state.selected_experience = exp['id']
                            st.session_state.current_page = 'experience'
                            st.rerun()


def experience_page():
    """Experience detail page."""
    exp_id = st.session_state.selected_experience
    
    conn = get_db()
    exp = conn.execute('SELECT * FROM experiences WHERE id = ?', (exp_id,)).fetchone()
    
    if not exp:
        st.error("Experience not found")
        return
    
    session_id = st.session_state.session_id
    is_favorite = conn.execute(
        'SELECT 1 FROM user_favorites WHERE session_id = ? AND experience_id = ?',
        (session_id, exp_id)
    ).fetchone() is not None
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"# {exp['title']}")
        st.markdown(f"**{exp['type']}** | {exp['age_range']}")
    
    with col2:
        fav_label = "★ Αφαίρεση" if is_favorite else "☆ Αποθήκευση"
        if st.button(fav_label, use_container_width=True):
            if is_favorite:
                conn.execute(
                    'DELETE FROM user_favorites WHERE session_id = ? AND experience_id = ?',
                    (session_id, exp_id)
                )
            else:
                conn.execute(
                    'INSERT INTO user_favorites (session_id, experience_id) VALUES (?, ?)',
                    (session_id, exp_id)
                )
            conn.commit()
            st.rerun()
    
    if st.button("← Πίσω στη βιβλιοθήκη"):
        st.session_state.current_page = 'library'
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(exp['description'])
        
        st.markdown("### 📋 Πληροφορίες")
        
        info_cols = st.columns(4)
        with info_cols[0]:
            st.metric("Ηλικίες", exp['age_range'])
        with info_cols[1]:
            st.metric("Διάρκεια", f"{exp['duration_min']} λεπτά")
        with info_cols[2]:
            st.metric("Μαθήματα", exp['subjects'].split(',')[0])
        with info_cols[3]:
            motion_class = exp['motion_level'].lower().replace('ή', 'h').replace('έ', 'e')
            st.markdown(
                f'<div style="text-align: center;">'
                f'<span class="motion-badge motion-{motion_class}">'
                f'{exp["motion_level"]}</span></div>',
                unsafe_allow_html=True
            )
        
        if exp['learning_goal']:
            st.info(f"**🎯 Στόχος Μάθησης:** {exp['learning_goal']}")
        
        if exp['safety_note']:
            st.warning(f"**⚠️ Σημείωση:** {exp['safety_note']}")
    
    with col2:
        st.markdown("### 📱 Τρόποι Πρόσβασης")
        
        short_url = f"http://localhost:8501/go/{exp['short_code']}"
        
        if st.button("🚀 Έναρξη Εμπειρίας", type="primary", use_container_width=True):
            conn.execute('UPDATE experiences SET opens_count = opens_count + 1 WHERE id = ?', (exp_id,))
            conn.commit()
            
            if exp['questions']:
                st.session_state.show_mission = True
        
        st.markdown("---")
        st.markdown("### 📲 QR Code")
        st.caption("Σκανάρισμα από άλλη συσκευή")
        
        qr_url = f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={quote(short_url)}"
        st.image(qr_url, width=200)
        st.caption(short_url)
    
    conn.close()
    
    if exp['questions'] and st.session_state.get('show_mission', False):
        with st.expander("🎯 Τι κρατάω από αυτή την εμπειρία;", expanded=True):
            st.markdown(exp['questions'].replace('\n', '\n\n'))
            if st.button("Κατάλαβα!", use_container_width=True):
                st.session_state.show_mission = False
                st.markdown(f'<meta http-equiv="refresh" content="0; url={exp["target_url"]}">', unsafe_allow_html=True)
                st.rerun()


def my_library_page():
    """My Library page."""
    st.markdown("# ⭐ My Library")
    st.write("Τα αγαπημένα σου")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Βιβλιοθήκη"):
            st.session_state.current_page = 'library'
            st.rerun()
    
    st.markdown("---")
    
    session_id = st.session_state.session_id
    
    conn = get_db()
    favorites = conn.execute('''
        SELECT e.* FROM experiences e
        JOIN user_favorites f ON e.id = f.experience_id
        WHERE f.session_id = ?
        ORDER BY f.created_at DESC
    ''', (session_id,)).fetchall()
    conn.close()
    
    if not favorites:
        st.info("Δεν έχεις προσθέσει ακόμα αγαπημένα.")
        if st.button("📚 Εξερεύνησε τη Βιβλιοθήκη", type="primary"):
            st.session_state.current_page = 'library'
            st.rerun()
        return
    
    cols_per_row = 3
    for i in range(0, len(favorites), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(favorites):
                exp = favorites[idx]
                
                with col:
                    st.markdown(f"**{exp['type']}**")
                    st.markdown(f"### {exp['title']}")
                    st.write(exp['description'])
                    st.caption(f"🎯 {exp['age_range']} | ⏱️ {exp['duration_min']} λεπτά")
                    
                    if st.button("Άνοιγμα →", key=f"fav_{exp['id']}", use_container_width=True):
                        st.session_state.selected_experience = exp['id']
                        st.session_state.current_page = 'experience'
                        st.rerun()


def admin_page():
    """Admin panel."""
    st.markdown("# 🔧 Admin Panel")
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Προσθήκη", "🔑 Κωδικοί"])
    
    conn = get_db()
    
    with tab1:
        total_exp = conn.execute('SELECT COUNT(*) as c FROM experiences').fetchone()['c']
        total_codes = conn.execute('SELECT COUNT(*) as c FROM access_codes').fetchone()['c']
        total_opens = conn.execute('SELECT SUM(opens_count) as s FROM experiences').fetchone()['s'] or 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Εμπειρίες", total_exp)
        col2.metric("Κωδικοί", total_codes)
        col3.metric("Opens", total_opens)
        
        st.markdown("---")
        st.markdown("### 🔥 Top Εμπειρίες")
        
        top_exp = conn.execute('''
            SELECT title, type, opens_count 
            FROM experiences 
            ORDER BY opens_count DESC 
            LIMIT 10
        ''').fetchall()
        
        for exp in top_exp:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(exp['title'])
            col2.write(exp['type'])
            col3.write(f"{exp['opens_count']} opens")
    
    with tab2:
        st.markdown("### Προσθήκη Εμπειρίας")
        
        with st.form("add_experience"):
            col1, col2 = st.columns(2)
            
            with col1:
                short_code = st.text_input("Short Code*", placeholder="space01")
                title = st.text_input("Τίτλος*")
                exp_type = st.selectbox("Τύπος", ["VR360", "AR", "Video360"])
                age_range = st.text_input("Ηλικίες", value="8-14")
                duration = st.number_input("Διάρκεια (λεπτά)", value=5, min_value=1)
            
            with col2:
                subjects = st.text_input("Μαθήματα")
                motion_level = st.selectbox("Motion Level", ["Ήρεμο", "Μέτριο", "Έντονο"])
                target_url = st.text_input("Target URL*")
                packages = st.multiselect("Πακέτα", ["TEACHER", "STUDENT", "GIFT"], default=["TEACHER", "STUDENT", "GIFT"])
            
            description = st.text_area("Περιγραφή")
            learning_goal = st.text_input("Στόχος Μάθησης")
            questions = st.text_area("Ερωτήσεις (3)", placeholder="1. ...\n2. ...\n3. ...")
            safety_note = st.text_input("Σημείωση Ασφάλειας")
            
            if st.form_submit_button("✅ Προσθήκη", type="primary"):
                if short_code and title and target_url:
                    try:
                        conn.execute('''
                            INSERT INTO experiences 
                            (short_code, title, description, type, age_range, duration_min, 
                             subjects, learning_goal, questions, safety_note, motion_level, 
                             target_url, package_types)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            short_code, title, description, exp_type, age_range, duration,
                            subjects, learning_goal, questions, safety_note, motion_level,
                            target_url, ','.join(packages)
                        ))
                        conn.commit()
                        st.success("✓ Εμπειρία προστέθηκε!")
                    except Exception as e:
                        st.error(f"Σφάλμα: {e}")
                else:
                    st.error("Συμπλήρωσε τα απαραίτητα πεδία (*)")
    
    with tab3:
        st.markdown("### Δημιουργία Κωδικού")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            package_type = st.selectbox("Package Type", ["TEACHER", "STUDENT", "GIFT"])
        with col2:
            if st.button("Generate Code", type="primary", use_container_width=True):
                code = f"{package_type}-{secrets.token_hex(4).upper()}"
                conn.execute('INSERT INTO access_codes (code, package_type) VALUES (?, ?)', (code, package_type))
                conn.commit()
                st.success(f"✓ Δημιουργήθηκε: `{code}`")
        
        st.markdown("---")
        st.markdown("### Πρόσφατοι Κωδικοί")
        
        codes = conn.execute('SELECT * FROM access_codes ORDER BY created_at DESC LIMIT 20').fetchall()
        
        for code in codes:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.code(code['code'])
            col2.write(code['package_type'])
            col3.write(code['status'])
    
    conn.close()


# ============================================================================
# ROUTER
# ============================================================================

def main():
    """Main app router."""
    
    query_params = st.query_params
    if 'admin' in query_params:
        admin_page()
        return
    
    if not st.session_state.logged_in:
        if st.session_state.current_page == 'login':
            login_page()
        else:
            landing_page()
    else:
        if st.session_state.current_page == 'library':
            library_page()
        elif st.session_state.current_page == 'experience':
            experience_page()
        elif st.session_state.current_page == 'my_library':
            my_library_page()
        else:
            library_page()


if __name__ == "__main__":
    main()
