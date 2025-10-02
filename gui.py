# gui.py
import tkinter as tk
from PIL import Image, ImageTk # Vous aurez besoin de la bibliothèque Pillow
import threading

class AlitaGUI:
    def __init__(self, main_app_instance):
        self.main_app = main_app_instance
        self.root = tk.Tk()
        # Configuration de la fenêtre
        self.root.title("Alita Assistant")
        self.root.geometry("600x700")
        self.root.overrideredirect(True) # Cache la barre de titre
        self.root.attributes("-topmost", True) # Garde la fenêtre au-dessus des autres
        self.root.attributes("-alpha", 0.9) # Rend la fenêtre semi-transparente

        #initialisation des frames du GIF
        self.gif_frames = []
        self.current_frame = 0
        self.animating = False

        # Gestion du déplacement de la fenêtre
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        # Chargement du logo
        try:
            # Ici, vous devrez charger votre image. Pillow est nécessaire.
            # pip install Pillow
            self.logo_path = "resources/baby_alita.png" # Chemin vers votre image statique
            self.load_gif("resources/baby_alita_talk.gif")
            self.logo_image = ImageTk.PhotoImage(Image.open(self.logo_path))
            self.logo_label = tk.Label(self.root, image=self.logo_image)
            self.logo_label.pack(pady=10)
        except Exception as e:
            print(f"Erreur de chargement du logo : {e}")

        # Zone pour les logs
        self.log_text = tk.Text(self.root, height=40, width=200, bg='black', fg='pink', borderwidth=0)
        self.log_text.pack(pady=10)
        self.log_text.config(state=tk.DISABLED)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def load_gif(self, filename):
        """Charge toutes les frames d'un GIF dans une liste."""
        try:
            gif = Image.open(filename)
            for frame in range(0, gif.n_frames):
                gif.seek(frame)
                self.gif_frames.append(ImageTk.PhotoImage(gif.copy()))
        except Exception as e:
            print(f"Erreur lors du chargement du GIF : {e}")
            self.gif_frames = []

    def animate_gif(self):
        """Met à jour l'image du logo pour créer l'animation."""
        if self.animating:
            self.logo_label.config(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.root.after(200, self.animate_gif) # Change l'image toutes les 100ms
        else:
            self.logo_label.config(image=self.logo_image)
            self.current_frame = 0

    def update_state(self, state, text=None):
        """Met à jour l'état de l'interface (logo et logs)."""
        if text:
            self.add_log(text)
        
        if state in ["listening", "processing", "speaking"]:
            self.animating = True
            if not self.gif_frames:
                # Si le GIF n'a pas pu être chargé, on utilise une image statique.
                self.logo_label.config(image=self.logo_image)
            else:
                self.animate_gif()
        else: # "initial" ou autres états
            self.animating = False
            self.logo_label.config(image=self.logo_image)

    def add_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_gui(self):
        self.root.mainloop()

# Le fichier main.py devra maintenant créer une instance de cette classe
# et la lancer dans un thread séparé.