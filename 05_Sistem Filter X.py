# =========================================================
# SISTEM FILTER X (INTEGRASI TOTAL GUI 1 - GUI 4)
# =========================================================

import os
import sys
import time
import shutil
import sqlite3
import threading
import subprocess
import re
import ctypes
from pathlib import Path
from datetime import datetime

from tkinter import *
from tkinter import ttk, messagebox, simpledialog, filedialog

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

import keyboard
import pyperclip
import win32gui

# =========================================================
# KONFIGURASI PATH & GLOBAL CONSTANTS
# =========================================================

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets")
IMAGE_REFS = []

VALID_USERNAME = "zrandi"
VALID_PASSWORD = "skripsi2026"

# Database Names
DB_DOMAIN = "blocked_domains.db"

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
DATABASE_NAME = os.path.join(BASE_DIR, "keyword_filter.db")

# Internet Control Configuration
NETWORK_INTERFACE_NAMES = ["Wi-Fi", "Ethernet"]
internet_disabled = False
cached_keywords = []

# Global Widget References
entry_username = None
entry_password = None
entry_1 = None          # Domain Filtering Output Area
output_text = None      # Keyword Filtering Output Area
output_path_entry = None # Keyword Export Path Entry


# =========================================================
# FUNGSI UTILITAS & UI UMUM
# =========================================================

def relative_to_assets(path: str) -> Path:
    # Jika program berjalan sebagai file .exe hasil kompilasi PyInstaller
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    # Jika program berjalan sebagai script .py biasa (saat development)
    else:
        base_path = Path(__file__).parent
        
    return base_path / "assets" / Path(path)


def load_photo_image(path: str):
    try:
        image = PhotoImage(file=path)
    except Exception:
        if Image is None or ImageTk is None:
            raise
        image = ImageTk.PhotoImage(Image.open(path))
    IMAGE_REFS.append(image)
    return image


