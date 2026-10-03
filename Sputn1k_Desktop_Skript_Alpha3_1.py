#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" SPUTN1K V6.0 DESKTOP CLIENT Linux | PyQt6 | Telegram-style layout """

import sys
import json
import time
import threading
import os
import base64
import mimetypes
from datetime import datetime
from typing import Optional, Dict, List, Callable
import requests
import websocket
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QPushButton, QLabel, QStackedWidget, QDialog, QFormLayout,
    QMessageBox, QFileDialog, QScrollArea, QFrame, QSizePolicy, QMenu,
    QToolButton, QGraphicsDropShadowEffect, QInputDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, QSize,
    QPropertyAnimation, QEasingCurve, QPoint
)
from PyQt6.QtGui import (
    QFont, QPixmap, QIcon, QColor, QPalette,
    QTextCursor, QAction, QPainter, QBrush, QPen, QLinearGradient,
    QFontDatabase, QBitmap
)

STYLE = """
QWidget {
    background-color: #0b0e14;
    color: #e1e6f0;
    font-family: 'Segoe UI', 'Roboto', 'Ubuntu', sans-serif;
    font-size: 14px;
}
QMainWindow {
    background-color: #0b0e14;
}
QSplitter::handle {
    background-color: #1f293d;
    width: 2px;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QListWidget {
    background-color: #131722;
    border: none;
    border-right: 1px solid #1f293d;
    padding: 4px;
    outline: none;
    font-size: 14px;
}
QListWidget::item {
    background-color: #0d111a;
    border: 1px solid #1f293d;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 3px 4px;
    min-height: 44px;
}
QListWidget::item:selected {
    background-color: #1a2a3d;
    border: 1px solid #00ff88;
}
QListWidget::item:hover {
    background-color: #161b26;
    border: 1px solid #00d8ff;
}
QLineEdit {
    background-color: #0d111a;
    border: 1px solid #1f293d;
    border-radius: 20px;
    padding: 8px 16px;
    color: #e1e6f0;
    font-size: 14px;
    selection-background-color: #00ff88;
    selection-color: #000000;
}
QLineEdit:focus {
    border: 1px solid #00ff88;
}
QLineEdit::placeholder {
    color: #4a5568;
}
QPushButton {
    background-color: #1f293d;
    border: 1px solid #2a3a4d;
    border-radius: 8px;
    padding: 8px 16px;
    color: #e1e6f0;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #2a3a4d;
    border: 1px solid #00d8ff;
}
QPushButton:pressed {
    background-color: #0d111a;
}
QPushButton#sendBtn {
    background-color: #00ff88;
    color: #000000;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 16px;
    min-width: 40px;
}
QPushButton#sendBtn:hover {
    background-color: #00cc6a;
}
QPushButton#sendBtn:pressed {
    background-color: #00994f;
}
QPushButton#primaryBtn {
    background-color: #00ff88;
    color: #000000;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton#primaryBtn:hover {
    background-color: #00cc6a;
}
QPushButton#dangerBtn {
    background-color: #ff4757;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton#dangerBtn:hover {
    background-color: #cc3344;
}
QPushButton#iconBtn {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 6px;
    font-size: 18px;
    min-width: 36px;
    min-height: 36px;
}
QPushButton#iconBtn:hover {
    background-color: #1f293d;
}
QTextEdit {
    background-color: #07090e;
    border: none;
    color: #e1e6f0;
    font-size: 14px;
    selection-background-color: #00ff88;
    selection-color: #000000;
}
QScrollBar:vertical {
    background-color: #0b0e14;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #1f293d;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #2a3a4d;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #0b0e14;
    height: 8px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #1f293d;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollBar:vertical:disabled {
    background-color: #131722;
}
QMenu {
    background-color: #131722;
    border: 1px solid #1f293d;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #1a2a3d;
    color: #00ff88;
}
QDialog {
    background-color: #131722;
    border: 1px solid #1f293d;
}
QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #00ff88;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #6b7280;
}
"""


CONFIG_PATH = os.path.expanduser("~/.sputn1k_config")

# ------------------------------------------------------------------
# ШИФРОВАНИЕ СООБЩЕНИЙ И ФАЙЛОВ (Alpha 3)
# ------------------------------------------------------------------
# Текст сообщений и вложенные файлы шифруются на клиенте перед
# отправкой; сервер хранит и пересылает только шифротекст и не может
# прочитать содержимое переписки. Ключ для конкретной переписки
# выводится (PBKDF2-HMAC-SHA256) из отсортированной пары логинов
# участников + общего секрета приложения.
#
# ВАЖНО (честно предупреждаем): это НЕ полноценное end-to-end
# шифрование с обменом ключами — секрет зашит в код клиента и
# одинаков для всех установок. Это защищает переписку от чтения
# сервером/при утечке базы данных на диске, но не защитит от того,
# кто имеет доступ к исходному коду клиента и знает имена
# собеседников. Для настоящего E2E нужен отдельный обмен ключами
# (например, асимметричные ключи пользователей) — это можно добавить
# отдельным шагом.
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Общий секрет приложения. Поменяйте на свой перед реальным
# развёртыванием — все клиенты, которые должны видеть переписку друг
# друга, должны использовать один и тот же секрет.
APP_SECRET = b"ORB1T-SPUTN1K-ALPHA3-STATIC-SECRET-CHANGE-ME"
_KDF_SALT = b"orb1t_sputn1k_alpha3_salt"

ENC_TEXT_PREFIX = "ENC1:"
ENC_FILE_PREFIX = "FILEENC1:"

_fernet_cache: Dict[str, "Fernet"] = {}


def _get_chat_fernet(user_a: str, user_b: str):
    """Возвращает Fernet-ключ для переписки между двумя пользователями (порядок не важен)."""
    if not CRYPTO_AVAILABLE:
        return None
    pair_id = ":".join(sorted([
        (user_a or "").lower().strip(),
        (user_b or "").lower().strip()
    ]))
    cached = _fernet_cache.get(pair_id)
    if cached:
        return cached
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=_KDF_SALT, iterations=100_000)
    derived = kdf.derive(APP_SECRET + b"::" + pair_id.encode("utf-8"))
    key = base64.urlsafe_b64encode(derived)
    f = Fernet(key)
    _fernet_cache[pair_id] = f
    return f


def encrypt_text_for_chat(plaintext: str, user_a: str, user_b: str) -> str:
    """Шифрует текст сообщения. При недоступности cryptography возвращает текст как есть."""
    if not plaintext:
        return plaintext
    f = _get_chat_fernet(user_a, user_b)
    if not f:
        return plaintext
    token = f.encrypt(plaintext.encode("utf-8")).decode("utf-8")
    return ENC_TEXT_PREFIX + token


def decrypt_text_for_chat(ciphertext: str, user_a: str, user_b: str) -> str:
    """Расшифровывает текст. Незашифрованные (старые) сообщения возвращаются как есть."""
    if not ciphertext or not ciphertext.startswith(ENC_TEXT_PREFIX):
        return ciphertext
    f = _get_chat_fernet(user_a, user_b)
    if not f:
        return tr("crypto_unavailable")
    token = ciphertext[len(ENC_TEXT_PREFIX):]
    try:
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, Exception):
        return tr("decrypt_error")


