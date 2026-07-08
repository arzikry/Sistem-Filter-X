# =========================================================
# SISTEM FILTER X
# GUI 4 KEYWORD FILTERING
# =========================================================

import os
import sys
import time
import shutil
import sqlite3
import threading
import subprocess
import keyboard
import pyperclip
import win32gui

from tkinter import (
    Tk,
    Frame,
    Label,
    Button,
    Text,
    Entry,
    END,
    messagebox,
    simpledialog,
    Scrollbar,
    filedialog,
)

# =====================================================
# KONFIGURASI WINDOW
# =====================================================

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# =====================================================
# DATABASE
# =====================================================

def get_base_path():

    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_path()

DATABASE_NAME = os.path.join(
    BASE_DIR,
    "keyword_filter.db"
)

# =====================================================
# INTERNET CONFIG
# =====================================================

NETWORK_INTERFACE_NAMES = [
    "Wi-Fi",
    "Ethernet"
]

internet_disabled = False

cached_keywords = []

# =====================================================
# TKINTER WINDOW
# =====================================================

window = Tk()

window.title("Keyword Filtering")

window.geometry(
    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
)

window.configure(bg="#1E74F6")

window.resizable(False, False)

# =====================================================
# LEFT PANEL
# =====================================================

left_frame = Frame(
    window,
    bg="#1E74F6",
    width=420,
    height=600
)

left_frame.place(x=0, y=0)

# =====================================================
# RIGHT PANEL
# =====================================================

right_frame = Frame(
    window,
    bg="#00A17C",
    width=580,
    height=600
)

right_frame.place(x=420, y=0)

# =====================================================
# TITLE
# =====================================================

title_label = Label(
    left_frame,
    text="KEYWORD FILTERING",
    bg="#1E74F6",
    fg="white",
    font=("Segoe UI", 24, "bold")
)

title_label.place(x=35, y=30)

subtitle_label = Label(
    left_frame,
    text="( Choose Option )",
    bg="#1E74F6",
    fg="white",
    font=("Segoe UI", 16)
)

subtitle_label.place(x=35, y=80)

# =====================================================
# OUTPUT TITLE
# =====================================================

output_title = Label(
    right_frame,
    text="( Input / Output Text )",
    bg="#00A17C",
    fg="white",
    font=("Segoe UI", 16)
)

output_title.place(x=25, y=20)

# =====================================================
# OUTPUT TEXTBOX
# =====================================================

output_text = Text(
    right_frame,
    bg="#D9D9D9",
    fg="black",
    font=("Consolas", 10),
    wrap="word"
)

output_text.place(
    x=25,
    y=60,
    width=530,
    height=280
)

scrollbar = Scrollbar(output_text)

scrollbar.pack(
    side="right",
    fill="y"
)

output_text.config(
    yscrollcommand=scrollbar.set
)

scrollbar.config(
    command=output_text.yview
)

# =====================================================
# OUTPUT PATH TITLE
# =====================================================

path_title = Label(
    right_frame,
    text="( Output Path )",
    bg="#00A17C",
    fg="white",
    font=("Segoe UI", 16)
)

path_title.place(x=25, y=370)

# =====================================================
# OUTPUT PATH ENTRY
# =====================================================

output_path_entry = Entry(
    right_frame,
    font=("Segoe UI", 11)
)

output_path_entry.place(
    x=25,
    y=410,
    width=530,
    height=40
)

# =====================================================
# WRITE LOG
# =====================================================

def write_log(message):

    output_text.insert(
        END,
        message + "\n"
    )

    output_text.see(END)

# =====================================================
# DATABASE INIT
# =====================================================

def init_database():

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

# =====================================================
# LOAD KEYWORDS
# =====================================================