def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def center_window(window, width, height):
    window.update_idletasks()
    x = int((window.winfo_screenwidth() - width) / 2)
    y = int((window.winfo_screenheight() - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def clear_window():
    """Membersihkan seluruh widget di window sebelum memuat halaman baru"""
    for widget in root.winfo_children():
        widget.destroy()


# =========================================================
# LOGIKA & DATABASE: DOMAIN FILTERING (GUI 3)
# =========================================================

def connect_domain_db():
    conn = sqlite3.connect(DB_DOMAIN)
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


def get_hosts_path():
    return r"C:\Windows\System32\drivers\etc\hosts"


def is_valid_domain(domain):
    pattern = r"^(?!-)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, domain) is not None


def log_message(message):
    if entry_1 and entry_1.winfo_exists():
        entry_1.insert(END, f"{message}\n")
        entry_1.see(END)


def load_blocked_sites():
    conn = connect_domain_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Domain_Name FROM blocked_domains ORDER BY Domain_ID ASC")
    sites = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sites


def update_hosts_file():
    hosts_path = get_hosts_path()
    blocked_sites = load_blocked_sites()
    try:
        with open(hosts_path, "r") as file:
            lines = file.readlines()

        cleaned_lines = [line for line in lines if not line.startswith("127.0.0.1")]

        with open(hosts_path, "w") as file:
            file.writelines(cleaned_lines)
            for site in blocked_sites:
                file.write(f"127.0.0.1 {site}\n")
                file.write(f"127.0.0.1 www.{site}\n")
    except PermissionError:
        log_message("\n[ERROR] Jalankan Program Sebagai Administrator.")


def enable_filtering():
    try:
        hosts_path = get_hosts_path()
        blocked_sites = load_blocked_sites()

        with open(hosts_path, "r") as file:
            lines = file.readlines()

        with open(hosts_path, "w") as file:
            for line in lines:
                if not any(site in line for site in blocked_sites):
                    file.write(line)
            for site in blocked_sites:
                file.write(f"127.0.0.1 {site}\n")
                file.write(f"127.0.0.1 www.{site}\n")

        log_message("\n[SUCCESS] Filtering Berhasil Diaktifkan.")
        log_message("[SUCCESS] File Hosts Berhasil Diperbarui.")
    except PermissionError:
        log_message("\n[ERROR] Jalankan Program Sebagai Administrator.")
    except Exception as e:
        log_message(f"\n[ERROR] {e}")


def add_domain():
    site = simpledialog.askstring("Add Domain", "     Masukkan Domain Yang Ingin Diblokir:     ")
    if not site:
        return
    site = site.strip().lower()
    if site.startswith("www."):
        site = site[4:]

    if not is_valid_domain(site):
        messagebox.showerror("Invalid Domain", "Format Domain Tidak Valid.\n\nContoh:\nyoutube.com")
        return

    conn = connect_domain_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO blocked_domains (Domain_Name, Last_Update)
        VALUES (?, ?)
        """, (site, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        log_message(f"\n[+] {site} Berhasil Ditambahkan.")
    except sqlite3.IntegrityError:
        messagebox.showinfo("Add Domain", "Maaf, Domain Yang Anda Tambahkan,\nSudah Ada Di Database.\n\nSilahkan Input Domain / Situs Yang Lainnya.")
    conn.close()


def delete_domain():
    site = simpledialog.askstring("Delete Domain", "     Masukkan Domain Yang Ingin Dihapus:     ")
    if not site:
        return
    site = site.strip().lower()
    if site.startswith("www."):
        site = site[4:]

    conn = connect_domain_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Domain_ID FROM blocked_domains WHERE Domain_Name = ?", (site,))
    if cursor.fetchone() is None:
        conn.close()
        messagebox.showwarning("Domain Tidak Ditemukan", "Maaf, Domain Yang Anda Inputkan,\nTidak Terdaftar Di Database.")
        return

    cursor.execute("DELETE FROM blocked_domains WHERE Domain_Name = ?", (site,))
    conn.commit()
    conn.close()

    update_hosts_file()
    log_message(f"\n[-] {site} Berhasil Dihapus.")


def get_filtering_status():
    hosts_path = get_hosts_path()
    blocked_sites = load_blocked_sites()
    try:
        with open(hosts_path, "r") as file:
            content = file.read()
        if not blocked_sites:
            return "INACTIVE"
        for site in blocked_sites:
            if f"127.0.0.1 {site}" not in content:
                return "INACTIVE"
        return "ACTIVE"
    except Exception:
        return "UNKNOWN"


def view_domains():
    conn = connect_domain_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Domain_ID, Domain_Name, Last_Update FROM blocked_domains ORDER BY Domain_ID ASC")
    rows = cursor.fetchall()
    filtering_status = get_filtering_status()

    cursor.execute("SELECT Last_Update FROM blocked_domains ORDER BY Last_Update DESC LIMIT 1")
    last_update_row = cursor.fetchone()
    last_update = last_update_row[0] if last_update_row else "-"
    total_domain = len(rows)
    conn.close()

    if entry_1:
        entry_1.delete("1.0", END)
        if rows:
            log_message("========== DOMAIN FILTERING STATUS ==========\n")
            log_message(f"Filtering Status : {filtering_status}")
            log_message(f"Total Domain     : {total_domain}")
            log_message(f"Last Update      : {last_update}\n")
            log_message("========== DAFTAR DOMAIN ==========")
            for row in rows:
                log_message(f"\nID           : {row[0]}")
                log_message(f"Domain       : {row[1]}")
                log_message(f"Last Update  : {row[2]}")
        else:
            log_message("\nTidak Ada Domain Yang Diblokir.")


def format_list():
    confirm = messagebox.askyesno("Format List (Domain)", "Tindakan Ini Akan Menghapus\nSemua Daftar Domain Yang Telah Ditambahkan.\n\nKlik YES Jika Yakin.")
    if not confirm:
        log_message("\n[INFO] Format List Dibatalkan.")
        return

    conn = connect_domain_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_domains")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='blocked_domains'")
    conn.commit()
    conn.close()

    update_hosts_file()
    log_message("\n[SUCCESS] Semua Domain Berhasil Dihapus.")
    log_message("[SUCCESS] ID Domain Berhasil Direset.")


def disable_filtering():
    confirm = messagebox.askyesno("Disable Filtering", "Apakah Anda Yakin Ingin Menonaktifkan Filtering?")
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
                    if f"127.0.0.1 {site}" in line or f"127.0.0.1 www.{site}" in line:
                        remove_line = True
                        break
                if not remove_line:
                    file.write(line)

        log_message("\n[SUCCESS] Filtering Berhasil Dinonaktifkan.")
        log_message("[SUCCESS] Seluruh Entri Hosts Berhasil Dibersihkan.")
    except PermissionError:
        log_message("\n[ERROR] Jalankan Program Sebagai Administrator.")
    except Exception as e:
        log_message(f"\n[ERROR] {e}")


# =========================================================
# LOGIKA & DATABASE: KEYWORD FILTERING (GUI 4)
# =========================================================

def init_keyword_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keyword_filtering (
        Keyword_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Keyword TEXT NOT NULL,
        Penalty_Duration_Sec INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def load_keywords_from_database():
    global cached_keywords
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT Keyword, Penalty_Duration_Sec FROM keyword_filtering")
    cached_keywords = cursor.fetchall()
    conn.close()
    write_log(f"[+] {len(cached_keywords)} Keyword Berhasil Dimuat.")


def write_log(message):
    if output_text and output_text.winfo_exists():
        output_text.insert(END, message + "\n")
        output_text.see(END)


def tambah_keyword_gui():
    keyword = simpledialog.askstring("Tambah Keyword", "Masukkan Keyword:", parent=root)
    if not keyword:
        return
    duration = simpledialog.askinteger("Durasi Hukuman", "Masukkan Durasi Hukuman (Detik):", parent=root)
    if duration is None:
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT Keyword FROM keyword_filtering WHERE Keyword = ?", (keyword.lower(),))
    if cursor.fetchone():
        conn.close()
        messagebox.showinfo("Add Keyword", "Maaf, Keyword Yang Anda Tambahkan,\nSudah Ada Di Database.\n\nSilahkan Input Keyword Yang Lainnya.")
        return

    cursor.execute("INSERT INTO keyword_filtering (Keyword, Penalty_Duration_Sec) VALUES (?, ?)", (keyword.lower(), duration))
    conn.commit()
    conn.close()

    write_log(f"[+] Keyword '{keyword}' Berhasil Ditambahkan.")
    load_keywords_from_database()


def hapus_keyword_gui():
    keyword = simpledialog.askstring("Hapus Keyword", "   Masukkan Keyword Yang Ingin Dihapus:   ")
    if not keyword:
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keyword_filtering WHERE Keyword = ?", (keyword.lower(),))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted > 0:
        write_log(f"[+] Keyword '{keyword}' Berhasil Dihapus.")
        load_keywords_from_database()
    else:
        messagebox.showwarning("Keyword Tidak Ditemukan", "Maaf, Keyword Yang Anda Inputkan,\nTidak Terdaftar Di Database.")


def format_database_gui():
    confirm = messagebox.askyesno("Format List (Keyword)", "Tindakan Ini Akan Menghapus\nSemua Daftar Keyword Yang Telah Ditambahkan.\n\nKlik YES Jika Yakin.")
    if not confirm:
        write_log("[INFO] Format List Dibatalkan.")
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keyword_filtering")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='keyword_filtering'")
    conn.commit()
    conn.close()

    load_keywords_from_database()
    write_log("[+] Semua Keyword Berhasil Dihapus.")


def lihat_keyword_gui():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT Keyword_ID, Keyword, Penalty_Duration_Sec FROM keyword_filtering ORDER BY Keyword_ID ASC")
    data = cursor.fetchall()
    conn.close()

    write_log("\n========== DAFTAR KEYWORD ==========")
    if not data:
        write_log("Belum Ada Keyword.")
        return
    for row in data:
        write_log(f"ID: {row[0]} | Keyword: {row[1]} | Penalty: {row[2]} detik")


def is_interface_exists():
    result = subprocess.run("netsh interface show interface", capture_output=True, text=True, shell=True)
    output_lower = result.stdout.lower()
    return any(interface.lower() in output_lower for interface in NETWORK_INTERFACE_NAMES)


def disable_internet(duration):
    global internet_disabled
    if internet_disabled:
        return
    if not is_interface_exists():
        write_log("[!] Interface internet tidak ditemukan.")
        return

    write_log(f"[!] Internet Diputus Selama {duration} Detik.")
    for interface_name in NETWORK_INTERFACE_NAMES:
        subprocess.run(f'netsh interface set interface "{interface_name}" disable', shell=True)

    internet_disabled = True
    threading.Thread(target=internet_reenable_timer, args=(duration,), daemon=True).start()


def internet_reenable_timer(duration):
    time.sleep(duration)
    enable_internet()


def enable_internet():
    global internet_disabled
    for interface_name in NETWORK_INTERFACE_NAMES:
        subprocess.run(f'netsh interface set interface "{interface_name}" enable', shell=True)
    internet_disabled = False
    write_log("[+] Internet Berhasil Diaktifkan Kembali.")


def is_browser_active():
    try:
        window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()
        browser_keywords = ["chrome", "firefox", "edge", "opera", "brave", "duckduckgo", "vivaldi", "tor browser"]
        return any(browser in window_title for browser in browser_keywords)
    except:
        return False


def monitor_keyboard():
    buffer = ""
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "space":
                buffer += " "
            elif len(event.name) == 1:
                buffer += event.name
            elif event.name == "enter":
                buffer = ""
            else:
                continue

        if len(buffer) > 50:
            buffer = buffer[-50:]

        for word, penalty in cached_keywords:
            if word.lower() in buffer.lower():
                if is_browser_active():
                    write_log(f"[!] Keyword Keyboard Terdeteksi: {word}")
                    disable_internet(penalty)
                    buffer = ""
                break


def monitor_clipboard():
    recent_text = ""
    while True:
        try:
            text = pyperclip.paste()
            if text != recent_text:
                recent_text = text
                for word, penalty in cached_keywords:
                    if word.lower() in text.lower():
                        if is_browser_active():
                            write_log(f"[!] Keyword Clipboard Terdeteksi: {word}")
                            disable_internet(penalty)
                            break
        except:
            pass
        time.sleep(1)


def export_program_gui():
    output_path = output_path_entry.get().strip()
    if output_path == "":
        messagebox.showerror("Error", "Output Path Tidak Boleh Kosong")
        return

    nama_program = simpledialog.askstring("Nama Program", "                  Masukkan Nama File .exe:                  ")
    if not nama_program:
        return

    write_log("[+] Memulai Export Program...")
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        current_file = os.path.abspath(__file__)
        cmd = f'python -m PyInstaller --onefile --noconsole --name "{nama_program}" --distpath "{output_path}" "{current_file}"'
        
        subprocess.run(cmd, shell=True)
        shutil.copy2(DATABASE_NAME, os.path.join(output_path, "keyword_filter.db"))
        write_log("[+] Export Program Berhasil.")
    except Exception as e:
        write_log(f"[!] Export Gagal: {e}")


def browse_folder():
    folder = filedialog.askdirectory()
    if folder and output_path_entry:
        output_path_entry.delete(0, END)
        output_path_entry.insert(0, folder)


# =========================================================
# MANAJEMEN HALAMAN GUI (FRAME SWITCHING ENGINE)
# =========================================================

def login_action():
    username = entry_username.get()
    password = entry_password.get()

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        messagebox.showinfo("Login Berhasil", "Selamat Datang Di Sistem Filter X")
        show_menu_screen()
    else:
        messagebox.showerror("Login Gagal", "Username Atau Password Salah!")


def show_login_screen():
    global entry_username, entry_password
    clear_window()
    root.title("Sistem Filter X - Login")

    canvas = Canvas(root, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
    canvas.place(x=0, y=0)
    canvas.create_rectangle(500.0, 0.0, 1000.0, 600.0, fill="#1E74F6", outline="")

    # Labels
    canvas.create_text(550.0, 155.0, anchor="nw", text="Username", fill="#FFFFFF", font=("Inter", 30, "normal"))
    canvas.create_text(550.0, 301.0, anchor="nw", text="Password", fill="#FFFFFF", font=("Inter", 30, "normal"))
    canvas.create_text(613.0, 60.0, anchor="nw", text="FILTER “X”", fill="#FFFFFF", font=("Inter", 40, "bold"))

    # Entries
    entry_username = Entry(root, bd=0, bg="#D9D9D9", fg="#000716", insertbackground="#000716", highlightthickness=0, font=("Arial", 18))
    entry_username.place(x=550.0, y=219.0, width=400.0, height=58.0)

    entry_password = Entry(root, bd=0, bg="#D9D9D9", fg="#000716", insertbackground="#000716", highlightthickness=0, show="*", font=("Arial", 18))
    entry_password.place(x=550.0, y=365.0, width=400.0, height=58.0)

    # Logo Asset
    try:
        image_image_1 = load_photo_image(relative_to_assets("image_1.png"))
        canvas.create_image(250.0, 300.0, image=image_image_1)
    except:
        pass

    # Button Login
    button_login = Button(root, text="Log In", font=("Segoe UI", 20, "bold"), bg="#FFFFFF", fg="#1E74F6", activebackground="#EAEAEA", activeforeground="#1E74F6", relief="flat", cursor="hand2", borderwidth=0, command=login_action)
    button_login.place(x=625.0, y=473.0, width=250.0, height=55.0)

    button_login.bind("<Enter>", lambda e: button_login.config(bg="#EAEAEA"))
    button_login.bind("<Leave>", lambda e: button_login.config(bg="#FFFFFF"))


def show_menu_screen():
    clear_window()
    root.title("Sistem Filter X - Menu")

    canvas2 = Canvas(root, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
    canvas2.place(x=0, y=0)
    canvas2.create_rectangle(500.0, 0.0, 1000.0, 600.0, fill="#1E74F6", outline="")

    try:
        image_image_1 = load_photo_image(relative_to_assets("image_1.png"))
        canvas2.create_image(250.0, 300.0, image=image_image_1)
    except:
        pass

    canvas2.create_text(750.0, 160.0, anchor="center", text="Welcome To\n FILTER “X”", fill="#FFFFFF", justify="center", font=("Inter", 40, "normal"))
    canvas2.create_text(585.0, 337.0, anchor="nw", text="Select Filtering Method", fill="#FFFFFF", font=("Inter", 25, "normal"))

    # Button Domain
    button_domain = Button(root, text="Domain Filtering", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#1E74F6", activebackground="#EAEAEA", activeforeground="#1E74F6", relief="flat", cursor="hand2", borderwidth=0, command=show_domain_screen)
    button_domain.place(x=533.0, y=397.0, width=200.0, height=50.0)
    button_domain.bind("<Enter>", lambda e: button_domain.config(bg="#EAEAEA"))
    button_domain.bind("<Leave>", lambda e: button_domain.config(bg="#FFFFFF"))

    # Button Keyword
    button_keyword = Button(root, text="Keyword Filtering", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#1E74F6", activebackground="#EAEAEA", activeforeground="#1E74F6", relief="flat", cursor="hand2", borderwidth=0, command=show_keyword_screen)
    button_keyword.place(x=767.0, y=397.0, width=200.0, height=50.0)
    button_keyword.bind("<Enter>", lambda e: button_keyword.config(bg="#EAEAEA"))
    button_keyword.bind("<Leave>", lambda e: button_keyword.config(bg="#FFFFFF"))


def show_domain_screen():
    global entry_1
    clear_window()
    root.title("Domain Filtering")

    canvas = Canvas(root, bg="#1E74F6", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
    canvas.place(x=0, y=0)
    canvas.create_rectangle(500.0, 0.0, 1000.0, 600.0, fill="#00A17C", outline="")

    canvas.create_text(44.0, 29.0, anchor="nw", text="DOMAIN FILTERING", fill="#FFFFFF", font=("Segoe UI", 28, "bold"))
    canvas.create_text(44.0, 90.0, anchor="nw", text="( Choose Option )", fill="#FFFFFF", font=("Segoe UI", 16))
    canvas.create_text(530.0, 39.0, anchor="nw", text="( Input / Output Text )", fill="#FFFFFF", font=("Segoe UI", 16))

    BUTTON_STYLE = {"font": ("Segoe UI", 11, "bold"), "bg": "#FFFFFF", "fg": "#1E74F6", "activebackground": "#D9D9D9", "activeforeground": "#1E74F6", "relief": "flat", "bd": 0, "cursor": "hand2"}

    Button(root, text="Add Domain", command=add_domain, **BUTTON_STYLE).place(x=147, y=176, width=210, height=50)
    Button(root, text="Delete Domain", command=delete_domain, **BUTTON_STYLE).place(x=147, y=257, width=210, height=50)
    Button(root, text="Domain List", command=view_domains, **BUTTON_STYLE).place(x=147, y=338, width=210, height=50)
    Button(root, text="Format List", command=format_list, **BUTTON_STYLE).place(x=147, y=419, width=210, height=50)
    
    # Tombol Back - Otomatis kembali ke Halaman Menu Utama
    Button(root, text="Back", command=show_menu_screen, **BUTTON_STYLE).place(x=147, y=500, width=210, height=50)

    Button(root, text="Enable Filtering", command=enable_filtering, font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#00A17C", activebackground="#D9D9D9", activeforeground="#00A17C", relief="flat", bd=0, cursor="hand2").place(x=645, y=500, width=210, height=50)
    Button(root, text="Disable Filtering", command=disable_filtering, font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#D9534F", activebackground="#D9D9D9", activeforeground="#D9534F", relief="flat", bd=0, cursor="hand2").place(x=645, y=430, width=210, height=50)

    entry_1 = Text(root, bd=0, bg="#D9D9D9", fg="#000000", font=("Consolas", 10), highlightthickness=0)
    entry_1.place(x=530, y=86, width=430, height=330)

    scrollbar = Scrollbar(root, command=entry_1.yview)
    scrollbar.place(x=960, y=86, width=20, height=330)
    entry_1.config(yscrollcommand=scrollbar.set)

    log_message("======================================")
    log_message("DOMAIN FILTERING SYSTEM")
    log_message("======================================")
    log_message("\nProgram Berhasil Dijalankan.")
    log_message("Silakan Pilih Menu Yang Tersedia.")


def show_keyword_screen():
    global output_text, output_path_entry
    clear_window()
    root.title("Keyword Filtering")

    left_frame = Frame(root, bg="#1E74F6", width=420, height=600)
    left_frame.place(x=0, y=0)

    right_frame = Frame(root, bg="#00A17C", width=580, height=600)
    right_frame.place(x=420, y=0)

    Label(left_frame, text="KEYWORD FILTERING", bg="#1E74F6", fg="white", font=("Segoe UI", 24, "bold")).place(x=35, y=30)
    Label(left_frame, text="( Choose Option )", bg="#1E74F6", fg="white", font=("Segoe UI", 16)).place(x=35, y=80)
    Label(right_frame, text="( Input / Output Text )", bg="#00A17C", fg="white", font=("Segoe UI", 16)).place(x=25, y=20)

    output_text = Text(right_frame, bg="#D9D9D9", fg="black", font=("Consolas", 10), wrap="word")
    output_text.place(x=25, y=60, width=530, height=280)

    scrollbar = Scrollbar(output_text)
    scrollbar.pack(side="right", fill="y")
    output_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=output_text.yview)

    Label(right_frame, text="( Output Path )", bg="#00A17C", fg="white", font=("Segoe UI", 16)).place(x=25, y=370)
    output_path_entry = Entry(right_frame, font=("Segoe UI", 11))
    output_path_entry.place(x=25, y=410, width=530, height=40)

    def create_menu_button(text, y, command):
        return Button(left_frame, text=text, command=command, bg="#FFFFFF", fg="#1E74F6", activebackground="#D9D9D9", activeforeground="#1E74F6", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2").place(x=100, y=y, width=220, height=50)

    create_menu_button("Add Keyword", 170, tambah_keyword_gui)
    create_menu_button("Delete Keyword", 250, hapus_keyword_gui)
    create_menu_button("Keyword List", 330, lihat_keyword_gui)
    create_menu_button("Format List", 410, format_database_gui)
    create_menu_button("Export Program", 490, export_program_gui)

    Button(right_frame, text="Browse", command=browse_folder, bg="#FFFFFF", fg="#00A17C", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2").place(x=440, y=470, width=115, height=40)
    
    # Tombol BACK - Otomatis kembali ke Halaman Menu Utama
    Button(right_frame, text="BACK", command=show_menu_screen, bg="#FFFFFF", fg="#00A17C", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2").place(x=25, y=470, width=115, height=40)

    write_log("[+] Program Monitoring Dimulai...")
    write_log(f"[+] {len(cached_keywords)} Keyword Berhasil Dimuat.")


# =========================================================
# MAIN INITIALIZATION & BACK-END THREAD RUNNER
# =========================================================

if __name__ == "__main__":
    # Aktifkan setelan resolusi layar (DPI) Windows
    enable_dpi_awareness()

    # Inisialisasi Database
    connect_domain_db().close()
    init_keyword_database()

    # Memuat cache keyword untuk background threads
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT Keyword, Penalty_Duration_Sec FROM keyword_filtering")
        cached_keywords = cursor.fetchall()
        conn.close()
    except:
        pass

    # Menjalankan Background Monitoring Threads secara global sekali saja
    threading.Thread(target=monitor_clipboard, daemon=True).start()
    threading.Thread(target=monitor_keyboard, daemon=True).start()

    # Mempersiapkan Root Window Tunggal
    root = Tk()
    root.geometry("1000x600")
    root.configure(bg="#FFFFFF")
    root.resizable(False, False)
    center_window(root, 1000, 600)

    # Menampilkan Halaman Pertama (Login)
    show_login_screen()

    root.mainloop()