def encrypt_bytes_for_chat(data: bytes, user_a: str, user_b: str) -> Optional[bytes]:
    f = _get_chat_fernet(user_a, user_b)
    if not f:
        return None
    return f.encrypt(data)


def decrypt_bytes_for_chat(token: bytes, user_a: str, user_b: str) -> Optional[bytes]:
    f = _get_chat_fernet(user_a, user_b)
    if not f:
        return None
    try:
        return f.decrypt(token)
    except Exception:
        return None



# ------------------------------------------------------------------
# ЛОКАЛИЗАЦИЯ / LOCALIZATION / ԼՈԿԱԼԻԶԱՑԻԱ
# Логотип "SPUTN1K" и название приложения всегда остаются на английском.
# ------------------------------------------------------------------
LANGUAGES = ["en", "ru", "hy"]
LANGUAGE_NAMES = {"en": "English", "ru": "Русский", "hy": "Հայերեն"}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "subtitle": "ORBIT MESSENGER v6.0",
        "server_ip_placeholder": "Server IP, e.g. 192.168.1.10 or 192.168.1.10:8000",
        "username_placeholder": "Login / Nickname",
        "password_placeholder": "Password",
        "login_btn": "Log In",
        "register_btn": "Register",
        "fill_fields": "Fill in login and password!",
        "login_error": "Login error",
        "no_response": "No response",
        "connection_error": "Connection error: ",
        "register_error": "Registration error: ",
        "register_result": "Registration result",
        "search_placeholder": "Search...",
        "no_contacts": "No contacts",
        "add_contact_btn": "+ Add contact",
        "add_contact_title": "Add contact",
        "add_contact_label": "Enter the user's 4-digit ID:",
        "info_title": "Info",
        "chat_placeholder": "Type a message...",
        "attached_image": "Image attached: ",
        "error_title": "Error",
        "send_error": "Send error: ",
        "select_image_title": "Select an image",
        "file_error": "File error: ",
        "settings_title": "Profile settings",
        "avatar_label": "Avatar (URL)",
        "avatar_placeholder": "Photo link",
        "nickname_label": "Nickname",
        "nickname_placeholder": "New nickname",
        "id_label": "Your ID (read-only)",
        "new_password_label": "New password",
        "new_password_placeholder": "Leave empty to keep current",
        "cancel_btn": "Cancel",
        "save_btn": "Save",
        "success_title": "Success",
        "settings_saved": "Settings saved!",
        "save_failed": "Failed to save",
        "sys_admin_console": "SYS_ADMIN CONSOLE",
        "support_console": "SUPPORT CONSOLE",
        "admin_info": "Account management | User list",
        "admin_search_placeholder": "Search by ID or nickname...",
        "logout_btn": "Log Out",
        "delete_title": "Delete",
        "delete_user_confirm": "Delete user {}?",
        "result_title": "Result",
        "rank_label": "Rank",
        "delete_tooltip": "Click to delete",
        "delete_for_me": "Delete for me",
        "delete_msg_confirm": "Delete this message for yourself only?\n(It will remain visible to the other person)",
        "delete_msg_error": "Failed to delete message",
        "language_tooltip": "Language",
        "window_title": "SPUTN1K Orbit Messenger",
        "conn_lost": "Connection error",
        "timeout_error": "Request timeout",
        "attached_file": "File attached: ",
        "select_file_title": "Select a file",
        "save_file_title": "Save file as...",
        "save_file_btn": "Save",
        "crypto_unavailable": "🔒 [Encryption unavailable: install the 'cryptography' package]",
        "decrypt_error": "🔒 [Could not decrypt this message]",
        "encryption_on": "🔒 Encryption: ON",
    },
    "ru": {
        "subtitle": "ORBIT MESSENGER v6.0",
        "server_ip_placeholder": "IP-сервера, напр. 192.168.1.10 или 192.168.1.10:8000",
        "username_placeholder": "Логин / Никнейм",
        "password_placeholder": "Пароль",
        "login_btn": "Войти",
        "register_btn": "Регистрация",
        "fill_fields": "Заполните логин и пароль!",
        "login_error": "Ошибка входа",
        "no_response": "Нет ответа",
        "connection_error": "Ошибка подключения: ",
        "register_error": "Ошибка регистрации: ",
        "register_result": "Результат регистрации",
        "search_placeholder": "Поиск...",
        "no_contacts": "Нет контактов",
        "add_contact_btn": "+ Добавить контакт",
        "add_contact_title": "Добавление",
        "add_contact_label": "Введите 4-значный ID пользователя:",
        "info_title": "Инфо",
        "chat_placeholder": "Написать сообщение...",
        "attached_image": "Прикреплено изображение: ",
        "error_title": "Ошибка",
        "send_error": "Ошибка отправки: ",
        "select_image_title": "Выберите изображение",
        "file_error": "Ошибка файла: ",
        "settings_title": "Настройки профиля",
        "avatar_label": "Аватар (URL)",
        "avatar_placeholder": "Ссылка на фото",
        "nickname_label": "Никнейм",
        "nickname_placeholder": "Новый ник",
        "id_label": "Ваш ID (только чтение)",
        "new_password_label": "Новый пароль",
        "new_password_placeholder": "Оставьте пустым, если не меняете",
        "cancel_btn": "Отмена",
        "save_btn": "Сохранить",
        "success_title": "Успех",
        "settings_saved": "Настройки сохранены!",
        "save_failed": "Не удалось сохранить",
        "sys_admin_console": "SYS_ADMIN CONSOLE",
        "support_console": "SUPPORT CONSOLE",
        "admin_info": "Управление аккаунтами | Список пользователей",
        "admin_search_placeholder": "Поиск по ID или Никнейму...",
        "logout_btn": "Выйти",
        "delete_title": "Удаление",
        "delete_user_confirm": "Удалить пользователя {}?",
        "result_title": "Результат",
        "rank_label": "Ранг",
        "delete_tooltip": "Нажмите для удаления",
        "delete_for_me": "Удалить у себя",
        "delete_msg_confirm": "Удалить это сообщение только у себя?\n(У собеседника оно останется видимым)",
        "delete_msg_error": "Не удалось удалить сообщение",
        "language_tooltip": "Язык",
        "window_title": "SPUTN1K Orbit Messenger",
        "conn_lost": "Ошибка соединения",
        "timeout_error": "Таймаут запроса",
        "attached_file": "Прикреплён файл: ",
        "select_file_title": "Выберите файл",
        "save_file_title": "Сохранить файл как...",
        "save_file_btn": "Сохранить",
        "crypto_unavailable": "🔒 [Шифрование недоступно: установите пакет 'cryptography']",
        "decrypt_error": "🔒 [Не удалось расшифровать это сообщение]",
        "encryption_on": "🔒 Шифрование: ВКЛ",
    },
    "hy": {
        "subtitle": "ORBIT MESSENGER v6.0",
        "server_ip_placeholder": "Սերվերի IP, օր. 192.168.1.10 կամ 192.168.1.10:8000",
        "username_placeholder": "Մուտքանուն / Մականուն",
        "password_placeholder": "Գաղտնաբառ",
        "login_btn": "Մուտք",
        "register_btn": "Գրանցում",
        "fill_fields": "Լրացրեք մուտքանունը և գաղտնաբառը:",
        "login_error": "Մուտքի սխալ",
        "no_response": "Պատասխան չկա",
        "connection_error": "Կապի սխալ: ",
        "register_error": "Գրանցման սխալ: ",
        "register_result": "Գրանցման արդյունք",
        "search_placeholder": "Փնտրել...",
        "no_contacts": "Կոնտակտներ չկան",
        "add_contact_btn": "+ Ավելացնել կոնտակտ",
        "add_contact_title": "Ավելացում",
        "add_contact_label": "Մուտքագրեք օգտատիրոջ 4-նիշանոց ID-ն.",
        "info_title": "Տեղեկություն",
        "chat_placeholder": "Գրել հաղորդագրություն...",
        "attached_image": "Կցված է նկար՝ ",
        "error_title": "Սխալ",
        "send_error": "Ուղարկման սխալ: ",
        "select_image_title": "Ընտրեք նկարը",
        "file_error": "Ֆայլի սխալ: ",
        "settings_title": "Պրոֆիլի կարգավորումներ",
        "avatar_label": "Ավատար (URL)",
        "avatar_placeholder": "Նկարի հղում",
        "nickname_label": "Մականուն",
        "nickname_placeholder": "Նոր մականուն",
        "id_label": "Ձեր ID-ն (միայն ընթերցում)",
        "new_password_label": "Նոր գաղտնաբառ",
        "new_password_placeholder": "Թողեք դատարկ, եթե չեք փոխում",
        "cancel_btn": "Չեղարկել",
        "save_btn": "Պահպանել",
        "success_title": "Հաջողություն",
        "settings_saved": "Կարգավորումները պահպանվեցին!",
        "save_failed": "Չհաջողվեց պահպանել",
        "sys_admin_console": "SYS_ADMIN CONSOLE",
        "support_console": "SUPPORT CONSOLE",
        "admin_info": "Հաշիվների կառավարում | Օգտատերերի ցանկ",
        "admin_search_placeholder": "Փնտրել ըստ ID կամ մականվան...",
        "logout_btn": "Ելք",
        "delete_title": "Ջնջում",
        "delete_user_confirm": "Ջնջե՞լ {} օգտատիրոջը:",
        "result_title": "Արդյունք",
        "rank_label": "Աստիճան",
        "delete_tooltip": "Սեղմեք ջնջելու համար",
        "delete_for_me": "Ջնջել ինձ մոտ",
        "delete_msg_confirm": "Ջնջե՞լ այս հաղորդագրությունը միայն ձեզ մոտ:\n(Զրուցակցի մոտ այն կմնա)",
        "delete_msg_error": "Չհաջողվեց ջնջել հաղորդագրությունը",
        "language_tooltip": "Լեզու",
        "window_title": "SPUTN1K Orbit Messenger",
        "conn_lost": "Կապի սխալ",
        "timeout_error": "Հարցման ժամանակը լրացավ",
        "attached_file": "Կցված է ֆայլ՝ ",
        "select_file_title": "Ընտրեք ֆայլը",
        "save_file_title": "Պահպանել ֆայլը որպես...",
        "save_file_btn": "Պահպանել",
        "crypto_unavailable": "🔒 [Գաղտնագրումը հասանելի չէ. տեղադրեք 'cryptography' փաթեթը]",
        "decrypt_error": "🔒 [Չհաջողվեց վերծանել այս հաղորդագրությունը]",
        "encryption_on": "🔒 Գաղտնագրում՝ ՄԻԱՑՎԱԾ",
    },
}

