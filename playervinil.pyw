import tkinter as tk
import pygame
import os
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from tkinter import Label, filedialog


class VinylSimulator:
    def __init__(self, window):
        self.window = window
        self.window.title("Vinyl Simulator")
        self.window.configure(bg="white")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = 990
        window_height = 680
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        pygame.init()
        pygame.mixer.init()

        self.setup_gui()

        self.music_files = []
        self.current_song_index = 0
        self.is_playing = False
        self.angle = 0
        self.song_duration = 0
        self.paused = False
        self.paused_time = 0
        self.rotation_id = None

    def setup_gui(self):
        self.vinyl_image = Image.open("vinyl.png").convert("RGBA")  # Open the vinyl image with an alpha channel
        self.remove_white_background(self.vinyl_image)

        # Load the transparent needle image
        needle_image_path = os.path.join(os.path.dirname(__file__), "needle.png")
        self.needle_image = Image.open(needle_image_path).convert("RGBA")
        self.remove_white_background(self.needle_image)

        # Convert the image to a Tkinter PhotoImage without border
        self.vinyl_photo = ImageTk.PhotoImage(self.vinyl_image)
        self.needle_photo = ImageTk.PhotoImage(self.needle_image)

        # Create a canvas widget for displaying the images without border
        self.canvas = tk.Canvas(
            self.window, width=510, height=400, bg="white", highlightthickness=0
        )
        self.canvas.pack(pady=20)

        # Display the vinyl image on the canvas
        self.vinyl_label = self.canvas.create_image(0, 0, anchor="nw", image=self.vinyl_photo, tags="vinyl_label")

        # Display the transparent needle image on the canvas
        self.needle_label = self.canvas.create_image(
            self.vinyl_image.width / 2 + 180, self.vinyl_image.height / 2 + 10, anchor="center", image=self.needle_photo
        )

        control_frame = tk.Frame(self.window, bg="white")
        control_frame.pack(pady=10)

        self.volume_label = Label(control_frame, bg="white", text="Ένταση Ήχου:", font=("Arial", 14))
        self.volume_label.pack(side=tk.LEFT)

        self.volume_slider = tk.Scale(control_frame, from_=0, to=100, orient="horizontal", command=self.set_volume)
        self.volume_slider.configure(width=30, length=300, bg="white", troughcolor="#E0E0E0", highlightbackground="#E0E0E0")
        self.volume_slider.set(50)
        self.volume_slider.pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(self.window, bg="white")
        button_frame.pack(pady=20)

        self.prev_button = tk.Button(button_frame, text="Προηγούμενο", command=self.play_previous, font=("Arial", 14))
        self.prev_button.configure(width=12, height=2, bg="#4CAF50", fg="white")
        self.prev_button.pack(side=tk.LEFT, padx=20)

        self.play_button = tk.Button(button_frame, text="Αναπαραγωγή", command=self.play_music, font=("Arial", 14))
        self.play_button.configure(width=12, height=2, bg="#FF5722", fg="white")
        self.play_button.pack(side=tk.LEFT, padx=20)

        self.stop_button = tk.Button(button_frame, text="Παύση", command=self.pause_music, font=("Arial", 14))
        self.stop_button.configure(width=12, height=2, bg="#F44336", fg="white")
        self.stop_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(button_frame, text="Επόμενο", command=self.play_next, font=("Arial", 14))
        self.next_button.configure(width=12, height=2, bg="#3F51B5", fg="white")
        self.next_button.pack(side=tk.LEFT, padx=20)

        load_button = tk.Button(button_frame, text="Φόρτωση Φακέλου", command=self.load_folder, font=("Arial", 14))
        load_button.configure(width=15, height=2, bg="#607D8B", fg="white")
        load_button.pack(side=tk.LEFT, padx=20)

        self.song_duration_label = Label(self.window, bg="white", text="Χρόνος Τραγουδιού: 00:00", font=("Arial", 20))
        self.song_duration_label.pack()

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.music_files = []
            self.current_song_index = 0
            self.is_playing = False
            self.load_music_files(folder_path)
            self.update_song_duration()

    def load_music_files(self, folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".mp3"):
                self.music_files.append(os.path.join(folder_path, file))

    def play_music(self):
        if not self.music_files:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.resume_rotation()
        else:
            file = self.music_files[self.current_song_index]
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()

            if not self.is_playing:
                self.is_playing = True
                self.rotate_vinyl()

            song_title = os.path.basename(file)
            self.window.title(f"Vinyl Simulator - {song_title}")

            audio = MP3(file)
            self.song_duration = int(audio.info.length)
            self.update_song_duration()

            self.window.after(100, self.check_song_end)

    def check_song_end(self):
        if not pygame.mixer.music.get_busy() and self.is_playing and not self.paused:
            self.play_next()
        else:
            if self.is_playing:
                current_time = pygame.mixer.music.get_pos() // 1000
                remaining_time = max(0, self.song_duration - current_time)
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                duration_str = f"Χρόνος Τραγουδιού: {minutes:02d}:{seconds:02d}"
                self.song_duration_label.config(text=duration_str)
            self.window.after(100, self.check_song_end)

    def update_song_duration(self):
        minutes = self.song_duration // 60
        seconds = self.song_duration % 60
        duration_str = f"Χρόνος Τραγουδιού: {minutes:02d}:{seconds:02d}"
        self.song_duration_label.config(text=duration_str)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.paused = False
        self.paused_time = 0
        self.stop_rotation()

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            self.paused_time = pygame.mixer.music.get_pos() // 1000
            self.pause_rotation()

    def play_previous(self):
        if not self.music_files:
            return

        if self.paused:
            self.paused = False

        self.current_song_index -= 1
        if self.current_song_index < 0:
            self.current_song_index = len(self.music_files) - 1

        pygame.mixer.music.fadeout(1000)

        self.window.after(1000, self.play_music)
        self.resume_rotation()

    def play_next(self):
        if not self.music_files:
            return

        if self.paused:
            self.paused = False

        self.current_song_index += 1
        if self.current_song_index >= len(self.music_files):
            self.current_song_index = 0

        pygame.mixer.music.fadeout(1000)

        self.window.after(1000, self.play_music)
        self.resume_rotation()

    def rotate_vinyl(self):
        if self.is_playing:
            self.angle += 15
            self.angle %= 360

            rotated_vinyl_image = self.vinyl_image.rotate(self.angle)
            self.vinyl_photo = ImageTk.PhotoImage(rotated_vinyl_image)
            self.canvas.itemconfig(self.vinyl_label, image=self.vinyl_photo)

            self.rotation_id = self.window.after(10, self.rotate_vinyl)

    def set_volume(self, volume):
        volume = float(volume) / 100
        pygame.mixer.music.set_volume(volume)

    def remove_white_background(self, image):
        image_data = image.getdata()

        new_image_data = []

        for item in image_data:
            if item[:3] == (255, 255, 255):  # Ελέγξτε αν οι τιμές R, G, B είναι (255, 255, 255)
                new_image_data.append((0, 0, 0, 0))  # Ορίστε τις τιμές R, G, B, A σε (0, 0, 0, 0) για διαφάνεια
            else:
                new_image_data.append(item)

        image.putdata(new_image_data)

    def pause_rotation(self):
        if self.rotation_id is not None:
            self.window.after_cancel(self.rotation_id)
            self.rotation_id = None

    def resume_rotation(self):
        if self.rotation_id is None:
            self.rotate_vinyl()

    def stop_rotation(self):
        if self.rotation_id is not None:
            self.window.after_cancel(self.rotation_id)
            self.rotation_id = None


window = tk.Tk()
vinyl_simulator = VinylSimulator(window)
window.mainloop()
