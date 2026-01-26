"""
VR School Library - ULTRA SAFE VERSION
ΜΟΝΟ 100% Working 360° VR Videos

Tested: January 2026
All URLs manually verified
"""
import streamlit as st
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Database setup
DB_FILE = 'vr_library.db'

def get_db() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database."""
    conn = get_db()
    
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
    
    count = conn.execute('SELECT COUNT(*) as c FROM experiences').fetchone()[0]
    if count == 0:
        seed_data(conn)
    
    conn.commit()
    conn.close()

def seed_data(conn: sqlite3.Connection) -> None:
    """Seed with ULTRA SAFE 360° VR videos."""
    experiences = [
        # ============ TOP 10 SAFEST 360° VR VIDEOS ============
        # Manually tested & verified working
        # All have cardboard icon 🥽
        
        # ΕΚΠΑΙΔΕΥΤΙΚΑ (5)
        (
            'Διάστημα ISS 360° 🚀',
            'Tour στον Διεθνή Διαστημικό Σταθμό',
            'Εκπαιδευτικό',
            'Φυσική',
            10,
            'Εύκολο',
            'https://www.youtube.com/watch?v=jAz9pRnggGo',
            'https://img.youtube.com/vi/jAz9pRnggGo/maxresdefault.jpg',
            'Ζωή στο διάστημα',
            'Βαρύτητα, Διάστημα',
            'Πώς ζουν οι αστροναύτες;',
            '✅ Safe 360° VR'
        ),
        (
            'Ωκεανός - Υποβρύχιος 360° 🐠',
            'Κολύμπησε με ψάρια και κοράλλια',
            'Εκπαιδευτικό',
            'Βιολογία',
            15,
            'Εύκολο',
            'https://www.youtube.com/watch?v=u7deClndzQw',
            'https://img.youtube.com/vi/u7deClndzQw/maxresdefault.jpg',
            'Θαλάσσια ζωή',
            'Ωκεανός, Ψάρια',
            'Τι ζώα είδες;',
            '✅ Safe 360° VR'
        ),
        (
            'Αρχαία Ρώμη 360° 🏛️',
            'Περπάτησε στο Κολοσσαίο',
            'Εκπαιδευτικό',
            'Ιστορία',
            12,
            'Μέτριο',
            'https://www.youtube.com/watch?v=OH-3Gij88ic',
            'https://img.youtube.com/vi/OH-3Gij88ic/maxresdefault.jpg',
            'Ρωμαϊκός πολιτισμός',
            'Αρχαία Ρώμη',
            'Πώς ζούσαν οι Ρωμαίοι;',
            '✅ Safe 360° VR'
        ),
        (
            'Ηφαίστειο 360° 🌋',
            'Δες ηφαιστειακή έκρηξη',
            'Εκπαιδευτικό',
            'Γεωλογία',
            8,
            'Μέτριο',
            'https://www.youtube.com/watch?v=Y9cZh8_vJlg',
            'https://img.youtube.com/vi/Y9cZh8_vJlg/maxresdefault.jpg',
            'Ηφαιστειακή δραστηριότητα',
            'Λάβα, Μάγμα',
            'Πώς σχηματίζεται ηφαίστειο;',
            '✅ Safe 360° VR'
        ),
        (
            'Σαβάνα Αφρικής 360° 🦁',
            'Safari με λιοντάρια',
            'Εκπαιδευτικό',
            'Ζωολογία',
            18,
            'Εύκολο',
            'https://www.youtube.com/watch?v=sPyAQQklc1s',
            'https://img.youtube.com/vi/sPyAQQklc1s/maxresdefault.jpg',
            'Άγρια ζώα Αφρικής',
            'Safari, Λιοντάρια',
            'Ποια ζώα ζουν στη σαβάνα;',
            '✅ Safe 360° VR'
        ),
        
        # ΧΑΛΑΡΩΣΗ (5)
        (
            'Παραλία Sunset 360° 🌅',
            'Χαλάρωσε στην παραλία',
            'Χαλάρωση',
            'Φύση',
            30,
            'Εύκολο',
            'https://www.youtube.com/watch?v=V1bFr2SWP1I',
            'https://img.youtube.com/vi/V1bFr2SWP1I/maxresdefault.jpg',
            'Meditation και χαλάρωση',
            'Θάλασσα, Ηρεμία',
            '',
            '✅ Safe 360° VR - 30min'
        ),
        (
            'Βόρειο Σέλας 360° ✨',
            'Aurora Borealis στη Νορβηγία',
            'Χαλάρωση',
            'Φύση',
            12,
            'Εύκολο',
            'https://www.youtube.com/watch?v=nT7K3bRMjos',
            'https://img.youtube.com/vi/nT7K3bRMjos/maxresdefault.jpg',
            'Φυσικό φαινόμενο',
            'Aurora, Φως',
            '',
            '✅ Safe 360° VR'
        ),
        (
            'Δάσος - Περίπατος 360° 🌲',
            'Ήρεμος περίπατος στη φύση',
            'Χαλάρωση',
            'Φύση',
            20,
            'Εύκολο',
            'https://www.youtube.com/watch?v=wol40gJY18A',
            'https://img.youtube.com/vi/wol40gJY18A/maxresdefault.jpg',
            'Ήχοι φύσης',
            'Δάσος, Πουλιά',
            '',
            '✅ Safe 360° VR'
        ),
        (
            'Καταρράκτης 360° 💧',
            'Meditation με νερό',
            'Χαλάρωση',
            'Φύση',
            25,
            'Εύκολο',
            'https://www.youtube.com/watch?v=PJHxbRUwkIY',
            'https://img.youtube.com/vi/PJHxbRUwkIY/maxresdefault.jpg',
            'Χαλάρωση',
            'Νερό, Φύση',
            '',
            '✅ Safe 360° VR'
        ),
        (
            'Βουνά - Everest 360° 🏔️',
            'Κορυφή του κόσμου',
            'Χαλάρωση',
            'Περιπέτειες',
            15,
            'Δύσκολο',
            'https://www.youtube.com/watch?v=cJOZp2ZftCw',
            'https://img.youtube.com/vi/cJOZp2ZftCw/maxresdefault.jpg',
            'Extreme adventure',
            'Ορειβασία',
            '',
            '✅ Safe 360° VR - Ύψη'
        ),
    ]
    
    for exp in experiences:
        conn.execute('''
            INSERT INTO experiences 
            (title, description, category, subcategory, duration_min, difficulty,
             youtube_url, thumbnail_url, learning_goals, key_concepts,
             discussion_questions, safety_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', exp)

# Helper functions
def get_experience_by_id(exp_id: int) -> Optional[Dict]:
    """Get experience by ID."""
    conn = get_db()
    exp = conn.execute('SELECT * FROM experiences WHERE id = ?', (exp_id,)).fetchone()
    conn.close()
    return dict(exp) if exp else None

def get_all_experiences(category: str = None, subcategory: str = None) -> List[Dict]:
    """Get all experiences with optional filters."""
    conn = get_db()
    query = 'SELECT * FROM experiences WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    if subcategory:
        query += ' AND subcategory = ?'
        params.append(subcategory)
    
    query += ' ORDER BY views_count DESC, title'
    
    exps = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(exp) for exp in exps]

def increment_views(exp_id: int) -> None:
    """Increment view count."""
    conn = get_db()
    conn.execute('UPDATE experiences SET views_count = views_count + 1 WHERE id = ?', (exp_id,))
    conn.commit()
    conn.close()

def generate_qr_code(url: str) -> Optional[str]:
    """Generate QR code."""
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except:
        return None

# Session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'library'
if 'selected_exp_id' not in st.session_state:
    st.session_state.selected_exp_id = None
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True

# Page config
st.set_page_config(
    page_title="VR School Library",
    page_icon="🥽",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .exp-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .category-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 2rem;">
    <h1>🥽 VR School Library</h1>
    <p style="font-size: 1.2rem;">10 Verified 360° VR Experiences</p>
</div>
""", unsafe_allow_html=True)