_current_lang = "en"


def set_language(lang: str):
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def tr(key: str) -> str:
    return TRANSLATIONS.get(_current_lang, TRANSLATIONS["en"]).get(key, key)


def load_app_config() -> dict:
    """Читает конфиг (JSON: {server_ip, lang}). Совместим со старым форматом (просто IP строкой)."""
    cfg = {"server_ip": "127.0.0.1", "lang": "en"}
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            if raw.startswith("{"):
                data = json.loads(raw)
                cfg["server_ip"] = data.get("server_ip", cfg["server_ip"])
                cfg["lang"] = data.get("lang", cfg["lang"])
            elif raw:
                cfg["server_ip"] = raw
    except Exception:
        pass
    return cfg


def save_app_config(server_ip: str, lang: str):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"server_ip": server_ip, "lang": lang}, f, ensure_ascii=False)
    except Exception:
        pass


class Colors:
    BG = "#0b0e14"
    PANEL = "#131722"
    ACCENT_GREEN = "#00ff88"
    ACCENT_BLUE = "#00d8ff"
    ACCENT_RED = "#ff4757"
    ACCENT_GOLD = "#ffd700"
    TEXT = "#e1e6f0"
    TEXT_SECONDARY = "#6b7280"
    BORDER = "#1f293d"
    CARD = "#0d111a"
    CARD_HOVER = "#161b26"
    CARD_SELECTED = "#1a2a3d"
    CHAT_BG = "#07090e"
    SELF_MSG = "#0d2a1a"
    OTHER_MSG = "#161b26"


def parse_server_address(raw: str) -> "tuple[str, int, int]":
    """
    Разбирает адрес сервера, введённый пользователем: "IP" или "IP:PORT".
    Возвращает (ip, http_port, ws_port). Если порт не указан — 7272/7273
    (порты сервера по умолчанию). Если указан свой HTTP-порт (например,
    сервер запущен с --http-port 8000), WS-порт берётся как http_port + 1
    — это соответствует умолчанию сервера (7273 = 7272 + 1). Если вы
    запускали сервер с --ws-port на другом смещении, введите его отдельно
    через двоеточие: "IP:HTTP_PORT:WS_PORT".
    """
    raw = (raw or "").strip()
    if not raw:
        return "127.0.0.1", 7272, 7273
    parts = raw.split(":")
    ip = parts[0].strip() or "127.0.0.1"
    if len(parts) == 1:
        return ip, 7272, 7273
    try:
        http_port = int(parts[1])
    except (ValueError, IndexError):
        return ip, 7272, 7273
    if len(parts) >= 3:
        try:
            ws_port = int(parts[2])
        except ValueError:
            ws_port = http_port + 1
    else:
        ws_port = http_port + 1
    return ip, http_port, ws_port


class WebSocketClient(QThread):
    message_received = pyqtSignal(dict)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, server_ip: str, username: str):
        super().__init__()
        self.server_ip = server_ip
        self.username = username
        self.ws: Optional[websocket.WebSocketApp] = None
        self.running = True

    def run(self):
        ip, _http_port, ws_port = parse_server_address(self.server_ip)
        url = f"ws://{ip}:{ws_port}"
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_open=self._on_open,
            on_close=self._on_close,
            on_error=self._on_error
        )
        self.ws.run_forever(ping_interval=30, ping_timeout=10)

    def _on_open(self, ws):
        ws.send(json.dumps({"type": "auth", "user": self.username}))
        self.connected.emit()

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("type") in ("new_message", "auth_ok"):
                self.message_received.emit(data)
        except json.JSONDecodeError:
            pass

    def _on_close(self, ws, close_status_code, close_msg):
        self.disconnected.emit()
        if self.running:
            time.sleep(3)
            if self.running:
                self.run()

    def _on_error(self, ws, error):
        pass

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()


