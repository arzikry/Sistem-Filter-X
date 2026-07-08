# =========================================================
# SISTEM FILTER X
# GUI 3 DOMAIN FILTERING
# =========================================================

from tkinter import (
    Tk,
    Canvas,
    Text,
    Button,
    Scrollbar,
    simpledialog,
    messagebox,
    END
)

import sqlite3
import re

from datetime import datetime

# ======================================================
# DATABASE SQLITE
# ======================================================
DB_NAME = "blocked_domains.db"

def connect_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blocked_domains (
        Domain_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Domain_Name TEXT UNIQUE,
        Last_Update TEXT
    )
    """)

    conn.commit()

    return conn

# ======================================================
# PATH FILE HOSTS WINDOWS
# ======================================================
def get_hosts_path():
    return r"C:\Windows\System32\drivers\etc\hosts"

# ======================================================
# VALIDASI DOMAIN
# ======================================================
def is_valid_domain(domain):

    pattern = r"^(?!-)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"

    return re.match(pattern, domain) is not None

# ======================================================
# LOG OUTPUT KE GUI
# ======================================================
def log_message(message):

    entry_1.insert(END, f"{message}\n")
    entry_1.see(END)

# ======================================================
# LOAD SEMUA DOMAIN
# ======================================================
def load_blocked_sites():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Domain_Name
    FROM blocked_domains
    ORDER BY Domain_ID ASC
    """)

    sites = [row[0] for row in cursor.fetchall()]

    conn.close()

    return sites

# ======================================================
# UPDATE HOSTS FILE
# ======================================================
def update_hosts_file():

    hosts_path = get_hosts_path()

    blocked_sites = load_blocked_sites()

    try:

        with open(hosts_path, "r") as file:
            lines = file.readlines()

        # Hapus semua entri domain yang pernah diblokir
        cleaned_lines = []

        for line in lines:

            if line.startswith("127.0.0.1"):

                continue

            cleaned_lines.append(line)

        with open(hosts_path, "w") as file:

            file.writelines(cleaned_lines)

            for site in blocked_sites:

                file.write(f"127.0.0.1 {site}\n")
                file.write(f"127.0.0.1 www.{site}\n")

    except PermissionError:

        log_message("")
        log_message("[ERROR] Jalankan Program Sebagai Administrator.")

# ======================================================
# ENABLE FILTERING
# ======================================================
def enable_filtering():

    try:

        hosts_path = get_hosts_path()

        blocked_sites = load_blocked_sites()

        with open(hosts_path, "r") as file:
            lines = file.readlines()

        with open(hosts_path, "w") as file:

            # Hapus entri lama
            for line in lines:
                if not any(site in line for site in blocked_sites):
                    file.write(line)

            # Tambahkan entri baru
            for site in blocked_sites:
                file.write(f"127.0.0.1 {site}\n")
                file.write(f"127.0.0.1 www.{site}\n")

        log_message("")
        log_message("[SUCCESS] Filtering Berhasil Diaktifkan.")
        log_message("[SUCCESS] File Hosts Berhasil Diperbarui.")

    except PermissionError:

        log_message("")
        log_message("[ERROR] Jalankan Program Sebagai Administrator.")

    except Exception as e:

        log_message("")
        log_message(f"[ERROR] {e}")

