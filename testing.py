import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Sistem Manajemen Karyawan & Transaksi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KONFIGURASI FILE PENYIMPANAN ---
FILE_KARYAWAN = 'data_karyawan.csv'
FILE_TRANSAKSI = 'data_transaksi.csv'

# --- FUNGSI LOAD & SAVE DATA ---
def load_data():
    """Memuat data dari CSV dan menangani perubahan struktur kolom."""
    
    # 1. Load Data Karyawan
    if os.path.exists(FILE_KARYAWAN):
        df_karyawan = pd.read_csv(FILE_KARYAWAN)
        # Cek apakah kolom 'Gaji' sudah ada (untuk handle data lama)
        if 'Gaji' not in df_karyawan.columns:
            df_karyawan['Gaji'] = 0 # Isi default 0 untuk data lama
            df_karyawan.to_csv(FILE_KARYAWAN, index=False) # Update struktur file
    else:
        # Data awal dummy
        df_karyawan = pd.DataFrame({
            'Nama': ['Budi Santoso', 'Siti Aminah'],
            'Jabatan': ['Manager', 'Staff'],
            'Departemen': ['Operasional', 'Keuangan'],
            'Gaji': [15000000, 5000000]
        })
        df_karyawan.to_csv(FILE_KARYAWAN, index=False)

    # 2. Load Data Transaksi
    if os.path.exists(FILE_TRANSAKSI):
        df_transaksi = pd.read_csv(FILE_TRANSAKSI)
    else:
        df_transaksi = pd.DataFrame({
            'Tanggal': [datetime.now().date()],
            'Keterangan': ['Saldo Awal'],
            'Kategori': ['Modal'],
            'Jumlah': [10000000],
            'Tipe': ['Pemasukan']
        })
        df_transaksi.to_csv(FILE_TRANSAKSI, index=False)
    
    return df_karyawan, df_transaksi

def save_data(df, filename):
    """Menyimpan dataframe ke file CSV."""
    df.to_csv(filename, index=False)

# --- INISIALISASI SESSION STATE ---
if 'karyawan' not in st.session_state:
    df_k, df_t = load_data()
    st.session_state['karyawan'] = df_k
    st.session_state['transaksi'] = df_t

# --- Sidebar Navigasi ---
st.sidebar.title("Navigasi Utama")
menu = st.sidebar.radio("Pilih Menu:", ["Dashboard & Transaksi", "Manajemen Karyawan"])

# --- FUNGSI 1: MANAJEMEN KARYAWAN ---
if menu == "Manajemen Karyawan":
    st.title("👥 Pengelolaan Data Karyawan")
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Tambah Karyawan Baru")
        with st.form("form_karyawan"):
            nama = st.text_input("Nama Lengkap")
            jabatan = st.selectbox("Jabatan", ["Manager", "Supervisor", "Staff", "Intern", "IT Support"])
            departemen = st.text_input("Departemen")
            # --- TAMBAHAN INPUT GAJI ---
            gaji = st.number_input("Gaji Pokok (Rp)", min_value=0, step=100000, format="%d")
            
            submit_karyawan = st.form_submit_button("Simpan Data")

            if submit_karyawan and nama and departemen:
                new_data = pd.DataFrame({
                    'Nama': [nama], 
                    'Jabatan': [jabatan], 
                    'Departemen': [departemen],
                    'Gaji': [gaji] # Simpan Gaji
                })
                st.session_state['karyawan'] = pd.concat([st.session_state['karyawan'], new_data], ignore_index=True)
                save_data(st.session_state['karyawan'], FILE_KARYAWAN)
                st.success("Karyawan berhasil ditambahkan!")
                st.rerun()

    with col2:
        st.subheader("Daftar Karyawan")
        
        # Tampilkan DataFrame
        # Kita format tampilan angka gajinya agar tidak ada koma yang aneh, tapi tetap angka
        st.dataframe(
            st.session_state['karyawan'], 
            use_container_width=True,
            column_config={
                "Gaji": st.column_config.NumberColumn(
                    "Gaji (Rp)",
                    format="Rp %d" # Format tampilan mata uang
                )
            }
        )
        
        # Fitur Hapus Karyawan
        if not st.session_state['karyawan'].empty:
            st.markdown("### Hapus Data")
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                idx_to_delete = st.number_input("Index Karyawan", min_value=0, max_value=len(st.session_state['karyawan'])-1, step=1, key="del_karyawan")
            with col_del2:
                st.write("") 
                st.write("") 
                if st.button("Hapus", key="btn_del_kar"):
                    st.session_state['karyawan'] = st.session_state['karyawan'].drop(idx_to_delete).reset_index(drop=True)
                    save_data(st.session_state['karyawan'], FILE_KARYAWAN)
                    st.rerun()