class MessageBubble(QWidget):
    delete_requested = pyqtSignal(str)

    def __init__(self, msg_data: dict, is_self: bool, my_username: str = "", chat_partner: str = "", parent=None):
        super().__init__(parent)
        self.msg_data = msg_data
        self.is_self = is_self
        self.my_username = my_username
        self.chat_partner = chat_partner
        self._setup_ui()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        msg_id = self.msg_data.get("id")
        if not msg_id:
            return
        menu = QMenu(self)
        delete_action = menu.addAction(f"🗑 {tr('delete_for_me')}")
        action = menu.exec(self.mapToGlobal(pos))
        if action == delete_action:
            reply = QMessageBox.question(
                self, tr("delete_title"), tr("delete_msg_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_requested.emit(msg_id)

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)

        bubble = QFrame()
        bubble.setObjectName("bubble")

        bg = Colors.SELF_MSG if self.is_self else Colors.OTHER_MSG
        bubble.setStyleSheet(f"""
            QFrame#bubble {{
                background-color: {bg};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 8px 14px;
                max-width: 500px;
            }}
        """)
        b_layout = QVBoxLayout()
        b_layout.setSpacing(4)
        b_layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.setSpacing(8)
        if not self.is_self:
            name_label = QLabel(self.msg_data.get("from", ""))
            name_label.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-weight: bold; font-size: 12px;")
            header.addWidget(name_label)

        time_label = QLabel(self.msg_data.get("time", ""))
        time_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 10px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(time_label)
        header.addStretch()
        b_layout.addLayout(header)

        text = self.msg_data.get("text", "")
        if text:
            display_text = decrypt_text_for_chat(text, self.my_username, self.chat_partner)
            text_label = QLabel(display_text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(f"color: {Colors.TEXT}; font-size: 14px; background: transparent;")
            text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            b_layout.addWidget(text_label)

        attachment = self.msg_data.get("image")
        if attachment and attachment.startswith(ENC_FILE_PREFIX):
            self._render_encrypted_attachment(attachment, b_layout)
        elif attachment and attachment.startswith("data:image"):
            # Старое незашифрованное изображение (совместимость со старыми сообщениями)
            try:
                b64_data = attachment.split(",")[1] if "," in attachment else attachment
                img_bytes = base64.b64decode(b64_data)
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes)

                scaled = pixmap.scaled(
                    300, 300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setStyleSheet("background: transparent; border-radius: 8px;")
                b_layout.addWidget(img_label)
            except Exception:
                pass

        bubble.setLayout(b_layout)

        if self.is_self:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet("background: transparent;")

    def _render_encrypted_attachment(self, attachment: str, b_layout: QVBoxLayout):
        """Расшифровывает и отображает вложение: картинку — превью, любой другой файл — карточку с кнопкой сохранения."""
        try:
            envelope = json.loads(attachment[len(ENC_FILE_PREFIX):])
            enc_bytes = base64.b64decode(envelope["data"])
            raw_bytes = decrypt_bytes_for_chat(enc_bytes, self.my_username, self.chat_partner)
            if raw_bytes is None:
                raise ValueError("decrypt failed")

            mime = envelope.get("mime", "application/octet-stream")
            filename = envelope.get("filename", "file")

            if mime.startswith("image/"):
                pixmap = QPixmap()
                pixmap.loadFromData(raw_bytes)
                scaled = pixmap.scaled(
                    300, 300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setStyleSheet("background: transparent; border-radius: 8px;")
                b_layout.addWidget(img_label)
            else:
                b_layout.addWidget(self._build_file_chip(filename, raw_bytes))
        except Exception:
            err_label = QLabel(tr("decrypt_error"))
            err_label.setStyleSheet(f"color: {Colors.ACCENT_RED}; font-size: 12px; background: transparent;")
            b_layout.addWidget(err_label)

    def _build_file_chip(self, filename: str, raw_bytes: bytes) -> QWidget:
        """Карточка вложенного файла (не изображения): иконка, имя, размер, кнопка сохранения."""
        chip = QFrame()
        chip.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255,255,255,0.04);
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
            }}
        """)
        row = QHBoxLayout()
        row.setContentsMargins(8, 8, 8, 8)
        row.setSpacing(10)

        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 22px; background: transparent;")
        row.addWidget(icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        name_label = QLabel(filename)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"color: {Colors.TEXT}; font-size: 13px; background: transparent;")
        size_kb = len(raw_bytes) / 1024
        size_text = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
        size_label = QLabel(size_text)
        size_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 10px; background: transparent;")
        info_layout.addWidget(name_label)
        info_layout.addWidget(size_label)
        row.addLayout(info_layout)
        row.addStretch()

        save_btn = QPushButton("💾")
        save_btn.setObjectName("iconBtn")
        save_btn.setFixedSize(32, 32)
        save_btn.setToolTip(tr("save_file_btn"))
        save_btn.clicked.connect(lambda: self._save_attached_file(filename, raw_bytes))
        row.addWidget(save_btn)

        chip.setLayout(row)
        return chip

    def _save_attached_file(self, filename: str, raw_bytes: bytes):
        path, _ = QFileDialog.getSaveFileName(self, tr("save_file_title"), filename)
        if path:
            try:
                with open(path, "wb") as f:
                    f.write(raw_bytes)
            except Exception as e:
                QMessageBox.warning(self, tr("error_title"), f"{tr('file_error')}{e}")


class ChatView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_target = ""
        self.messages_cache = []
        self._my_username = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PANEL};
                border-bottom: 1px solid {Colors.BORDER};
                padding: 0px;
            }}
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 12, 16, 12)

        self.back_btn = QPushButton("←")
        self.back_btn.setObjectName("iconBtn")
        self.back_btn.setFixedSize(36, 36)
        self.back_btn.clicked.connect(self._on_back)
        self.back_btn.hide()
        header_layout.addWidget(self.back_btn)

        self.target_avatar = QLabel()
        self.target_avatar.setFixedSize(40, 40)
        self.target_avatar.setStyleSheet(f"""
            background-color: {Colors.CARD};
            border: 2px solid {Colors.ACCENT_GREEN};
            border-radius: 20px;
        """)
        header_layout.addWidget(self.target_avatar)

        self.target_name = QLabel(" ")
        self.target_name.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {Colors.TEXT};
            background: transparent;
        """)
        header_layout.addWidget(self.target_name)

        self.online_status = QLabel("")
        self.online_status.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        header_layout.addWidget(self.online_status)
        header_layout.addStretch()

        self.encryption_indicator = QLabel(tr("encryption_on") if CRYPTO_AVAILABLE else tr("crypto_unavailable"))
        self.encryption_indicator.setStyleSheet(
            f"font-size: 10px; color: {Colors.ACCENT_GREEN if CRYPTO_AVAILABLE else Colors.ACCENT_RED}; background: transparent;"
        )
        header_layout.addWidget(self.encryption_indicator)

        self.header.setLayout(header_layout)
        layout.addWidget(self.header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"background-color: {Colors.CHAT_BG}; border: none;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet(f"background-color: {Colors.CHAT_BG};")
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setSpacing(2)
        self.messages_layout.setContentsMargins(8, 8, 8, 8)
        self.messages_layout.addStretch()
        self.messages_container.setLayout(self.messages_layout)

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PANEL};
                border-top: 1px solid {Colors.BORDER};
            }}
        """)
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(8)

        self.file_btn = QPushButton("📎")
        self.file_btn.setObjectName("iconBtn")
        self.file_btn.setFixedSize(40, 40)
        self.file_btn.setToolTip(tr("select_file_title"))
        self.file_btn.clicked.connect(self._select_file)
        input_layout.addWidget(self.file_btn)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(tr("chat_placeholder"))
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)

        input_frame.setLayout(input_layout)
        layout.addWidget(input_frame)

        self.image_status = QLabel("")
        self.image_status.setStyleSheet(f"color: {Colors.ACCENT_GREEN}; font-size: 11px; padding: 2px 16px; background-color: {Colors.CARD};")
        self.image_status.hide()
        layout.addWidget(self.image_status)

        self.setLayout(layout)

        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_messages)
        self.poll_timer.start(3000)
        self._pending_file_payload = None

    def set_target(self, target: str):
        self.current_target = target
        self.target_name.setText(target)
        self.back_btn.show()
        if target:
            self._load_history()
        else:
            self._clear_messages()

    def clear(self):
        self.current_target = ""
        self.target_name.setText(" ")
        self.online_status.setText("")
        self.back_btn.hide()
        self._clear_messages()

    def on_new_message(self, data: dict):
        if self.current_target:
            msg_from = data.get("from", "").lower()
            target_lower = self.current_target.lower()
            if msg_from == target_lower or msg_from == self._get_my_username().lower():
                self._load_history()

    def _get_my_username(self) -> str:
        return self._my_username

    def set_my_username(self, username: str):
        self._my_username = username

    def _load_history(self):
        if not self.current_target:
            return
        try:
            main_window = self.window()
            if hasattr(main_window, '_api_request'):
                resp = main_window._api_request({
                    "action": "get_chat",
                    "from_user": self._get_my_username(),
                    "target": self.current_target
                })
                if resp and resp.get("status") == "success":
                    history = resp.get("history", [])
                    self._render_messages(history)
        except Exception:
            pass

    def _render_messages(self, history: list):
        if history == self.messages_cache:
            return
        self.messages_cache = history[:]
        self._clear_messages()

        my_username = self._get_my_username()
        for msg in history:
            is_self = msg.get("from", "").lower() == my_username.lower()
            bubble = MessageBubble(msg, is_self, my_username=my_username, chat_partner=self.current_target)
            bubble.delete_requested.connect(self._delete_message)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

        QTimer.singleShot(100, self._scroll_to_bottom)

    def _clear_messages(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self.messages_cache = []

    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _send_message(self):
        text = self.input_field.text().strip()
        if not text and not self._pending_file_payload:
            return
        try:
            main_window = self.window()
            if hasattr(main_window, '_api_request'):
                my_username = self._get_my_username()
                enc_text = encrypt_text_for_chat(text, my_username, self.current_target) if text else text
                payload = {
                    "action": "send_msg",
                    "from_user": my_username,
                    "target": self.current_target,
                    "text": enc_text,
                    "image": self._pending_file_payload
                }
                resp = main_window._api_request(payload)
                if resp and resp.get("status") == "success":
                    self.input_field.clear()
                    self._pending_file_payload = None
                    self.image_status.hide()
                    self._load_history()
        except Exception as e:
            QMessageBox.warning(self, tr("error_title"), f"{tr('send_error')}{e}")

    def _select_file(self):
        """Выбор и прикрепление файла любого формата (шифруется перед отправкой)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("select_file_title"), "", "All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                mime, _ = mimetypes.guess_type(file_path)
                mime = mime or "application/octet-stream"
                filename = os.path.basename(file_path)

                my_username = self._get_my_username()
                encrypted = encrypt_bytes_for_chat(raw_bytes, my_username, self.current_target)
                if encrypted is not None:
                    envelope = {
                        "filename": filename,
                        "mime": mime,
                        "data": base64.b64encode(encrypted).decode("utf-8")
                    }
                    self._pending_file_payload = ENC_FILE_PREFIX + json.dumps(envelope)
                else:
                    # cryptography не установлена — предупреждаем и всё равно
                    # прикладываем файл (без шифрования), чтобы не терять функциональность
                    QMessageBox.warning(self, tr("error_title"), tr("crypto_unavailable"))
                    b64 = base64.b64encode(raw_bytes).decode('utf-8')
                    self._pending_file_payload = f"data:{mime};base64,{b64}"

                self.image_status.setText(f"{tr('attached_file')}{filename}")
                self.image_status.show()
            except Exception as e:
                QMessageBox.warning(self, tr("error_title"), f"{tr('file_error')}{e}")

    def _poll_messages(self):
        if self.current_target:
            self._load_history()

    def _delete_message(self, msg_id: str):
        """Удалить сообщение только у текущего пользователя ("у себя")."""
        try:
            main_window = self.window()
            if hasattr(main_window, '_api_request'):
                resp = main_window._api_request({
                    "action": "delete_message",
                    "from_user": self._get_my_username(),
                    "target": self.current_target,
                    "msg_id": msg_id
                })
                if resp and resp.get("status") == "success":
                    self._load_history()
                else:
                    QMessageBox.warning(
                        self, tr("error_title"),
                        (resp or {}).get("info", tr("delete_msg_error"))
                    )
        except Exception as e:
            QMessageBox.warning(self, tr("error_title"), f"{tr('delete_msg_error')}: {e}")

    def _on_back(self):
        self.clear()
        parent = self.parent()
        while parent and not isinstance(parent, MainWindow):
            parent = parent.parent()
        if parent and hasattr(parent, 'show_contacts'):
            parent.show_contacts()

    def retranslate_ui(self):
        self.input_field.setPlaceholderText(tr("chat_placeholder"))
        self.file_btn.setToolTip(tr("select_file_title"))
        self.encryption_indicator.setText(tr("encryption_on") if CRYPTO_AVAILABLE else tr("crypto_unavailable"))


