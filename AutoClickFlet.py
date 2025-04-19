import flet as ft
import pyautogui
from pynput import mouse
import threading
import time

click_positions = []
recording = False
listener = None
last_click_time = 0

def start_recording(save_button):
    global recording, click_positions, listener, last_click_time
    click_positions = []
    recording = True
    last_click_time = 0

    def on_click(x, y, button, pressed):
        global recording, last_click_time
        if pressed and recording:
            last_click_time = time.time()
            click_positions.append((x, y))

    listener = mouse.Listener(on_click=on_click)
    listener.start()

def stop_recording():
    global recording, listener, last_click_time
    recording = False
    if listener:
        listener.stop()
        listener = None

    if click_positions and time.time() - last_click_time < 0.5:
        removed = click_positions.pop()

def run_clicker(delay, cycles, infinite, page, cycle_counter_text):
    count = 0
    try:
        while infinite or count < cycles:
            for pos in click_positions:
                pyautogui.click(pos[0], pos[1])
                time.sleep(delay)
            count += 1

            def update_cycle():
                cycle_counter_text.value = f"Текущий цикл: {count}"
                page.update()

            threading.Timer(0, update_cycle).start()
    except KeyboardInterrupt:
        pass

def main(page: ft.Page):
    page.window.title_bar_hidden = False
    page.window.frameless = False
    page.window.left = 200
    page.window.top = 100
    page.window_resizable = False

    cycle_counter_text = ft.Text("Текущий цикл: 0", size=16)

    record_button = ft.ElevatedButton("Записать")
    save_button = ft.ElevatedButton("Сохранить", visible=False)
    start_button = ft.ElevatedButton("Запустить")

    delay_field = ft.TextField(
        label="Задержка между нажатиями (секунды)",
        value="0.2",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    cycle_count_field = ft.TextField(
        label="Количество циклов",
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    infinite_checkbox = ft.Checkbox(label="Бесконечный цикл")

    def on_record_click(e):
        record_button.visible = False
        save_button.visible = True
        page.update()
        start_recording(save_button)

    def on_save_click(e):
        stop_recording()
        save_button.visible = False
        record_button.visible = True
        page.update()

    def on_start_click(e):
        try:
            delay = float(delay_field.value)
        except ValueError:
            delay = 0.2

        try:
            cycles = int(cycle_count_field.value)
        except ValueError:
            cycles = 1

        infinite = infinite_checkbox.value
        threading.Thread(target=run_clicker, args=(delay, cycles, infinite, page, cycle_counter_text)).start()

    record_button.on_click = on_record_click
    save_button.on_click = on_save_click
    start_button.on_click = on_start_click

    page.add(
        delay_field,
        cycle_count_field,
        infinite_checkbox,
        cycle_counter_text,
        record_button,
        save_button,
        start_button
    )

ft.app(target=main)