# ======================================================
# ADD DOMAIN
# ======================================================
def add_domain():

    site = simpledialog.askstring(
        "Add Domain",
        "     Masukkan Domain Yang Ingin Diblokir:     "
    )

    if not site:
        return

    site = site.strip().lower()

    if site.startswith("www."):
        site = site[4:]

    if not is_valid_domain(site):

        messagebox.showerror(
            "Invalid Domain",
            "Format Domain Tidak Valid.\n\nContoh:\nyoutube.com"
        )

        return

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO blocked_domains
        (Domain_Name, Last_Update)
        VALUES (?, ?)
        """, (
            site,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()

        log_message("")
        log_message(f"[+] {site} Berhasil Ditambahkan.")

    except sqlite3.IntegrityError:

        messagebox.showinfo(
            "Add Domain",
            "Maaf, Domain Yang Anda Tambahkan,\n"
            "Sudah Ada Di Database.\n\n"
            "Silahkan Input Domain / Situs Yang Lainnya."
        )

    conn.close()

# ======================================================
# DELETE DOMAIN
# ======================================================
def delete_domain():

    site = simpledialog.askstring(
        "Delete Domain",
        "     Masukkan Domain Yang Ingin Dihapus:     "
    )

    if not site:
        return

    site = site.strip().lower()

    if site.startswith("www."):
        site = site[4:]

    conn = connect_db()
    cursor = conn.cursor()

    # Cek apakah domain ada
    cursor.execute("""
    SELECT Domain_ID
    FROM blocked_domains
    WHERE Domain_Name = ?
    """, (site,))

    result = cursor.fetchone()

    # Jika domain tidak ditemukan
    if result is None:

        conn.close()

        messagebox.showwarning(
            "Domain Tidak Ditemukan",
            "Maaf, Domain Yang Anda Inputkan,\n"
            "Tidak Terdaftar Di Database."
        )

        return

    # Jika domain ditemukan
    cursor.execute("""
    DELETE FROM blocked_domains
    WHERE Domain_Name = ?
    """, (site,))

    conn.commit()
    conn.close()

    update_hosts_file()

    log_message("")
    log_message(f"[-] {site} Berhasil Dihapus.")

# ======================================================
# CEK STATUS FILTERING
# ======================================================
def get_filtering_status():

    hosts_path = get_hosts_path()

    blocked_sites = load_blocked_sites()

    try:

        with open(hosts_path, "r") as file:
            content = file.read()

        # Jika tidak ada domain dalam database
        if not blocked_sites:
            return "INACTIVE"

        # Cek apakah semua domain ada di hosts
        for site in blocked_sites:

            if f"127.0.0.1 {site}" not in content:
                return "INACTIVE"

        return "ACTIVE"

    except Exception:
        return "UNKNOWN"

# ======================================================
# VIEW DOMAIN LIST
# ======================================================
def view_domains():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Domain_ID,
           Domain_Name,
           Last_Update
    FROM blocked_domains
    ORDER BY Domain_ID ASC
    """)

    rows = cursor.fetchall()

    total_domain = len(rows)

    filtering_status = get_filtering_status()

    cursor.execute("""
    SELECT Last_Update
    FROM blocked_domains
    ORDER BY Last_Update DESC
    LIMIT 1
    """)

    last_update_row = cursor.fetchone()

    if last_update_row:
        last_update = last_update_row[0]
    else:
        last_update = "-"

    # Hitung total domain
    total_domain = len(rows)

    # Ambil Last Update terbaru
    cursor.execute("""
    SELECT Last_Update
    FROM blocked_domains
    ORDER BY Last_Update DESC
    LIMIT 1
    """)

    last_update_row = cursor.fetchone()

    if last_update_row:
        last_update = last_update_row[0]
    else:
        last_update = "-"

    conn.close()

    entry_1.delete("1.0", END)

    if rows:

        log_message("========== DOMAIN FILTERING STATUS ==========")
        log_message("")

        log_message(f"Filtering Status : {filtering_status}")
        log_message(f"Total Domain     : {total_domain}")
        log_message(f"Last Update      : {last_update}")

        log_message("")
        log_message("========== DAFTAR DOMAIN ==========")

        for row in rows:

            log_message("")
            log_message(f"ID           : {row[0]}")
            log_message(f"Domain       : {row[1]}")
            log_message(f"Last Update  : {row[2]}")

    else:

        log_message("")
        log_message("Tidak Ada Domain Yang Diblokir.")

# ======================================================
# FORMAT LIST
# ======================================================
def format_list():

    confirm = messagebox.askyesno(
        "Format List (Domain)",
        "Tindakan Ini Akan Menghapus\nSemua Daftar Domain Yang Telah Ditambahkan.\n\nKlik YES Jika Yakin."
    )

    if not confirm:

        log_message("")
        log_message("[INFO] Format List Dibatalkan.")

        return


    conn = connect_db()
    cursor = conn.cursor()


    # Hapus semua data domain
    cursor.execute("""
    DELETE FROM blocked_domains
    """)


    # Reset ID AUTOINCREMENT SQLite
    cursor.execute("""
    DELETE FROM sqlite_sequence
    WHERE name='blocked_domains'
    """)


    conn.commit()
    conn.close()


    update_hosts_file()


    log_message("")
    log_message("[SUCCESS] Semua Domain Berhasil Dihapus.")
    log_message("[SUCCESS] ID Domain Berhasil Direset.")

# ======================================================
# DISABLE FILTERING
# ======================================================
def disable_filtering():

    confirm = messagebox.askyesno(
        "Disable Filtering",
        "Apakah Anda Yakin Ingin Menonaktifkan Filtering?"
    )

    if not confirm:
        return

    hosts_path = get_hosts_path()

    blocked_sites = load_blocked_sites()

    try:

        with open(hosts_path, "r") as file:
            lines = file.readlines()

        with open(hosts_path, "w") as file:

            for line in lines:

                remove_line = False

                for site in blocked_sites:

                    if (
                        f"127.0.0.1 {site}" in line
                        or
                        f"127.0.0.1 www.{site}" in line
                    ):
                        remove_line = True
                        break

                if not remove_line:
                    file.write(line)

        log_message("")
        log_message("[SUCCESS] Filtering Berhasil Dinonaktifkan.")
        log_message("[SUCCESS] Seluruh Entri Hosts Berhasil Dibersihkan.")

    except PermissionError:

        log_message("")
        log_message("[ERROR] Jalankan Program Sebagai Administrator.")

    except Exception as e:

        log_message("")
        log_message(f"[ERROR] {e}")

# ======================================================
# BACK MENU
# ======================================================
def back_menu():

    log_message("")
    log_message("[INFO] Kembali Ke Halaman Sebelumnya.")

    window.destroy()