class ContactsWidget(QWidget):
    contact_selected = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PANEL};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(12, 12, 12, 8)
        header_layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(42, 42)
        self.avatar_label.setStyleSheet(f"""
            background-color: {Colors.CARD};
            border: 2px solid {Colors.ACCENT_GREEN};
            border-radius: 21px;
        """)
        top_row.addWidget(self.avatar_label)

        self.nickname_label = QLabel("...")
        self.nickname_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {Colors.TEXT};
            background: transparent;
        """)
        top_row.addWidget(self.nickname_label)
        top_row.addStretch()

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("iconBtn")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.clicked.connect(self._open_settings)
        top_row.addWidget(self.settings_btn)

        self.admin_btn = QPushButton("🛡")
        self.admin_btn.setObjectName("iconBtn")
        self.admin_btn.setFixedSize(36, 36)
        self.admin_btn.clicked.connect(self._open_admin)
        self.admin_btn.hide()
        top_row.addWidget(self.admin_btn)

        self.lang_btn = QToolButton()
        self.lang_btn.setText("🌐")
        self.lang_btn.setObjectName("iconBtn")
        self.lang_btn.setFixedSize(36, 36)
        self.lang_btn.setToolTip(tr("language_tooltip"))
        self.lang_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._build_lang_menu()
        top_row.addWidget(self.lang_btn)

        self.logout_btn = QPushButton("🚪")
        self.logout_btn.setObjectName("iconBtn")
        self.logout_btn.setFixedSize(36, 36)
        self.logout_btn.clicked.connect(self._logout)
        top_row.addWidget(self.logout_btn)

        header_layout.addLayout(top_row)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("search_placeholder"))
        self.search_input.textChanged.connect(self._filter_contacts)
        header_layout.addWidget(self.search_input)

        self.header.setLayout(header_layout)
        layout.addWidget(self.header)

        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self._on_contact_clicked)
        layout.addWidget(self.contacts_list)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(12, 8, 12, 12)

        self.add_btn = QPushButton(tr("add_contact_btn"))
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.clicked.connect(self._add_contact)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 2px dashed {Colors.BORDER};
                border-radius: 8px;
                padding: 12px;
                color: {Colors.TEXT_SECONDARY};
                font-size: 13px;
            }}
            QPushButton:hover {{
                border: 2px dashed {Colors.ACCENT_GREEN};
                color: {Colors.ACCENT_GREEN};
            }}
        """)
        btn_layout.addWidget(self.add_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self._on_settings_callback = None
        self._on_admin_callback = None
        self._on_logout_callback = None
        self._api_request_func = None
        self._current_user = ""
        self._user_role = "user"
        self._user_data = {}

    def _build_lang_menu(self):
        menu = QMenu(self)
        for code in LANGUAGES:
            action = menu.addAction(LANGUAGE_NAMES[code])
            action.setCheckable(True)
            action.setChecked(code == get_language())
            action.triggered.connect(lambda checked, c=code: self._set_language(c))
        self.lang_btn.setMenu(menu)

    def _set_language(self, code: str):
        set_language(code)
        self._build_lang_menu()
        self.retranslate_ui()
        self.language_changed.emit(code)

    def set_callbacks(self, on_settings, on_admin, on_logout):
        self._on_settings_callback = on_settings
        self._on_admin_callback = on_admin
        self._on_logout_callback = on_logout

    def set_api_func(self, func):
        self._api_request_func = func

    def update_user_info(self, username: str, role: str, user_data: dict, friends: list):
        self._current_user = username
        self._user_role = role
        self._user_data = user_data
        self.nickname_label.setText(username)
        self.admin_btn.setVisible(role == 'admin')

        avatar_url = user_data.get("avatar", "")
        if avatar_url:
            self._load_avatar(avatar_url)

        self._update_contacts(friends)

    def _load_avatar(self, url: str):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(resp.content)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        42, 42,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    mask = QBitmap(scaled.size())
                    mask.fill(Qt.GlobalColor.color0)
                    painter = QPainter(mask)
                    painter.setBrush(QBrush(Qt.GlobalColor.color1))
                    painter.setPen(QPen(Qt.GlobalColor.color1))
                    painter.drawEllipse(0, 0, scaled.width(), scaled.height())
                    painter.end()
                    scaled.setMask(mask)
                    self.avatar_label.setPixmap(scaled)
        except Exception:
            pass

    def retranslate_ui(self):
        self.lang_btn.setToolTip(tr("language_tooltip"))
        self.search_input.setPlaceholderText(tr("search_placeholder"))
        self.add_btn.setText(tr("add_contact_btn"))
        self._update_contacts(self._last_friends if hasattr(self, '_last_friends') else [])

    def _update_contacts(self, friends: list):
        self._last_friends = friends
        self.contacts_list.clear()
        if not friends:
            item = QListWidgetItem(tr("no_contacts"))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.contacts_list.addItem(item)
            return

        for friend in friends:
            item = QListWidgetItem(f" 👤 {friend}")
            item.setData(Qt.ItemDataRole.UserRole, friend)
            self.contacts_list.addItem(item)

    def _filter_contacts(self, text: str):
        for i in range(self.contacts_list.count()):
            item = self.contacts_list.item(i)
            if item:
                item.setHidden(text.lower() not in item.text().lower() if text else False)

    def _on_contact_clicked(self, item):
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return
        friend = item.data(Qt.ItemDataRole.UserRole)
        if friend:
            self.contact_selected.emit(friend)

    def _add_contact(self):
        if not self._api_request_func:
            return
        user_id, ok = QInputDialog.getText(
            self, tr("add_contact_title"), tr("add_contact_label"), text=""
        )
        if ok and user_id:
            resp = self._api_request_func({
                "action": "add_friend_by_id",
                "from_user": self._current_user,
                "target_id": user_id.strip()
            })
            if resp:
                QMessageBox.information(self, tr("info_title"), resp.get("info", ""))
                if resp.get("status") == "success":
                    self._update_contacts(resp.get("friends", []))

    def _open_settings(self):
        if self._on_settings_callback:
            self._on_settings_callback()

    def _open_admin(self):
        if self._on_admin_callback:
            self._on_admin_callback()

    def _logout(self):
        if self._on_logout_callback:
            self._on_logout_callback()


class AuthWidget(QWidget):
    login_success = pyqtSignal(str, str, dict, list)
    language_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._api_request_func = None

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.addStretch()
        self.lang_btn = QToolButton()
        self.lang_btn.setText("🌐")
        self.lang_btn.setObjectName("iconBtn")
        self.lang_btn.setFixedSize(36, 36)
        self.lang_btn.setToolTip(tr("language_tooltip"))
        self.lang_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._build_lang_menu()
        top_row.addWidget(self.lang_btn)
        layout.addLayout(top_row)

        layout.addStretch()

        # Логотип и имя приложения всегда остаются на английском
        logo_label = QLabel("SPUTN1K")
        logo_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 800;
            color: {Colors.ACCENT_GREEN};
            letter-spacing: 6px;
            background: transparent;
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        self.subtitle = QLabel(tr("subtitle"))
        self.subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: {Colors.TEXT_SECONDARY};
            letter-spacing: 4px;
            background: transparent;
        """)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle)
        layout.addSpacing(30)

        self.server_ip = QLineEdit()
        self.server_ip.setPlaceholderText(tr("server_ip_placeholder"))
        self.server_ip.setText("127.0.0.1")
        layout.addWidget(self.server_ip)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(tr("username_placeholder"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(tr("password_placeholder"))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._login)
        layout.addWidget(self.password_input)
        layout.addSpacing(8)

        self.login_btn = QPushButton(tr("login_btn"))
        self.login_btn.setObjectName("primaryBtn")
        self.login_btn.clicked.connect(self._login)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton(tr("register_btn"))
        self.register_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Colors.ACCENT_BLUE};
                border-radius: 8px;
                padding: 10px 24px;
                color: {Colors.ACCENT_BLUE};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 216, 255, 0.1);
            }}
        """)
        self.register_btn.clicked.connect(self._register)
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.register_btn)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-size: 13px; background: transparent;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addStretch()

        saved_ip = QApplication.instance().property('server_ip')
        if saved_ip:
            self.server_ip.setText(saved_ip)
        self.setLayout(layout)

    def _build_lang_menu(self):
        menu = QMenu(self)
        for code in LANGUAGES:
            action = menu.addAction(LANGUAGE_NAMES[code])
            action.setCheckable(True)
            action.setChecked(code == get_language())
            action.triggered.connect(lambda checked, c=code: self._set_language(c))
        self.lang_btn.setMenu(menu)

    def _set_language(self, code: str):
        set_language(code)
        self._build_lang_menu()
        self.retranslate_ui()
        self.language_changed.emit(code)

    def retranslate_ui(self):
        self.lang_btn.setToolTip(tr("language_tooltip"))
        self.subtitle.setText(tr("subtitle"))
        self.server_ip.setPlaceholderText(tr("server_ip_placeholder"))
        self.username_input.setPlaceholderText(tr("username_placeholder"))
        self.password_input.setPlaceholderText(tr("password_placeholder"))
        self.login_btn.setText(tr("login_btn"))
        self.register_btn.setText(tr("register_btn"))

    def set_api_func(self, func):
        self._api_request_func = func

    def _get_server_ip(self) -> str:
        ip = self.server_ip.text().strip()
        if not ip:
            ip = "127.0.0.1"
        QApplication.instance().setProperty('server_ip', ip)
        save_app_config(ip, get_language())
        return ip

    def _login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText(tr("fill_fields"))
            return
        try:
            self._get_server_ip()
            resp = self._api_request_func({
                "action": "login",
                "user": username,
                "pass": password
            })
            if resp and resp.get("status") == "success":
                role = resp.get("role", "user")
                user_data = resp.get("user_data", {})
                friends = resp.get("friends", [])
                self.login_success.emit(username, role, user_data, friends)
            else:
                self.status_label.setText(resp.get("info", tr("login_error")) if resp else tr("no_response"))
        except Exception as e:
            self.status_label.setText(f"{tr('connection_error')}{e}")

    def _register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText(tr("fill_fields"))
            return
        try:
            self._get_server_ip()
            resp = self._api_request_func({
                "action": "register",
                "user": username,
                "pass": password
            })
            self.status_label.setText(resp.get("info", tr("register_result")) if resp else tr("no_response"))
        except Exception as e:
            self.status_label.setText(f"{tr('register_error')}{e}")