# --- FUNGSI 2: DASHBOARD & TRANSAKSI ---
elif menu == "Dashboard & Transaksi":
    st.title("📊 Dashboard & Transaksi")
    
    # 1. Form Input
    with st.expander("➕ Tambah Transaksi Baru", expanded=False):
        with st.form("form_transaksi"):
            col_a, col_b = st.columns(2)
            with col_a:
                tgl = st.date_input("Tanggal", datetime.now())
                ket = st.text_input("Keterangan")
            with col_b:
                kategori = st.selectbox("Kategori", ["Operasional", "Gaji Karyawan", "Pemasaran", "Infrastruktur", "Penjualan", "Modal"])
                jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=10000)
                tipe = st.radio("Tipe", ["Pemasukan", "Pengeluaran"])
            
            submit_transaksi = st.form_submit_button("Simpan Transaksi")
            
            if submit_transaksi:
                new_trans = pd.DataFrame({
                    'Tanggal': [tgl], 'Keterangan': [ket], 'Kategori': [kategori], 
                    'Jumlah': [jumlah], 'Tipe': [tipe]
                })
                st.session_state['transaksi'] = pd.concat([st.session_state['transaksi'], new_trans], ignore_index=True)
                save_data(st.session_state['transaksi'], FILE_TRANSAKSI)
                st.success("Transaksi berhasil disimpan!")
                st.rerun()

    st.markdown("---")

    # 2. Pencarian & Tabel
    st.subheader("Data Transaksi")
    col_search, col_action = st.columns([3, 2])
    with col_search:
        search_term = st.text_input("🔍 Cari transaksi...")
    
    df_trans = st.session_state['transaksi']
    
    if search_term:
        filtered_df = df_trans[df_trans['Keterangan'].astype(str).str.contains(search_term, case=False)]
    else:
        filtered_df = df_trans

    st.dataframe(filtered_df, use_container_width=True)

    # Hapus Transaksi
    if not st.session_state['transaksi'].empty:
        with st.expander("🗑️ Hapus Transaksi"):
            st.warning("Hapus data berdasarkan INDEX.")
            col_del_t1, col_del_t2 = st.columns([3, 1])
            with col_del_t1:
                max_idx = len(st.session_state['transaksi']) - 1
                idx_trans_del = st.number_input(f"Index (0 - {max_idx})", min_value=0, max_value=max_idx, step=1, key="input_del_trans")
            with col_del_t2:
                st.write("") 
                st.write("") 
                if st.button("Hapus Data", key="btn_del_trans"):
                    st.session_state['transaksi'] = st.session_state['transaksi'].drop(idx_trans_del).reset_index(drop=True)
                    save_data(st.session_state['transaksi'], FILE_TRANSAKSI)
                    st.success("Terhapus!")
                    st.rerun()

    st.markdown("---")

    # 3. Grafik
    st.subheader("Analisis Grafik")
    if not filtered_df.empty:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_bar = px.bar(filtered_df, x='Kategori', y='Jumlah', color='Tipe', 
                             title="Transaksi per Kategori", barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_chart2:
            fig_pie = px.pie(filtered_df, values='Jumlah', names='Tipe', 
                             title="Pemasukan vs Pengeluaran", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)