# ======================================================
# GUI WINDOW
# ======================================================
window = Tk()

window.title("Domain Filtering")

window.geometry("1000x600")
window.configure(bg="#1E74F6")

# ======================================================
# CANVAS
# ======================================================
canvas = Canvas(
    window,
    bg="#1E74F6",
    height=600,
    width=1000,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)

# ======================================================
# PANEL KANAN
# ======================================================
canvas.create_rectangle(
    500.0,
    0.0,
    1000.0,
    600.0,
    fill="#00A17C",
    outline=""
)

# ======================================================
# TITLE
# ======================================================
canvas.create_text(
    44.0,
    29.0,
    anchor="nw",
    text="DOMAIN FILTERING",
    fill="#FFFFFF",
    font=("Segoe UI", 28, "bold")
)

canvas.create_text(
    44.0,
    90.0,
    anchor="nw",
    text="( Choose Option )",
    fill="#FFFFFF",
    font=("Segoe UI", 16)
)

canvas.create_text(
    530.0,
    39.0,
    anchor="nw",
    text="( Input / Output Text )",
    fill="#FFFFFF",
    font=("Segoe UI", 16)
)

# ======================================================
# STYLE BUTTON
# ======================================================
BUTTON_FONT = ("Segoe UI", 11, "bold")

BUTTON_STYLE = {
    "font": BUTTON_FONT,
    "bg": "#FFFFFF",
    "fg": "#1E74F6",
    "activebackground": "#D9D9D9",
    "activeforeground": "#1E74F6",
    "relief": "flat",
    "bd": 0,
    "cursor": "hand2"
}

# ======================================================
# BUTTON ADD DOMAIN
# ======================================================
button_1 = Button(
    window,
    text="Add Domain",
    command=add_domain,
    **BUTTON_STYLE
)

button_1.place(
    x=147,
    y=176,
    width=210,
    height=50
)

# ======================================================
# BUTTON DELETE DOMAIN
# ======================================================
button_2 = Button(
    window,
    text="Delete Domain",
    command=delete_domain,
    **BUTTON_STYLE
)

button_2.place(
    x=147,
    y=257,
    width=210,
    height=50
)

# ======================================================
# BUTTON DOMAIN LIST
# ======================================================
button_3 = Button(
    window,
    text="Domain List",
    command=view_domains,
    **BUTTON_STYLE
)

button_3.place(
    x=147,
    y=338,
    width=210,
    height=50
)

# ======================================================
# BUTTON FORMAT LIST
# ======================================================
button_4 = Button(
    window,
    text="Format List",
    command=format_list,
    **BUTTON_STYLE
)

button_4.place(
    x=147,
    y=419,
    width=210,
    height=50
)

# ======================================================
# BUTTON BACK
# ======================================================
button_5 = Button(
    window,
    text="Back",
    command=back_menu,
    **BUTTON_STYLE
)

button_5.place(
    x=147,
    y=500,
    width=210,
    height=50
)

# ======================================================
# BUTTON ENABLE FILTERING
# ======================================================
button_6 = Button(
    window,
    text="Enable Filtering",
    command=enable_filtering,
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
    fg="#00A17C",
    activebackground="#D9D9D9",
    activeforeground="#00A17C",
    relief="flat",
    bd=0,
    cursor="hand2"
)

button_6.place(
    x=645,
    y=500,
    width=210,
    height=50
)

# ======================================================
# BUTTON DISABLE FILTERING
# ======================================================
button_7 = Button(
    window,
    text="Disable Filtering",
    command=disable_filtering,
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
    fg="#D9534F",
    activebackground="#D9D9D9",
    activeforeground="#D9534F",
    relief="flat",
    bd=0,
    cursor="hand2"
)

button_7.place(
    x=645,
    y=430,
    width=210,
    height=50
)

# ======================================================
# TEXT OUTPUT AREA
# ======================================================

# TEXT BOX
entry_1 = Text(
    window,
    bd=0,
    bg="#D9D9D9",
    fg="#000000",
    font=("Consolas", 10),
    highlightthickness=0,
    yscrollcommand=lambda *args: scrollbar.set(*args)
)

entry_1.place(
    x=530,
    y=86,
    width=430,
    height=330
)

# SCROLLBAR
scrollbar = Scrollbar(
    window,
    command=entry_1.yview
)

scrollbar.place(
    x=960,
    y=86,
    width=20,
    height=330
)

# HUBUNGKAN SCROLLBAR DENGAN TEXT
entry_1.config(yscrollcommand=scrollbar.set)

# ======================================================
# START PROGRAM
# ======================================================

log_message("======================================")
log_message("DOMAIN FILTERING SYSTEM")
log_message("======================================")
log_message("")
log_message("Program Berhasil Dijalankan.")
log_message("Silakan Pilih Menu Yang Tersedia.")

# ======================================================
# WINDOW
# ======================================================
window.resizable(False, False)
window.mainloop()