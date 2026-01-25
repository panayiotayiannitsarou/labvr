import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 🔐 AUTHENTICATION & SCHOOL CODES
# ═══════════════════════════════════════════════════════════

# SUPER ADMIN PASSWORD (ΕΣΥ - για να δίνεις κωδικούς)
SUPER_ADMIN_PASSWORD = "YIANNITSAROUPAN"

# SCHOOL CODES (ΕΣΥ δίνεις αυτούς τους κωδικούς στους εκπαιδευτικούς)
SCHOOL_CODES = {
    "TALIOTIS2025": "Λύκειο Γιαννάκη Ταλιώτη, Πάφος",
    "NEOFYTOU2025": "Λύκειο Αγίου Νεοφύτου, Πάφος",
    "KYKKOU2025": "Λύκειο Κύκκου, Πάφος",
    "MAKARIOU2025": "Λύκειο Α' Εθνάρχη Μακαρίου Γ', Πάφος",
    "EMPAS2025": "Λύκειο Εμπάς, Πάφος",
    # Άλλες πόλεις
    "FYLAXIS2025": "Λύκειο Αγίας Φυλάξεως, Λεμεσός",
    "ARXAGEL2025": "Γυμνάσιο Αρχαγγέλου, Λευκωσία",
}

# ═══════════════════════════════════════════════════════════
# 💾 PERSISTENT DATA STORAGE (JSON file)
# ═══════════════════════════════════════════════════════════

DATA_FILE = "schools_data.json"

def load_data():
    """Φόρτωση δεδομένων από JSON αρχείο"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"⚠️ Σφάλμα φόρτωσης δεδομένων: {e}")
            return {}
    return {}

def save_data(data):
    """Αποθήκευση δεδομένων σε JSON αρχείο"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"⚠️ Σφάλμα αποθήκευσης: {e}")
        return False

def init_session_state():
    """Αρχικοποίηση session state"""
    if 'schools_data' not in st.session_state:
        st.session_state.schools_data = load_data()
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.current_school = None
        st.session_state.is_super_admin = False

def calculate_allocation(total_revenue, target):
    """
    Υπολογίζει κατανομή χρημάτων με βάση τον αλγόριθμο:
    - 50% Μονάδα, 50% VR
    - ΑΛΛΑ αν 50% > στόχος, τότε:
      - Μονάδα παίρνει μέχρι τον στόχο
      - Υπόλοιπο όλο σε VR
    """
    half_revenue = total_revenue * 0.5
    
    if half_revenue <= target:
        # Normal split: 50-50
        monada = half_revenue
        vr = half_revenue
    else:
        # Target reached! Μονάδα gets target, rest goes to VR
        monada = target
        vr = total_revenue - target
    
    return {
        'monada': round(monada, 2),
        'vr': round(vr, 2),
        'target_reached': half_revenue >= target
    }

# ═══════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="VR Inclusion Lab - Διαχείριση & Διαφάνεια",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-box {
        background: #10B981;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    .warning-box {
        background: #F59E0B;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
init_session_state()

