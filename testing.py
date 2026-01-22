import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime       
import os
import io
from fpdf import FPDF

def convert_df_to_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    num_cols = len(df.columns)
    col_width = 275 / num_cols 
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(200, 220, 255) 
   
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    pdf.set_fill_color(255, 255, 255)
    
    for index, row in df.iterrows():
        row_height = 8
        for col in df.columns:
            data_str = str(row[col])
            pdf.cell(col_width, row_height, data_str, border=1)
        pdf.ln() 
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Laporan')
        workbook  = writer.book
        worksheet = writer.sheets['Laporan']
        border_format = workbook.add_format({
            'border': 1,       
            'align': 'left',   
            'valign': 'vcenter'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD', 
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max(), 
                len(str(col))                      
            ) + 3
            
            worksheet.set_column(i, i, max_len, border_format)
            
        (max_row, max_col) = df.shape
        worksheet.add_table(0, 0, max_row, max_col - 1, {
            'columns': [{'header': column} for column in df.columns],
            'style': 'Table Style Medium 9' 
        })
            
    return output.getvalue()

st.set_page_config(
    page_title="Sistem Manajemen Karyawan & Transaksi",
    layout="wide",
    initial_sidebar_state="expanded"
)
FILE_KARYAWAN = 'data_karyawan.csv'
FILE_TRANSAKSI = 'data_transaksi.csv'
# ==========================================
def check_login(username, password):
    """Verifikasi username dan password sederhana."""
    return username == "admin" and password == "admin123"

def convert_df_to_excel(df):
    """Mengubah DataFrame menjadi file Excel (bytes)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def convert_df_to_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=10)
    cols = df.columns
    for col in cols:
        pdf.cell(40, 10, str(col), border=1)
    pdf.ln()
    pdf.set_font("Arial", size=10)
    
    for index, row in df.iterrows():
        for col in cols:
            data_str = str(row[col])[:20] 
            pdf.cell(40, 10, data_str, border=1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

def load_data():
    if os.path.exists(FILE_KARYAWAN):
        df_karyawan = pd.read_csv(FILE_KARYAWAN)
        if 'Gaji' not in df_karyawan.columns:
            df_karyawan['Gaji'] = 0
            df_karyawan.to_csv(FILE_KARYAWAN, index=False)
    else:
        df_karyawan = pd.DataFrame({
            'Nama': ['Budi Santoso', 'Siti Aminah'],
            'Jabatan': ['Manager', 'Staff'],
            'Departemen': ['Operasional', 'Keuangan'],
            'Gaji': [15000000, 5000000]
        })
        df_karyawan.to_csv(FILE_KARYAWAN, index=False)

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
    df.to_csv(filename, index=False)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'karyawan' not in st.session_state:
    df_k, df_t = load_data()
    st.session_state['karyawan'] = df_k
    st.session_state['transaksi'] = df_t

if not st.session_state['logged_in']:
    st.title("🔒 Login Administrator")
    
    col_login1, col_login2, col_login3 = st.columns([1,2,1])
    
    with col_login2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if check_login(username, password):
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
else:

    st.sidebar.title("Navigasi Utama")
    st.sidebar.info("Login sebagai: Admin")
    
    menu = st.sidebar.radio("Pilih Menu:", ["Dashboard & Transaksi", "Manajemen Karyawan"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

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
                gaji = st.number_input("Gaji Pokok (Rp)", min_value=0, step=100000, format="%d")
                
                submit_karyawan = st.form_submit_button("Simpan Data")

                if submit_karyawan and nama and departemen:
                    new_data = pd.DataFrame({
                        'Nama': [nama], 
                        'Jabatan': [jabatan], 
                        'Departemen': [departemen],
                        'Gaji': [gaji]
                    })
                    st.session_state['karyawan'] = pd.concat([st.session_state['karyawan'], new_data], ignore_index=True)
                    save_data(st.session_state['karyawan'], FILE_KARYAWAN)
                    st.success("Karyawan berhasil ditambahkan!")
                    st.rerun()

        with col2:
            st.subheader("Daftar Karyawan")
            df_curr_karyawan = st.session_state['karyawan']
            df_curr_karyawan_display = df_curr_karyawan.copy()
            df_curr_karyawan_display.insert(0, "No", range(1, len(df_curr_karyawan_display) + 1))
            
            st.dataframe(
                df_curr_karyawan_display, 
                use_container_width=True,
                column_config={
                    "Gaji": st.column_config.NumberColumn("Gaji (Rp)", format="Rp %d")
                }
            )
            
            st.markdown("##### 📥 Unduh Data Karyawan")
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                excel_data = convert_df_to_excel(df_curr_karyawan)
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name='data_karyawan.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='dl_excel_karyawan'
                )
            
            with col_d2:
                try:
                    pdf_data = convert_df_to_pdf(df_curr_karyawan, "Laporan Data Karyawan")
                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name='data_karyawan.pdf',
                        mime='application/pdf',
                        key='dl_pdf_karyawan'
                    )
                except Exception as e:
                    st.error(f"Gagal generate PDF: {e}")

            if not df_curr_karyawan.empty:
                st.markdown("---")
                st.markdown("### Hapus Data")
                col_del1, col_del2 = st.columns([3, 1])
                with col_del1:
                    idx_to_delete = st.number_input("Nomor Urut Karyawan", min_value=1, max_value=len(df_curr_karyawan), step=1, key="del_karyawan")
                with col_del2:
                    st.write("") 
                    st.write("") 
                    if st.button("Hapus", key="btn_del_kar"):
                        st.session_state['karyawan'] = df_curr_karyawan.drop(idx_to_delete - 1).reset_index(drop=True)
                        save_data(st.session_state['karyawan'], FILE_KARYAWAN)
                        st.rerun()

    elif menu == "Dashboard & Transaksi":
        st.title("📊 Dashboard & Transaksi")
        
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

        st.subheader("Data Transaksi")
        col_search, col_action = st.columns([3, 2])
        with col_search:
            search_term = st.text_input("🔍 Cari transaksi...")
        
        df_trans = st.session_state['transaksi']
        
        if search_term:
            filtered_df = df_trans[df_trans['Keterangan'].astype(str).str.contains(search_term, case=False)]
        else:
            filtered_df = df_trans
            filtered_df_display = filtered_df.copy()
        filtered_df_display.insert(0, "No", range(1, len(filtered_df_display) + 1))

        st.dataframe(filtered_df_display, use_container_width=True)

        if not filtered_df.empty:
            st.markdown("##### 📥 Unduh Laporan Transaksi")
            col_dt1, col_dt2 = st.columns(2)
            
            with col_dt1:
                excel_trans = convert_df_to_excel(filtered_df)
                st.download_button(
                    label="Download Excel",
                    data=excel_trans,
                    file_name='laporan_transaksi.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='dl_excel_trans'
                )
            
            with col_dt2:
                try:
                    pdf_trans = convert_df_to_pdf(filtered_df, "Laporan Keuangan & Transaksi")
                    st.download_button(
                        label="Download PDF",
                        data=pdf_trans,
                        file_name='laporan_transaksi.pdf',
                        mime='application/pdf',
                        key='dl_pdf_trans'
                    )
                except Exception as e:
                    st.error(f"Gagal generate PDF: {e}")

        if not st.session_state['transaksi'].empty:
            st.markdown("---")
            with st.expander("🗑️ Hapus Transaksi"):
                st.warning("Hapus data berdasarkan NOMOR URUT.")
                col_del_t1, col_del_t2 = st.columns([3, 1])
                with col_del_t1:
                    max_no = len(st.session_state['transaksi'])
                    idx_trans_del = st.number_input(f"Nomor Urut (1 - {max_no})", min_value=1, max_value=max_no, step=1, key="input_del_trans")
                with col_del_t2:
                    st.write("") 
                    st.write("") 
                    if st.button("Hapus Data", key="btn_del_trans"):
                        st.session_state['transaksi'] = st.session_state['transaksi'].drop(idx_trans_del - 1).reset_index(drop=True)
                        save_data(st.session_state['transaksi'], FILE_TRANSAKSI)
                        st.success("Terhapus!")
                        st.rerun()

        st.markdown("---")

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
