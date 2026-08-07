import customtkinter as ctk


def start():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()

    app.title("WeightSlip AI Pro")

    app.geometry("1400x850")

    app.minsize(1200, 700)

    label = ctk.CTkLabel(
        app,
        text="WeightSlip AI Pro\nVersion 0.1",
        font=("Segoe UI", 30, "bold")
    )

    label.pack(expand=True)

    app.mainloop()