# ═══════════════════════════════════════════════════════════
# 🔐 AUTHENTICATION SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🔐 Είσοδος Εκπαιδευτικού")
    
    if not st.session_state.authenticated:
        # LOGIN FORM
        school_code = st.text_input("Κωδικός Σχολείου:", type="password", key="login_code")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Είσοδος", use_container_width=True):
                if school_code in SCHOOL_CODES:
                    st.session_state.authenticated = True
                    st.session_state.current_school = SCHOOL_CODES[school_code]
                    st.session_state.is_super_admin = False
                    st.rerun()
                elif school_code == SUPER_ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_super_admin = True
                    st.success("Super Admin Login!")
                    st.rerun()
                else:
                    st.error("❌ Λάθος κωδικός!")
        
        with col2:
            if st.button("Δημόσια Προβολή", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()
        
        st.markdown("---")
        st.info("""
        **Για Εκπαιδευτικούς:**  
        Χρησιμοποιήστε τον κωδικό που σας δόθηκε.
        
        **Για Επισκέπτες:**  
        Πατήστε "Δημόσια Προβολή".
        """)
    
    else:
        # LOGGED IN
        if st.session_state.is_super_admin:
            st.success("🔑 Super Admin")
            st.markdown("### 📊 Όλα τα Σχολεία")
            for school in st.session_state.schools_data.keys():
                st.write(f"• {school}")
        else:
            st.success(f"✅ Συνδεθήκατε")
            st.info(f"**Σχολείο:**  \n{st.session_state.current_school}")
        
        if st.button("Αποσύνδεση", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_school = None
            st.session_state.is_super_admin = False
            st.rerun()
        
        st.markdown("---")

# ═══════════════════════════════════════════════════════════
# 📊 MAIN CONTENT
# ═══════════════════════════════════════════════════════════

st.markdown('<h1 class="main-header">🏫 VR Inclusion Lab - Πλατφόρμα Διαφάνειας</h1>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# MODE 1: ΕΚΠΑΙΔΕΥΤΙΚΟΣ (School Admin) - EDIT MODE
# ═══════════════════════════════════════════════════════════

if st.session_state.authenticated and not st.session_state.is_super_admin:
    school_name = st.session_state.current_school
    
    # Initialize school data if new
    if school_name not in st.session_state.schools_data:
        st.session_state.schools_data[school_name] = {
            "target": 100,
            "transactions": [],
            "last_update": datetime.now().strftime('%Y-%m-%d')
        }
    
    school_data = st.session_state.schools_data[school_name]
    
    st.markdown(f"## 🎯 Διαχείριση: {school_name}")
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════
    # SETTINGS SECTION
    # ═══════════════════════════════════════════════════════════
    
    with st.expander("⚙️ Ρυθμίσεις Σχολείου", expanded=False):
        new_target = st.number_input(
            "Στόχος για Ειδική Μονάδα (€):",
            min_value=0,
            value=school_data['target'],
            step=10,
            help="Όταν η Μονάδα φτάσει αυτόν τον στόχο, όλα τα επιπλέον πάνε σε VR"
        )
        
        if st.button("💾 Αποθήκευση Στόχου"):
            st.session_state.schools_data[school_name]['target'] = new_target
            if save_data(st.session_state.schools_data):
                st.success(f"✅ Στόχος ενημερώθηκε σε {new_target}€")
            else:
                st.error("❌ Σφάλμα αποθήκευσης!")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════
    # ADD TRANSACTION
    # ═══════════════════════════════════════════════════════════
    
    st.markdown("### 💰 Καταχώριση Νέας Είσπραξης")
    
    # Initialize form reset trigger
    if f'reset_form_{school_name}' not in st.session_state:
        st.session_state[f'reset_form_{school_name}'] = 0
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        new_source = st.text_input(
            "Πηγή εσόδου:",
            placeholder="π.χ. Συνεισφορές, Workshop, Sponsor",
            key=f'source_{school_name}_{st.session_state[f"reset_form_{school_name}"]}'
        )
    
    with col2:
        new_amount = st.number_input(
            "Ποσό (€):",
            min_value=0,
            step=1,
            key=f'amount_{school_name}_{st.session_state[f"reset_form_{school_name}"]}'
        )
    
    with col3:
        new_date = st.date_input(
            "Ημερομηνία:",
            value=datetime.now(),
            key=f'date_{school_name}_{st.session_state[f"reset_form_{school_name}"]}'
        )
    
    if st.button("➕ Προσθήκη Είσπραξης", type="primary", use_container_width=True):
        if new_amount > 0 and new_source.strip():
            st.session_state.schools_data[school_name]['transactions'].append({
                'date': new_date.strftime('%Y-%m-%d'),
                'amount': new_amount,
                'source': new_source
            })
            st.session_state.schools_data[school_name]['last_update'] = datetime.now().strftime('%Y-%m-%d')
            
            # Save to file
            if save_data(st.session_state.schools_data):
                # Increment reset counter to create new widget keys (this clears the form)
                st.session_state[f'reset_form_{school_name}'] += 1
                
                st.success(f"✅ Προστέθηκε: {new_amount}€ από {new_source}")
                st.rerun()
            else:
                st.error("❌ Σφάλμα αποθήκευσης!")
        else:
            st.error("⚠️ Συμπληρώστε ποσό και πηγή!")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════
    # CALCULATIONS & DASHBOARD
    # ═══════════════════════════════════════════════════════════
    
    # Calculate totals
    total_revenue = sum(t['amount'] for t in school_data['transactions'])
    allocation = calculate_allocation(total_revenue, school_data['target'])
    
    # Metrics
    st.markdown("### 📊 Οικονομική Κατάσταση")
    
    if allocation['target_reached']:
        # Target reached - show total revenue and VR equipment
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("💰 Σύνολο Εσόδων", f"{total_revenue}€")
        
        with col2:
            st.metric("🥽 VR Εξοπλισμός", f"{allocation['vr']}€")
    else:
        # Target not reached - show full breakdown
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Σύνολο Εσόδων", f"{total_revenue}€")
        
        with col2:
            st.metric("❤️ Ειδική Μονάδα", f"{allocation['monada']:.2f}€", 
                      delta=f"Στόχος: {school_data['target']}€")
        
        with col3:
            st.metric("🥽 VR Εξοπλισμός", f"{allocation['vr']:.2f}€")
        
        with col4:
            progress_pct = min((allocation['monada'] / school_data['target']) * 100, 100)
            st.metric("📈 Πρόοδος Στόχου", f"{progress_pct:.0f}%")
    
    # Target status
    if allocation['target_reached']:
        st.balloons()  # 🎈 Animation!
        st.markdown('<div class="success-box">🎉 ΣΤΟΧΟΣ ΕΠΙΤΕΥΧΘΗΚΕ! Όλα τα νέα έσοδα πάνε σε VR εξοπλισμό!</div>', unsafe_allow_html=True)
    else:
        remaining = school_data['target'] - allocation['monada']
        st.markdown(f'<div class="warning-box">📊 Υπολείπονται {remaining:.2f}€ για τον στόχο της Μονάδας</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Allocation breakdown - only show if target NOT reached
    if not allocation['target_reached']:
        st.markdown("#### 📊 Κατανομή Χρημάτων")
        
        fig_pie = px.pie(
            values=[allocation['monada'], allocation['vr']],
            names=['Ειδική Μονάδα', 'VR Εξοπλισμός'],
            color_discrete_sequence=['#10B981', '#3B82F6'],
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Percentages
        monada_pct = (allocation['monada'] / total_revenue * 100) if total_revenue > 0 else 0
        vr_pct = (allocation['vr'] / total_revenue * 100) if total_revenue > 0 else 0
        
        st.write(f"• Ειδική Μονάδα: **{allocation['monada']:.2f}€** ({monada_pct:.1f}%)")
        st.write(f"• VR Εξοπλισμός: **{allocation['vr']:.2f}€** ({vr_pct:.1f}%)")
        
        st.markdown("---")
    
    # Full transaction history
    st.markdown("### 📋 Πλήρες Ιστορικό Συναλλαγών")
    
    if school_data['transactions']:
        df_full = pd.DataFrame(school_data['transactions'])
        df_full['date'] = pd.to_datetime(df_full['date'])
        df_full = df_full.sort_values('date', ascending=False)
        df_full['date'] = df_full['date'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            df_full[['date', 'source', 'amount']].rename(columns={
                'date': 'Ημερομηνία',
                'source': 'Πηγή',
                'amount': 'Ποσό (€)'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Download CSV
        csv = df_full.to_csv(index=False).encode('utf-8-sig')  # utf-8-sig for proper Greek characters
        
        st.download_button(
            "📥 Λήψη CSV",
            csv,
            f"{school_name}_transactions.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("Δεν υπάρχουν συναλλαγές")

# ═══════════════════════════════════════════════════════════
# MODE 2: SUPER ADMIN - Όλα τα σχολεία
# ═══════════════════════════════════════════════════════════

elif st.session_state.authenticated and st.session_state.is_super_admin:
    st.markdown("## 🔑 Super Admin Dashboard")
    st.markdown("### 📊 Επισκόπηση Όλων των Σχολείων")
    
    for school_name, data in st.session_state.schools_data.items():
        with st.expander(f"🏫 {school_name}", expanded=False):
            total = sum(t['amount'] for t in data['transactions'])
            alloc = calculate_allocation(total, data['target'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Έσοδα", f"{total:.2f}€")
            with col2:
                st.metric("Μονάδα", f"{alloc['monada']:.2f}€")
            with col3:
                st.metric("VR", f"{alloc['vr']:.2f}€")
            
            st.caption(f"Στόχος: {data['target']}€ | Τελευταία ενημέρωση: {data['last_update']}")

# ═══════════════════════════════════════════════════════════
# MODE 3: ΔΗΜΟΣΙΑ ΠΡΟΒΟΛΗ (Public View - Read Only)
# ═══════════════════════════════════════════════════════════

else:
    st.markdown("## 👁️ Δημόσια Προβολή - Επιλέξτε Σχολείο")
    
    if len(st.session_state.schools_data) == 0:
        st.info("Δεν υπάρχουν διαθέσιμα σχολεία ακόμα.")
    else:
        selected_school = st.selectbox(
            "Επιλέξτε σχολείο για προβολή:",
            options=list(st.session_state.schools_data.keys())
        )
        
        if selected_school:
            school_data = st.session_state.schools_data[selected_school]
            
            st.markdown(f"### 🏫 {selected_school}")
            st.caption(f"Τελευταία ενημέρωση: {datetime.strptime(school_data['last_update'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
            st.markdown("---")
            
            # Calculations
            total_revenue = sum(t['amount'] for t in school_data['transactions'])
            allocation = calculate_allocation(total_revenue, school_data['target'])
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 Σύνολο Εσόδων", f"{total_revenue:.2f}€")
            
            with col2:
                st.metric("❤️ Ειδική Μονάδα", f"{allocation['monada']:.2f}€")
            
            with col3:
                st.metric("🥽 VR Εξοπλισμός", f"{allocation['vr']:.2f}€")
            
            # Progress section only
            st.markdown("#### 🎯 Στόχος Μονάδας")
            st.progress(min(allocation['monada'] / school_data['target'], 1.0))
            st.write(f"**{allocation['monada']:.2f}€** από **{school_data['target']}€**")
            
            if allocation['target_reached']:
                st.success("✅ Στόχος επιτεύχθηκε!")
            else:
                remaining = school_data['target'] - allocation['monada']
                st.info(f"Υπολείπονται: {remaining:.2f}€")

# ═══════════════════════════════════════════════════════════
# 📌 FOOTER
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 1rem;'>
    <p style='margin: 0;'>💯 100% Διαφάνεια - Κάθε ευρώ καταγράφεται</p>
    <p style='margin: 0; font-size: 0.9rem;'>VR Inclusion Lab © 2025</p>
</div>
""", unsafe_allow_html=True)