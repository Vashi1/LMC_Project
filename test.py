import pygame
import time
import random
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class ExperimentGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Experiment Settings")
        self.root.geometry("400x500")

        # Variables to store settings
        self.participant_name = tk.StringVar()
        self.music_type = tk.StringVar(value="beats")
        self.num_epochs = tk.StringVar(value="1")
        self.epoch_durations = []

        self.create_gui()

    def create_gui(self):
        # Participant name
        tk.Label(self.root, text="Participant Name:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.participant_name).pack(pady=5)

        # Music type
        tk.Label(self.root, text="Music Type:").pack(pady=5)
        tk.Radiobutton(self.root, text="Beats", variable=self.music_type, value="beats").pack()
        tk.Radiobutton(self.root, text="No Beats", variable=self.music_type, value="no_beats").pack()

        # Number of epochs
        tk.Label(self.root, text="Number of Epochs:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.num_epochs).pack(pady=5)

        # Button to add epoch durations
        tk.Button(self.root, text="Set Epoch Durations", command=self.set_epoch_durations).pack(pady=10)

        # Start button
        tk.Button(self.root, text="Start Experiment", command=self.start_experiment).pack(pady=20)

    def set_epoch_durations(self):
        try:
            num_epochs = int(self.num_epochs.get())
            duration_window = tk.Toplevel(self.root)
            duration_window.title("Set Epoch Durations")
            duration_window.geometry("300x400")

            duration_entries = []
            for i in range(num_epochs):
                tk.Label(duration_window, text=f"Epoch {i + 1} Duration (seconds):").pack(pady=5)
                entry = tk.Entry(duration_window)
                entry.pack(pady=5)
                duration_entries.append(entry)

            def save_durations():
                try:
                    self.epoch_durations = [float(entry.get()) for entry in duration_entries]
                    duration_window.destroy()
                    messagebox.showinfo("Success", "Epoch durations saved!")
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers for durations")

            tk.Button(duration_window, text="Save Durations", command=save_durations).pack(pady=20)

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of epochs")

    def start_experiment(self):
        if not self.epoch_durations:
            messagebox.showerror("Error", "Please set epoch durations first")
            return

        if not self.participant_name.get():
            messagebox.showerror("Error", "Please enter participant name")
            return

        self.root.destroy()
        run_experiment(
            self.participant_name.get(),
            self.epoch_durations,
            len(self.epoch_durations),
            self.music_type.get()
        )


def run_experiment(participant_name, epoch_durations, num_epochs, music_type):
    # Initialize pygame
    pygame.init()

    # Constants
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    BEAT_INTERVAL = 0.4286

    # Initialize display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Perceptual Learning Experiment')

    # Paths to music files
    MUSIC_DRUMS = "/home/rakshith/PycharmProjects/pythonProject/drums-with-percussion-140-bpm-190230.mp3"
    MUSIC_PIANO = "/home/rakshith/PycharmProjects/pythonProject/relaxing-piano-music-248868.mp3"

    # Store results
    results = []
    event_log = []  # New list to store green screen and error events

    # Start the experiment loop
    for epoch in range(num_epochs):
        # Display epoch start message
        screen.fill(WHITE)
        font = pygame.font.Font(None, 36)
        text = font.render(f"Press ENTER to start Epoch {epoch + 1}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()

        # Wait for ENTER key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False

        # Play music
        if music_type == "beats":
            pygame.mixer.music.load(MUSIC_DRUMS)
        else:
            pygame.mixer.music.load(MUSIC_PIANO)
        pygame.mixer.music.play(-1)

        screen.fill(WHITE)
        pygame.display.flip()

        start_time = time.time()
        reaction_times = []
        errors = 0
        epoch_duration = epoch_durations[epoch]
        last_green_time = -1
        green_shown = False
        green_start_time = None

        # Main experiment loop
        while time.time() - start_time < epoch_duration:
            current_time = time.time()

            # Show green screen based on music type
            if not green_shown:
                if music_type == "no_beats":
                    if random.random() < 0.05 and current_time - last_green_time > 1:
                        screen.fill(GREEN)
                        pygame.display.flip()
                        green_shown = True
                        green_start_time = current_time
                        last_green_time = current_time
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        event_log.append(["green_screen", epoch + 1, timestamp])

                elif music_type == "beats":
                    if current_time - last_green_time > 1 and int((current_time - start_time) / BEAT_INTERVAL) % 2 == 0:
                        screen.fill(GREEN)
                        pygame.display.flip()
                        green_shown = True
                        green_start_time = current_time
                        last_green_time = current_time
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        event_log.append(["green_screen", epoch + 1, timestamp])

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    if green_shown:
                        reaction_time = time.time() - green_start_time
                        reaction_times.append(reaction_time)
                        screen.fill(WHITE)
                        pygame.display.flip()
                        green_shown = False
                    else:
                        errors += 1
                        event_log.append(["error", epoch + 1, timestamp])

        # Stop music after each epoch
        pygame.mixer.music.stop()

        # Save epoch results
        results.append({
            "Participant": participant_name,
            "Epoch": epoch + 1,
            "Reaction Times": reaction_times,
            "Errors": errors,
            "Epoch Duration": epoch_duration
        })

    # Save results
    save_results(results, event_log, participant_name)

    pygame.quit()


def save_results(results, event_log, participant_name):
    # Save reaction times and errors
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_filename = f"experiment_results_{participant_name}_{timestamp}.csv"
    events_filename = f"experiment_events_{participant_name}_{timestamp}.csv"

    # Save main results
    with open(results_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Participant", "Epoch", "Reaction Time", "Errors", "Epoch Duration"])

        for result in results:
            for rt in result["Reaction Times"]:
                writer.writerow([
                    result["Participant"],
                    result["Epoch"],
                    rt,
                    result["Errors"],
                    result["Epoch Duration"]
                ])

    # Save event log
    with open(events_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Event Type", "Epoch", "Timestamp"])
        writer.writerows(event_log)

    print(f"Results saved to {results_filename}")
    print(f"Event log saved to {events_filename}")


def main():
    gui = ExperimentGUI()
    gui.root.mainloop()


if __name__ == "__main__":
    main()