import flet as ft
import sqlite3
from datetime import datetime

DB_NAME = "aircraft_logbook.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS board_state (
            board_num TEXT PRIMARY KEY,
            board_model TEXT DEFAULT 'МД-М'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board_num TEXT,
            flight_date TEXT,
            hours REAL,
            fuel_used REAL,
            cycles REAL
        )
    ''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "Бортовой Журнал ВС"
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO
    
    init_db()

    # Начальные борты
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM board_state")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO board_state (board_num, board_model) VALUES (?, ?)", [
            ("76763", "МД-М"),
            ("76764", "МД"),
            ("78701", "МД-90А")
        ])
        conn.commit()
    conn.close()

    def get_boards():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT board_num, board_model FROM board_state")
        rows = cursor.fetchall()
        conn.close()
        return rows

    boards_data = get_boards()
    
    # Мобильный интерфейс
    board_dropdown = ft.Dropdown(
        label="Выберите борт ВС",
        options=[ft.dropdown.Option(b[0], text=f"{b[0]} ({b[1]})") for b in boards_data],
        value=boards_data[0][0] if boards_data else None,
    )

    hours_input = ft.TextField(label="Налет (часы)", value="2.5")
    fuel_input = ft.TextField(label="Топливо (т)", value="4.2")
    cycles_input = ft.TextField(label="Циклы", value="1")
    status_text = ft.Text("")

    def save_flight(e):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO flights (board_num, flight_date, hours, fuel_used, cycles) VALUES (?, ?, ?, ?, ?)",
                           (board_dropdown.value, datetime.now().strftime("%Y-%m-%d %H:%M"), float(hours_input.value), float(fuel_input.value), float(cycles_input.value)))
            conn.commit()
            conn.close()
            status_text.value = "✅ Сохранено!"
            status_text.color = ft.Colors.GREEN
            page.update()
        except Exception as ex:
            status_text.value = f"❌ Ошибка: {ex}"
            status_text.color = ft.Colors.RED
            page.update()

    page.add(
        ft.Text("✈️ Бортовой Журнал", size=22, weight=ft.FontWeight.BOLD),
        board_dropdown,
        ft.Divider(),
        hours_input,
        fuel_input,
        cycles_input,
        ft.Button("💾 Сохранить запись", on_click=save_flight),
        status_text
    )

if __name__ == "__main__":
    ft.app(target=main)