def load_keywords_from_database():

    global cached_keywords

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT Keyword,
               Penalty_Duration_Sec
        FROM keyword_filtering
    """)

    cached_keywords = cursor.fetchall()

    conn.close()

    write_log(
        f"[+] {len(cached_keywords)} Keyword Berhasil Dimuat."
    )

# =====================================================
# ADD KEYWORD
# =====================================================

def tambah_keyword_gui():

    keyword = simpledialog.askstring(
        "Tambah Keyword",
        "Masukkan Keyword:",
        parent=window
    )


    if not keyword:
        return


    duration = simpledialog.askinteger(
        "Durasi Hukuman",
        "Masukkan Durasi Hukuman (Detik):",
        parent=window
    )


    if duration is None:
        return


    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()


    # Cek apakah keyword sudah ada
    cursor.execute("""
        SELECT Keyword
        FROM keyword_filtering
        WHERE Keyword = ?
    """, (keyword.lower(),))


    existing_keyword = cursor.fetchone()


    # Jika keyword ditemukan
    if existing_keyword:


        conn.close()


        messagebox.showinfo(
            "Add Keyword",
            "Maaf, Keyword Yang Anda Tambahkan,\nSudah Ada Di Database.\n\n"
            "Silahkan Input Keyword Yang Lainnya."
        )


        return



    # Jika keyword belum ada, tambahkan
    cursor.execute("""
        INSERT INTO keyword_filtering
        (Keyword, Penalty_Duration_Sec)
        VALUES (?, ?)
    """, (keyword.lower(), duration))


    conn.commit()

    conn.close()


    write_log(
        f"[+] Keyword '{keyword}' Berhasil Ditambahkan."
    )


    load_keywords_from_database()

# =====================================================
# DELETE KEYWORD
# =====================================================

def hapus_keyword_gui():

    keyword = simpledialog.askstring(
        "Hapus Keyword",
        "   Masukkan Keyword Yang Ingin Dihapus:   "
    )


    if not keyword:
        return


    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()


    cursor.execute("""
        DELETE FROM keyword_filtering
        WHERE Keyword = ?
    """, (keyword.lower(),))


    deleted = cursor.rowcount


    conn.commit()

    conn.close()


    if deleted > 0:


        write_log(
            f"[+] Keyword '{keyword}' Berhasil Dihapus."
        )


        load_keywords_from_database()


    else:


        messagebox.showwarning(
            "Keyword Tidak Ditemukan",
            "Maaf, Keyword Yang Anda Inputkan,\nTidak Terdaftar Di Database."
        )

# =====================================================
# FORMAT DATABASE
# =====================================================

def format_database_gui():

    confirm = messagebox.askyesno(
        "Format List (Keyword)",
        "Tindakan Ini Akan Menghapus\nSemua Daftar Keyword Yang Telah Ditambahkan.\n\nKlik YES Jika Yakin."
    )


    # Jika klik NO
    if not confirm:

        write_log(
            "[INFO] Format List Dibatalkan."
        )

        return


    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()


    # Hapus semua keyword
    cursor.execute(
        "DELETE FROM keyword_filtering"
    )


    # Reset ID AUTOINCREMENT SQLite
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='keyword_filtering'"
    )


    conn.commit()

    conn.close()


    # Reload database
    load_keywords_from_database()


    write_log(
        "[+] Semua Keyword Berhasil Dihapus."
    )

# =====================================================
# VIEW KEYWORD
# =====================================================

def lihat_keyword_gui():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT Keyword_ID,
               Keyword,
               Penalty_Duration_Sec
        FROM keyword_filtering
        ORDER BY Keyword_ID ASC
    """)

    data = cursor.fetchall()

    conn.close()

    write_log("\n========== DAFTAR KEYWORD ==========")

    if not data:

        write_log("Belum Ada Keyword.")

        return

    for row in data:

        write_log(
            f"ID: {row[0]} | "
            f"Keyword: {row[1]} | "
            f"Penalty: {row[2]} detik"
        )

# =====================================================
# CEK INTERFACE INTERNET
# =====================================================

def is_interface_exists():

    result = subprocess.run(
        "netsh interface show interface",
        capture_output=True,
        text=True,
        shell=True
    )

    output_lower = result.stdout.lower()

    return any(
        interface.lower() in output_lower
        for interface in NETWORK_INTERFACE_NAMES
    )

# =====================================================
# DISABLE INTERNET
# =====================================================

def disable_internet(duration):

    global internet_disabled

    if internet_disabled:
        return

    if not is_interface_exists():

        write_log(
            "[!] Interface internet tidak ditemukan."
        )

        return

    write_log(
        f"[!] Internet Diputus Selama {duration} Detik."
    )

    for interface_name in NETWORK_INTERFACE_NAMES:

        subprocess.run(
            f'netsh interface set interface "{interface_name}" disable',
            shell=True
        )

    internet_disabled = True

    threading.Thread(
        target=internet_reenable_timer,
        args=(duration,),
        daemon=True
    ).start()

# =====================================================
# INTERNET TIMER
# =====================================================

def internet_reenable_timer(duration):

    time.sleep(duration)

    enable_internet()

# =====================================================
# ENABLE INTERNET
# =====================================================

