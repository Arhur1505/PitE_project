import pygame
import pygame.surfarray
import numpy as np
import imageio
import imageio_ffmpeg

from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv


def record_run(
    model_path="quick_ppo_hill_climb.zip",
    output_file_mp4="gameplay.mp4",
    output_file_png="gameplay.png",
    max_frames=1000,
    fps=30
):
    """
    Uruchamia środowisko HillClimbEnv z wczytanym modelem PPO,
    rejestruje klatki (z pygame) i zapisuje je do pliku MP4.
    Dodatkowo zapisuje pierwszy kadr jako plik PNG.

    :param model_path: ścieżka do wytrenowanego modelu (np. "logs/best_model.zip")
    :param output_file_mp4: ścieżka docelowa pliku .mp4 (wideo)
    :param output_file_png: ścieżka docelowa pierwszego kadru .png
    :param max_frames: maksymalna liczba klatek do nagrania
    :param fps: liczba klatek na sekundę w wideo
    """
    # 1. Inicjalizacja środowiska i modelu
    env = HillClimbEnv(max_steps=100000, debug=False)
    model = PPO.load(model_path)

    obs, info = env.reset()
    done = False
    truncated = False
    total_reward = 0.0

    images = []
    frame_count = 0

    # 2. Główna pętla nagrywania
    while not done and not truncated and frame_count < max_frames:
        # Decyzja modelu
        action, _ = model.predict(obs)
        obs, reward, done, truncated, info = env.step(action)

        # Render do okna pygame
        env.render()

        # Zrzucenie aktualnej klatki z ekranu pygame
        screen_surface = pygame.display.get_surface()
        frame_array = pygame.surfarray.array3d(screen_surface)
        # Pygame zwraca tablicę (width, height, 3), trzeba ją transponować:
        frame_array = np.transpose(frame_array, (1, 0, 2))

        images.append(frame_array)
        total_reward += reward
        frame_count += 1

    env.close()
    print(f"Test completed. Total reward: {total_reward:.2f}")

    # 3. Zapis do pliku MP4 z użyciem imageio i ffmpeg
    print(f"Saving {len(images)} frames to {output_file_mp4} as MP4...")
    # 'mp4' => imageio wewnętrznie używa imageio_ffmpeg, parametry możesz dostosować
    imageio.mimwrite(
        uri=output_file_mp4,
        ims=images,
        fps=fps,
        codec="libx264",  # możesz zmienić na inny, np. "libx265", "mpeg4" itp.
        quality=8         # jakość (0-10) - zależy od kodeka
    )
    print("MP4 saved!")

    # 4. Zapis pierwszego kadru jako PNG (przydatny np. do LaTeX itp.)
    if images:
        first_frame = images[0]  # numpy array (H, W, 3)
        print(f"Saving first frame to {output_file_png}...")
        imageio.imsave(output_file_png, first_frame)
        print("PNG saved!")


if __name__ == "__main__":
    record_run(
        model_path="quick_ppo_hill_climb.zip",
        output_file_mp4="gameplay.mp4",
        output_file_png="gameplay.png",
        max_frames=3000,
        fps=30
    )