class SettingsDialog(QDialog):
    def __init__(self, current_user: str, user_data: dict, api_func, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._user_data = user_data
        self._api_func = api_func
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(tr("settings_title"))
        self.setFixedSize(400, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.PANEL};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel(tr("settings_title"))
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        avatar_label = QLabel(tr("avatar_label"))
        avatar_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        layout.addWidget(avatar_label)

        self.avatar_input = QLineEdit()
        self.avatar_input.setPlaceholderText(tr("avatar_placeholder"))
        self.avatar_input.setText(self._user_data.get("avatar", ""))
        layout.addWidget(self.avatar_input)

        nick_label = QLabel(tr("nickname_label"))
        nick_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        layout.addWidget(nick_label)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText(tr("nickname_placeholder"))
        self.nick_input.setText(self._current_user)
        layout.addWidget(self.nick_input)

        id_label = QLabel(tr("id_label"))
        id_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        layout.addWidget(id_label)

        id_input = QLineEdit()
        id_input.setText(self._user_data.get("id", ""))
        id_input.setEnabled(False)
        id_input.setStyleSheet("opacity: 0.5;")
        layout.addWidget(id_input)

        pass_label = QLabel(tr("new_password_label"))
        pass_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        layout.addWidget(pass_label)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText(tr("new_password_placeholder"))
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton(tr("cancel_btn"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 10px 24px;
                color: {Colors.TEXT};
            }}
            QPushButton:hover {{ border-color: {Colors.ACCENT_RED}; }}
        """)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton(tr("save_btn"))
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _save(self):
        nick = self.nick_input.text().strip()
        password = self.pass_input.text()
        avatar = self.avatar_input.text().strip()
        resp = self._api_func({
            "action": "save_settings",
            "from_user": self._current_user,
            "new_nick": nick,
            "new_pass": password,
            "new_avatar": avatar
        })
        if resp and resp.get("status") == "success":
            QMessageBox.information(self, tr("success_title"), tr("settings_saved"))
            self.done(1)
        else:
            QMessageBox.warning(self, tr("error_title"), resp.get("info", tr("save_failed")) if resp else tr("error_title"))


class AdminPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._api_func = None
        self._current_user = ""
        self._users_list = {}

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PANEL};
                border-bottom: 2px solid {Colors.ACCENT_GOLD};
            }}
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_row = QHBoxLayout()
        self.console_title = QLabel(tr("sys_admin_console"))
        self.console_title.setStyleSheet(f"color: {Colors.ACCENT_GOLD}; font-weight: bold; font-size: 16px; background: transparent;")
        title_row.addWidget(self.console_title)
        title_row.addStretch()

        self.exit_btn = QPushButton(tr("logout_btn"))
        self.exit_btn.setObjectName("dangerBtn")
        self.exit_btn.clicked.connect(self._on_exit)
        title_row.addWidget(self.exit_btn)

        header_layout.addLayout(title_row)

        self.info_label = QLabel(tr("admin_info"))
        self.info_label.setStyleSheet(f"color: {Colors.ACCENT_GREEN}; font-size: 11px; background: transparent;")
        header_layout.addWidget(self.info_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("admin_search_placeholder"))
        self.search_input.textChanged.connect(self._filter_users)
        header_layout.addWidget(self.search_input)

        self.header.setLayout(header_layout)
        layout.addWidget(self.header)

        self.users_list = QListWidget()
        self.users_list.itemClicked.connect(self._on_user_clicked)
        layout.addWidget(self.users_list)

        self.setLayout(layout)
        self._on_exit_callback = None

    def set_callbacks(self, on_exit):
        self._on_exit_callback = on_exit

    def set_api_func(self, func):
        self._api_func = func

    def update_users(self, users_list: dict, current_user: str):
        self._users_list = users_list
        self._current_user = current_user
        is_sys_admin = (current_user == 'sys_adm1n')
        if is_sys_admin:
            self.console_title.setText(tr("sys_admin_console"))
        else:
            self.console_title.setText(tr("support_console"))

        self.users_list.clear()
        for username, u_data in users_list.items():
            rank = u_data.get("rank", 1)
            user_id = u_data.get("id", "N/A")
            is_admin = rank >= 3 or username in ('sys_adm1n', 'SYSTEM_MANAGER')
            badge = "👑 ADMIN" if is_admin else "👤 USER"
            display_text = f"{badge} {username} | ID: {user_id} | {tr('rank_label')}: {rank}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, username)

            if is_admin:
                item.setForeground(QColor(Colors.ACCENT_GOLD))
            else:
                item.setForeground(QColor(Colors.TEXT))

            if is_sys_admin and username != current_user:
                item.setToolTip(tr("delete_tooltip"))

            self.users_list.addItem(item)

    def retranslate_ui(self):
        self.exit_btn.setText(tr("logout_btn"))
        self.info_label.setText(tr("admin_info"))
        self.search_input.setPlaceholderText(tr("admin_search_placeholder"))
        if self._users_list:
            self.update_users(self._users_list, self._current_user)

    def _filter_users(self, text: str):
        for i in range(self.users_list.count()):
            item = self.users_list.item(i)
            if item:
                item.setHidden(text.lower() not in item.text().lower() if text else False)

    def _on_user_clicked(self, item):
        username = item.data(Qt.ItemDataRole.UserRole)
        if not username or username == self._current_user:
            return
        if self._current_user != 'sys_adm1n':
            return
        reply = QMessageBox.question(
            self, tr("delete_title"), tr("delete_user_confirm").format(username),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            resp = self._api_func({
                "action": "delete_user",
                "from_user": self._current_user,
                "target_user": username
            })
            if resp:
                QMessageBox.information(self, tr("result_title"), resp.get("info", ""))
                if resp.get("status") == "success":
                    self.update_users(resp.get("users_list", {}), self._current_user)

    def _on_exit(self):
        if self._on_exit_callback:
            self._on_exit_callback()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._current_user = ""
        self._user_role = "user"
        self._user_data = {}
        self._friends = []

        # Загружаем сохранённый IP и язык ДО построения интерфейса,
        # чтобы виджеты сразу создавались с нужным переводом
        cfg = load_app_config()
        self._server_ip = cfg.get("server_ip", "127.0.0.1")
        set_language(cfg.get("lang", "en"))

        self._ws_client: Optional[WebSocketClient] = None
        self._setup_window()
        self._setup_ui()
        self._apply_loaded_config()

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_connection_status)
        self._status_timer.start(10000)

    def _setup_window(self):
        # Название приложения всегда остаётся на английском
        self.setWindowTitle(tr("window_title"))
        self.setMinimumSize(900, 600)
        self.resize(1100, 720)

        screen = QApplication.primaryScreen()
        if screen:
            center = screen.availableGeometry().center()
            geo = self.frameGeometry()
            geo.moveCenter(center)
            self.move(geo.topLeft())
        self.setStyleSheet(STYLE)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()

        self.auth_widget = AuthWidget()
        self.auth_widget.set_api_func(self._api_request)
        self.auth_widget.login_success.connect(self._on_login_success)
        self.auth_widget.language_changed.connect(self._on_language_changed)
        self.stack.addWidget(self.auth_widget)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet(f"background-color: {Colors.BG};")
        main_screen_layout = QVBoxLayout()
        main_screen_layout.setContentsMargins(0, 0, 0, 0)
        main_screen_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(2)
        self.splitter.setChildrenCollapsible(False)

        self.contacts_widget = ContactsWidget()
        self.contacts_widget.contact_selected.connect(self._open_chat)
        self.contacts_widget.set_api_func(self._api_request)
        self.contacts_widget.set_callbacks(
            on_settings=self._open_settings,
            on_admin=self._open_admin_panel,
            on_logout=self._logout
        )
        self.contacts_widget.language_changed.connect(self._on_language_changed)
        self.splitter.addWidget(self.contacts_widget)

        self.chat_view = ChatView()
        self.splitter.addWidget(self.chat_view)

        self.admin_panel = AdminPanel()
        self.admin_panel.set_api_func(self._api_request)
        self.admin_panel.set_callbacks(on_exit=self._exit_admin)
        self.admin_panel.hide()

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.splitter)
        self.content_stack.addWidget(self.admin_panel)

        main_screen_layout.addWidget(self.content_stack)
        self.main_widget.setLayout(main_screen_layout)

        self.stack.addWidget(self.main_widget)
        main_layout.addWidget(self.stack)
        central.setLayout(main_layout)

        self.stack.setCurrentWidget(self.auth_widget)
        self.splitter.setSizes([280, 820])

    def _apply_loaded_config(self):
        if self._server_ip:
            self.auth_widget.server_ip.setText(self._server_ip)

    def _on_language_changed(self, lang: str):
        """Синхронизация языка между экраном входа и основным окном + сохранение в конфиг"""
        set_language(lang)
        self.auth_widget.retranslate_ui()
        self.contacts_widget.retranslate_ui()
        self.chat_view.retranslate_ui()
        self.admin_panel.retranslate_ui()
        self.setWindowTitle(tr("window_title"))
        save_app_config(self._server_ip, lang)

    def _api_request(self, payload: dict) -> Optional[dict]:
        try:
            ip, http_port, _ws_port = parse_server_address(self._server_ip)
            resp = requests.post(
                f"http://{ip}:{http_port}/api",
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"status": "error", "info": f"HTTP Error {resp.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "info": tr("conn_lost")}
        except requests.exceptions.Timeout:
            return {"status": "error", "info": tr("timeout_error")}
        except Exception as e:
            return {"status": "error", "info": str(e)}

    def _on_login_success(self, username: str, role: str, user_data: dict, friends: list):
        entered_ip = self.auth_widget.server_ip.text().strip()
        if entered_ip:
            self._server_ip = entered_ip
            save_app_config(self._server_ip, get_language())
        self._current_user = username
        self._user_role = role
        self._user_data = user_data
        self._friends = friends

        self.contacts_widget.update_user_info(username, role, user_data, friends)
        self.chat_view.set_my_username(username)

        self._connect_websocket()
        self.stack.setCurrentWidget(self.main_widget)

        if role == 'admin':
            self._open_admin_panel()

    def _connect_websocket(self):
        if self._ws_client:
            self._ws_client.stop()
            self._ws_client.wait(1000)

        self._ws_client = WebSocketClient(self._server_ip, self._current_user)
        self._ws_client.message_received.connect(self._on_ws_message)
        self._ws_client.start()

    def _on_ws_message(self, data: dict):
        msg_type = data.get("type", "")
        if msg_type == "new_message":
            self.chat_view.on_new_message(data)

    def _update_connection_status(self):
        if self._ws_client and not self._ws_client.isRunning():
            self._connect_websocket()

    def _open_chat(self, target: str):
        self.chat_view.set_target(target)
        self.content_stack.setCurrentWidget(self.splitter)

    def show_contacts(self):
        self.chat_view.clear()
        self.content_stack.setCurrentWidget(self.splitter)

    def _open_admin_panel(self):
        if self._user_role != 'admin':
            return
        resp = self._api_request({
            "action": "get_users",
            "from_user": self._current_user
        })
        if resp and resp.get("status") == "success":
            users_list = resp.get("users_list", {})
            self.admin_panel.update_users(users_list, self._current_user)
        self.content_stack.setCurrentWidget(self.admin_panel)

    def _exit_admin(self):
        self.content_stack.setCurrentWidget(self.splitter)

    def _open_settings(self):
        dialog = SettingsDialog(
            self._current_user,
            self._user_data,
            self._api_request,
            self
        )
        if dialog.exec() == 1:
            resp = self._api_request({
                "action": "login",
                "user": self._current_user,
                "pass": self._user_data.get("pass", "")
            })
            if resp and resp.get("status") == "success":
                self._on_login_success(
                    resp.get("user", self._current_user),
                    resp.get("role", "user"),
                    resp.get("user_data", {}),
                    resp.get("friends", [])
                )

    def _logout(self):
        if self._ws_client:
            self._ws_client.stop()
            self._ws_client = None
        self._current_user = ""
        self._user_role = "user"
        self._user_data = {}
        self._friends = []
        self.chat_view.clear()
        self.auth_widget.status_label.setText("")
        self.auth_widget.password_input.clear()
        self.stack.setCurrentWidget(self.auth_widget)

    def closeEvent(self, event):
        if self._ws_client:
            self._ws_client.stop()
        event.accept()


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("SPUTN1K")
    app.setOrganizationName("OrbitNet")

    # Безопасное определение доступных шрифтов
    try:
        if hasattr(QFontDatabase, 'families'):
            fonts = QFontDatabase.families()
        else:
            fonts = QFontDatabase().families()
    except Exception:
        fonts = []

    if "Segoe UI" in fonts:
        app.setFont(QFont("Segoe UI", 10))
    elif "Ubuntu" in fonts:
        app.setFont(QFont("Ubuntu", 10))
    else:
        app.setFont(QFont("sans-serif", 10))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
