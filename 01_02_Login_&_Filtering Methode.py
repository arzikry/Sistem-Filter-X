# =========================================================
# SISTEM FILTER X
# GUI 1 LOGIN + GUI 2 PILIH METODE FILTERING
# =========================================================

from pathlib import Path
import ctypes
import sys

from tkinter import *
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


# =========================================================
# KONFIGURASI
# =========================================================

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets")

IMAGE_REFS = []

VALID_USERNAME = "zrandi"
VALID_PASSWORD = "skripsi2026"


# =========================================================
# FUNGSI UMUM
# =========================================================

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


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


# =========================================================
# GUI KE-2
# HALAMAN PILIH METODE FILTERING
# =========================================================

def open_filter_menu():

    filter_window = Toplevel()

    filter_window.title("Sistem Filter X")
    filter_window.geometry("1000x600")
    filter_window.configure(bg="#FFFFFF")

    center_window(filter_window, 1000, 600)

    canvas2 = Canvas(
        filter_window,
        bg="#FFFFFF",
        height=600,
        width=1000,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas2.place(x=0, y=0)

    canvas2.create_rectangle(
        500.0,
        0.0,
        1000.0,
        600.0,
        fill="#1E74F6",
        outline=""
    )

    # =====================================================
    # GAMBAR KIRI
    # =====================================================

    image_image_1 = load_photo_image(
        relative_to_assets("image_1.png")
    )

    image_1 = canvas2.create_image(
        250.0,
        300.0,
        image=image_image_1
    )

    # =====================================================
    # TEXT WELCOME
    # =====================================================

    canvas2.create_text(
        750.0,
        160.0,
        anchor="center",
        text="Welcome To\n FILTER “X”",
        fill="#FFFFFF",
        justify="center",
        font=("Inter", 40, "normal")
    )

    # =====================================================
    # TEXT SELECT METHOD
    # =====================================================

    canvas2.create_text(
        585.0,
        337.0,
        anchor="nw",
        text="Select Filtering Method",
        fill="#FFFFFF",
        font=("Inter", 25, "normal")
    )

    # =====================================================
    # BUTTON DOMAIN FILTERING
    # =====================================================

    button_domain = Button(
        filter_window,
        text="Domain Filtering",
        font=("Segoe UI", 14, "bold"),
        bg="#FFFFFF",
        fg="#1E74F6",
        activebackground="#EAEAEA",
        activeforeground="#1E74F6",
        relief="flat",
        cursor="hand2",
        borderwidth=0,
        command=lambda: messagebox.showinfo(
            "Info",
            "Menu Domain Filtering Belum Ditambahkan"
        )
    )

    button_domain.place(
        x=533.0,
        y=397.0,
        width=200.0,
        height=50.0
    )

    # Hover Domain Button
    def domain_enter(e):
        button_domain.config(bg="#EAEAEA")

    def domain_leave(e):
        button_domain.config(bg="#FFFFFF")

    button_domain.bind("<Enter>", domain_enter)
    button_domain.bind("<Leave>", domain_leave)

    # =====================================================
    # BUTTON KEYWORD FILTERING
    # =====================================================

    button_keyword = Button(
        filter_window,
        text="Keyword Filtering",
        font=("Segoe UI", 14, "bold"),
        bg="#FFFFFF",
        fg="#1E74F6",
        activebackground="#EAEAEA",
        activeforeground="#1E74F6",
        relief="flat",
        cursor="hand2",
        borderwidth=0,
        command=lambda: messagebox.showinfo(
            "Info",
            "Menu Keyword Filtering Belum Ditambahkan"
        )
    )

    button_keyword.place(
        x=767.0,
        y=397.0,
        width=200.0,
        height=50.0
    )

    # Hover Keyword Button
    def keyword_enter(e):
        button_keyword.config(bg="#EAEAEA")

    def keyword_leave(e):
        button_keyword.config(bg="#FFFFFF")

    button_keyword.bind("<Enter>", keyword_enter)
    button_keyword.bind("<Leave>", keyword_leave)

    filter_window.resizable(False, False)


# =========================================================
# FUNGSI LOGIN
# =========================================================

def login():

    username = entry_username.get()
    password = entry_password.get()

    if username == VALID_USERNAME and password == VALID_PASSWORD:

        messagebox.showinfo(
            "Login Berhasil",
            "Selamat Datang Di Sistem Filter X"
        )

        # BUKA GUI KE-2
        open_filter_menu()

        # SEMBUNYIKAN GUI LOGIN
        window.withdraw()

    else:

        messagebox.showerror(
            "Login Gagal",
            "Username Atau Password Salah!"
        )


# =========================================================
# MAIN WINDOW
# GUI LOGIN
# =========================================================

enable_dpi_awareness()

window = Tk()

window.title("Sistem Filter X")

window.geometry("1000x600")
window.configure(bg="#FFFFFF")

center_window(window, 1000, 600)

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=600,
    width=1000,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)

# =========================================================
# BACKGROUND BIRU
# =========================================================

canvas.create_rectangle(
    500.0,
    0.0,
    1000.0,
    600.0,
    fill="#1E74F6",
    outline=""
)

# =========================================================
# TEXT USERNAME
# =========================================================

canvas.create_text(
    550.0,
    155.0,
    anchor="nw",
    text="Username",
    fill="#FFFFFF",
    font=("Inter", 30, "normal")
)

entry_username = Entry(
    window,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    insertbackground="#000716",
    highlightthickness=0,
    font=("Arial", 18)
)

entry_username.place(
    x=550.0,
    y=219.0,
    width=400.0,
    height=58.0
)

# =========================================================
# TEXT PASSWORD
# =========================================================

canvas.create_text(
    550.0,
    301.0,
    anchor="nw",
    text="Password",
    fill="#FFFFFF",
    font=("Inter", 30, "normal")
)

entry_password = Entry(
    window,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    insertbackground="#000716",
    highlightthickness=0,
    show="*",
    font=("Arial", 18)
)

entry_password.place(
    x=550.0,
    y=365.0,
    width=400.0,
    height=58.0
)

# =========================================================
# GAMBAR LOGO KIRI
# =========================================================

image_image_1 = load_photo_image(
    relative_to_assets("image_1.png")
)

image_1 = canvas.create_image(
    250.0,
    300.0,
    image=image_image_1
)

# =========================================================
# JUDUL FILTER X
# =========================================================

canvas.create_text(
    613.0,
    60.0,
    anchor="nw",
    text="FILTER “X”",
    fill="#FFFFFF",
    font=("Inter", 40, "bold")
)

# =========================================================
# BUTTON LOGIN
# =========================================================

button_login = Button(
    window,
    text="Log In",
    font=("Segoe UI", 20, "bold"),
    bg="#FFFFFF",
    fg="#1E74F6",
    activebackground="#EAEAEA",
    activeforeground="#1E74F6",
    relief="flat",
    cursor="hand2",
    borderwidth=0,
    command=login
)

button_login.place(
    x=625.0,
    y=473.0,
    width=250.0,
    height=55.0
)

# Hover Login Button
def on_enter_login(e):
    button_login.config(bg="#EAEAEA")


def on_leave_login(e):
    button_login.config(bg="#FFFFFF")


button_login.bind("<Enter>", on_enter_login)
button_login.bind("<Leave>", on_leave_login)

window.resizable(False, False)

window.mainloop()