def enable_internet():

    global internet_disabled

    for interface_name in NETWORK_INTERFACE_NAMES:

        subprocess.run(
            f'netsh interface set interface "{interface_name}" enable',
            shell=True
        )

    internet_disabled = False

    write_log("[+] Internet Berhasil Diaktifkan Kembali.")

# =====================================================
# CEK BROWSER
# =====================================================

def is_browser_active():

    try:

        window_title = win32gui.GetWindowText(
            win32gui.GetForegroundWindow()
        ).lower()

        browser_keywords = [

            "chrome",
            "firefox",
            "edge",
            "opera",
            "brave",
            "duckduckgo",
            "vivaldi",
            "tor browser"
        ]

        return any(
            browser in window_title
            for browser in browser_keywords
        )

    except:
        return False

# =====================================================
# MONITOR KEYBOARD
# =====================================================

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

                    write_log(
                        f"[!] Keyword Keyboard Terdeteksi: {word}"
                    )

                    disable_internet(penalty)

                    buffer = ""

                break

# =====================================================
# MONITOR CLIPBOARD
# =====================================================

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

                            write_log(
                                f"[!] Keyword Clipboard Terdeteksi: {word}"
                            )

                            disable_internet(penalty)

                            break

        except:
            pass

        time.sleep(1)

# =====================================================
# EXPORT PROGRAM
# =====================================================

def export_program_gui():

    output_path = output_path_entry.get().strip()

    if output_path == "":

        messagebox.showerror(
            "Error",
            "Output Path Tidak Boleh Kosong"
        )

        return

    nama_program = simpledialog.askstring(
        "Nama Program",
        "                  Masukkan Nama File .exe:                  "
    )

    if not nama_program:
        return

    write_log("[+] Memulai Export Program...")

    try:

        if not os.path.exists(output_path):

            os.makedirs(output_path)

        current_file = os.path.abspath(__file__)

        cmd = (
            f'python -m PyInstaller '
            f'--onefile '
            f'--noconsole '
            f'--name "{nama_program}" '
            f'--distpath "{output_path}" '
            f'"{current_file}"'
        )

        subprocess.run(
            cmd,
            shell=True
        )

        shutil.copy2(
            DATABASE_NAME,
            os.path.join(
                output_path,
                "keyword_filter.db"
            )
        )

        write_log(
            "[+] Export Program Berhasil."
        )

    except Exception as e:

        write_log(
            f"[!] Export Gagal: {e}"
        )

# =====================================================
# BROWSE OUTPUT PATH
# =====================================================

def browse_folder():

    folder = filedialog.askdirectory()

    if folder:

        output_path_entry.delete(0, END)

        output_path_entry.insert(
            0,
            folder
        )

# =====================================================
# BUTTON STYLE
# =====================================================

def create_menu_button(text, y, command):

    btn = Button(
        left_frame,
        text=text,
        command=command,
        bg="#FFFFFF",
        fg="#1E74F6",
        activebackground="#D9D9D9",
        activeforeground="#1E74F6",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        cursor="hand2"
    )

    btn.place(
        x=100,
        y=y,
        width=220,
        height=50
    )

    return btn

# =====================================================
# BUTTONS
# =====================================================

create_menu_button(
    "Add Keyword",
    170,
    tambah_keyword_gui
)

create_menu_button(
    "Delete Keyword",
    250,
    hapus_keyword_gui
)

create_menu_button(
    "Keyword List",
    330,
    lihat_keyword_gui
)

create_menu_button(
    "Format List",
    410,
    format_database_gui
)

create_menu_button(
    "Export Program",
    490,
    export_program_gui
)

browse_button = Button(
    right_frame,
    text="Browse",
    command=browse_folder,
    bg="#FFFFFF",
    fg="#00A17C",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    cursor="hand2"
)

browse_button.place(
    x=440,
    y=470,
    width=115,
    height=40
)

# =====================================================
# BACK BUTTON
# =====================================================

back_button = Button(
    right_frame,
    text="BACK",
    command=window.destroy,
    bg="#FFFFFF",
    fg="#00A17C",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    cursor="hand2"
)

back_button.place(
    x=25,
    y=470,
    width=115,
    height=40
)

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    init_database()

    load_keywords_from_database()

    write_log(
        "[+] Program Monitoring Dimulai..."
    )

    threading.Thread(
        target=monitor_clipboard,
        daemon=True
    ).start()

    threading.Thread(
        target=monitor_keyboard,
        daemon=True
    ).start()

    window.mainloop()