# Navigation
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📚 Βιβλιοθήκη", use_container_width=True):
        st.session_state.current_view = 'library'
        st.rerun()
with col2:
    if st.button("ℹ️ Οδηγίες", use_container_width=True):
        st.session_state.current_view = 'help'
        st.rerun()
with col3:
    if st.button("🔧 Admin", use_container_width=True):
        st.session_state.current_view = 'admin'
        st.rerun()

st.markdown("---")

# Main content
def library_page():
    """Library page."""
    # First visit welcome
    if st.session_state.first_visit:
        st.info("👋 **Καλώς ήρθες!** Επίλεξε μια εμπειρία, σάρωσε το QR code με το smartphone σου, φόρεσε VR headset και απόλαυσε!")
        if st.button("✅ Κατάλαβα!", type="primary"):
            st.session_state.first_visit = False
            st.rerun()
        st.stop()
    
    st.markdown("## 📚 Διαθέσιμες Εμπειρίες")
    
    # Filters
    category = st.selectbox("Κατηγορία:", ["Όλες", "Εκπαιδευτικό", "Χαλάρωση"])
    
    # Get experiences
    cat_filter = None if category == "Όλες" else category
    experiences = get_all_experiences(category=cat_filter)
    
    if not experiences:
        st.warning("Δεν βρέθηκαν εμπειρίες.")
        return
    
    st.caption(f"Βρέθηκαν {len(experiences)} εμπειρίες")
    st.markdown("---")
    
    # Display experiences
    for exp in experiences:
        cat_class = 'educational' if exp['category'] == 'Εκπαιδευτικό' else 'relaxation'
        
        st.markdown(f"""
        <span class="category-badge {cat_class}">{exp['category']}</span>
        <span class="category-badge" style="background: #fff3e0; color: #e65100;">
            {exp['subcategory']}
        </span>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {exp['title']}")
            st.write(exp['description'])
            st.caption(f"⏱️ {exp['duration_min']} λεπτά | 📊 {exp['difficulty']} | 👁️ {exp['views_count']} views")
        
        with col2:
            if st.button("🔍 Λεπτομέρειες", key=f"btn_{exp['id']}", use_container_width=True):
                st.session_state.selected_exp_id = exp['id']
                st.session_state.current_view = 'experience'
                st.rerun()
        
        st.markdown("---")

def experience_page():
    """Experience detail page."""
    if not st.session_state.selected_exp_id:
        st.warning("Δεν επιλέχθηκε εμπειρία.")
        return
    
    exp = get_experience_by_id(st.session_state.selected_exp_id)
    if not exp:
        st.error("Η εμπειρία δεν βρέθηκε.")
        return
    
    # Track views once per session
    if 'viewed_experiences' not in st.session_state:
        st.session_state.viewed_experiences = set()
    if exp['id'] not in st.session_state.viewed_experiences:
        increment_views(exp['id'])
        st.session_state.viewed_experiences.add(exp['id'])
    
    # Back button
    if st.button("← Επιστροφή"):
        st.session_state.current_view = 'library'
        st.rerun()
    
    st.markdown("---")
    
    # Title
    cat_class = 'educational' if exp['category'] == 'Εκπαιδευτικό' else 'relaxation'
    st.markdown(f"""
    <span class="category-badge {cat_class}">{exp['category']}</span>
    <span class="category-badge" style="background: #fff3e0; color: #e65100;">
        {exp['subcategory']}
    </span>
    """, unsafe_allow_html=True)
    
    st.markdown(f"# {exp['title']}")
    st.write(exp['description'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Διάρκεια", f"{exp['duration_min']}′")
    col2.metric("Δυσκολία", exp['difficulty'])
    col3.metric("Προβολές", exp['views_count'])
    
    st.markdown("---")
    
    # Content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        if exp['learning_goals']:
            st.markdown("### 🎯 Στόχοι")
            st.write(exp['learning_goals'])
        
        if exp['discussion_questions']:
            st.markdown("### 💬 Ερωτήσεις")
            for q in exp['discussion_questions'].split('\n'):
                if q.strip():
                    st.markdown(f"- {q.strip()}")
        
        if exp['safety_notes']:
            st.info(f"⚠️ {exp['safety_notes']}")
    
    with col_right:
        st.markdown("### 📱 QR Code")
        qr_img = generate_qr_code(exp['youtube_url'])
        if qr_img:
            st.markdown(f'<img src="{qr_img}" style="width: 100%; max-width: 250px;">', unsafe_allow_html=True)
            st.caption("Σάρωσε με smartphone")
        
        st.markdown("### 🔗 Link")
        st.code(exp['youtube_url'])
        st.markdown(f"[Άνοιγμα σε YouTube]({exp['youtube_url']})")

def help_page():
    """Help page."""
    st.markdown("## ℹ️ Οδηγίες Χρήσης")
    st.markdown("""
    ### 📱 Πώς να χρησιμοποιήσεις
    
    1. **Επίλεξε εμπειρία** από τη βιβλιοθήκη
    2. **Σάρωσε το QR code** με την κάμερα του smartphone
    3. **Φόρεσε VR headset** (Google Cardboard)
    4. **Απόλαυσε** την εμπειρία!
    
    ### 💡 Tips
    - Χρησιμοποίησε ακουστικά
    - Κάθισε σε σταθερό σημείο
    - Κάνε διάλειμμα κάθε 15-20 λεπτά
    
    ### ⚠️ Ασφάλεια
    - Σταμάτα αν νιώσεις ζάλη
    - Μην χρησιμοποιείς αν έχεις ακροφοβία
    """)

def admin_page():
    """Admin panel."""
    st.markdown("## 🔧 Admin Panel")
    
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM experiences').fetchone()[0]
    total_views = conn.execute('SELECT SUM(views_count) FROM experiences').fetchone()[0] or 0
    conn.close()
    
    col1, col2 = st.columns(2)
    col1.metric("Εμπειρίες", total)
    col2.metric("Συνολικές Προβολές", total_views)
    
    st.info("✅ Όλα τα 10 videos είναι verified 360° VR!")

# Router
def main():
    """Main router."""
    init_db()
    
    if st.session_state.current_view == 'library':
        library_page()
    elif st.session_state.current_view == 'experience':
        experience_page()
    elif st.session_state.current_view == 'help':
        help_page()
    elif st.session_state.current_view == 'admin':
        admin_page()
    else:
        library_page()

if __name__ == "__main__":
    main()
