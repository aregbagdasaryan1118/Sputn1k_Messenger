#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPUTN1K ALPHA 3 — ORBIT MESSENGER SERVER
HTTP API (port 7272) + WebSocket (port 7273)
Бэкенд для десктоп-клиента (Sputn1k_Desktop_Skript_Alpha3.py).
Поддерживает удаление сообщений "у себя" (action: delete_message) —
сообщение скрывается только у того, кто его удалил, у собеседника
оно остаётся видимым. Шифрование/расшифрование сообщений и файлов
происходит полностью на стороне клиента — сервер хранит и передаёт
только непрозрачный (зашифрованный) текст и не имеет доступа к ключам.
"""

import http.server
import socketserver
import json
import os
import time
import uuid
import threading
import asyncio
import argparse
import socket
import html as html_module
from datetime import datetime
import websockets

# Конфигурация (значения по умолчанию — переопределяются аргументами
# командной строки, см. parse_args() и main())
HTTP_PORT = 7272
WS_PORT = 7273
BIND_HOST = "0.0.0.0"  # "0.0.0.0" = слушать на всех сетевых интерфейсах машины
DB_FILE = "orbit_db.json"
LOCK = threading.Lock()

# WebSocket clients: { websocket: username }
WS_CLIENTS = {}
WS_CLIENTS_LOCK = threading.Lock()

# Работа с базой
def load_db():
    """Загрузка БД с потокобезопасностью"""
    if not os.path.exists(DB_FILE):
        default_db = _create_default_db()
        save_db(default_db)
        return default_db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "friend_requests" not in data:
                data["friend_requests"] = []
            if "pending_messages" not in data:
                data["pending_messages"] = {}
            return data
    except Exception as e:
        print(f"[!] Ошибка загрузки БД: {e}")
        return _create_default_db()


def save_db(data):
    """Сохранение БД с потокобезопасностью"""
    with LOCK:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _create_default_db():
    return {
        "users": {
            "sys_adm1n": {
                "pass": "imsysadm", "rank": 4, "id": "0000",
                "hidden": False, "about": "SYSTEM CORE",
                "reg_date": "08.07.2026", "msg_count": 0, "avatar": ""
            },
            "SYSTEM_MANAGER": {
                "pass": "sukablyad", "rank": 4, "id": "0001",
                "hidden": False, "about": "Служба поддержки Ørb1t.",
                "reg_date": "08.07.2026", "msg_count": 0, "avatar": ""
            }
        },
        "friends": {"sys_adm1n": [], "SYSTEM_MANAGER": []},
        "chats": {},
        "friend_requests": [],
        "pending_messages": {}
    }


def find_user_by_username(db, username):
    """Поиск пользователя без учёта регистра"""
    for existing_user in db['users']:
        if existing_user.lower() == username.lower():
            return existing_user
    return None


def find_user_by_id(db, user_id):
    """Поиск пользователя по ID"""
    for username, data in db['users'].items():
        if str(data.get('id')) == str(user_id):
            return username
    return None


def sanitize_text(text):
    """Санитизация текста — без HTML"""
    if text is None:
        return ""
    return html_module.escape(str(text), quote=True)[:2000]


def get_chat_key(u1, u2):
    """Ключ чата: отсортированные имена в нижнем регистре"""
    names = sorted([u1.lower().strip(), u2.lower().strip()])
    return f"{names[0]}:{names[1]}"


# WebSocket сервер
async def ws_handler(websocket):
    """Обработчик WebSocket-соединения"""
    username = None
    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                msg_type = data.get("type", "")
                if msg_type == "auth":
                    username = data.get("user", "")
                    with WS_CLIENTS_LOCK:
                        WS_CLIENTS[websocket] = username
                    print(f"[WS] Пользователь {username} подключился")
                    await websocket.send(json.dumps({
                        "type": "auth_ok",
                        "user": username
                    }))
                    db = load_db()
                    pending = db.get("pending_messages", {}).get(username.lower(), [])
                    for msg in pending:
                        await websocket.send(json.dumps({
                            "type": "new_message",
                            **msg
                        }))
                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if username:
            print(f"[WS] Пользователь {username} отключился")
        with WS_CLIENTS_LOCK:
            WS_CLIENTS.pop(websocket, None)


async def broadcast_message(chat_key, message_data, exclude_ws=None):
    """Рассылка сообщения подключенным WebSocket-клиентам"""
    parts = chat_key.split(":")
    if len(parts) != 2:
        return
    user1, user2 = parts
    targets = {user1, user2}
    with WS_CLIENTS_LOCK:
        for ws, ws_user in list(WS_CLIENTS.items()):
            if ws == exclude_ws:
                continue
            if ws_user and ws_user.lower() in targets:
                try:
                    await ws.send(json.dumps({
                        "type": "new_message",
                        "chat_key": chat_key,
                        **message_data
                    }))
                except Exception:
                    pass


def get_local_ips():
    """Определяет IP-адреса, на которых сервер реально доступен в локальной сети."""
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass
    return sorted(ips)


def run_ws_server():
    """Запуск WebSocket сервера в отдельном потоке asyncio"""
    async def start():
        print(f"[*] WebSocket сервер запущен на {BIND_HOST}:{WS_PORT}")
        async with websockets.serve(ws_handler, BIND_HOST, WS_PORT):
            await asyncio.Future()
    asyncio.run(start())


def notify_clients(chat_key, message_data):
    """Отправка уведомлений WebSocket-клиентам из HTTP-потока"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(
                broadcast_message(chat_key, message_data),
                loop
            )
    except RuntimeError:
        pass


class OrbitHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP API handler"""
    def do_OPTIONS(self):
        # Строка статуса должна отправляться ПЕРВОЙ — иначе получается
        # битый HTTP-ответ на CORS-preflight.
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Веб-клиент больше не поддерживается (фокус на десктоп-версии) —
        # GET используется только для базовой проверки, что сервер жив.
        if self.path in ('/', ''):
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("SPUTN1K Orbit Messenger Server — running (desktop-only, Alpha 3)".encode('utf-8'))
            return
        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == '/api':
            self._handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _handle_api(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            req = json.loads(post_data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_response({"status": "error", "info": "Некорректный запрос JSON"})
            return

        db = load_db()
        action = req.get('action', '')
        handler = self._get_handler(action)
        if handler:
            result = handler(req, db)
        else:
            result = {"status": "error", "info": "Неизвестное действие"}
        self._json_response(result)

    def _get_handler(self, action):
        handlers = {
            'login': self._handle_login,
            'register': self._handle_register,
            'add_friend_by_id': self._handle_add_friend,
            'save_settings': self._handle_save_settings,
            'get_chat': self._handle_get_chat,
            'send_msg': self._handle_send_msg,
            'delete_message': self._handle_delete_message,
            'delete_user': self._handle_delete_user,
            'get_users': self._handle_get_users,
        }
        return handlers.get(action)

    def _json_response(self, data):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _handle_login(self, req, db):
        u_input = sanitize_text(req.get('user', '').strip())
        p = req.get('pass', '').strip()
        if not u_input or not p:
            return {"status": "error", "info": "Заполните все поля"}

        matched_user = find_user_by_username(db, u_input)
        if not matched_user:
            return {"status": "error", "info": "Пользователь не найден"}

        user_data = db['users'][matched_user]
        if user_data['pass'] != p:
            return {"status": "error", "info": "Неверный пароль"}

        user_rank = user_data.get('rank', 1)
        role = 'admin' if (user_rank >= 3 or matched_user in ['sys_adm1n', 'SYSTEM_MANAGER']) else 'user'
        friends_list = db['friends'].get(matched_user, [])
        return {
            "status": "success",
            "role": role,
            "user": matched_user,
            "user_data": user_data,
            "friends": friends_list,
            "users_list": db['users'] if role == 'admin' else {}
        }

    def _handle_register(self, req, db):
        u = sanitize_text(req.get('user', '').strip())
        p = req.get('pass', '').strip()
        if not u or not p:
            return {"status": "error", "info": "Заполните все поля"}
        if len(u) < 2 or len(u) > 24:
            return {"status": "error", "info": "Длина от 2 до 24 символов"}
        if len(p) < 4:
            return {"status": "error", "info": "Пароль минимум 4 символа"}
        if u in db['users']:
            return {"status": "error", "info": "Логин уже занят"}
        if find_user_by_username(db, u):
            return {"status": "error", "info": "Логин уже занят (регистр)"}

        new_id = str(int(time.time() * 10000) % 10000).zfill(4)
        today = time.strftime("%d.%m.%Y")
        db['users'][u] = {
            "pass": p,
            "rank": 1,
            "id": new_id,
            "hidden": False,
            "about": "",
            "reg_date": today,
            "msg_count": 0,
            "avatar": ""
        }
        db['friends'][u] = []
        save_db(db)
        return {"status": "success", "info": f"Успешная регистрация! Ваш ID: {new_id}"}

    def _handle_add_friend(self, req, db):
        from_u = req.get('from_user')
        target_id = str(req.get('target_id', '')).strip()
        found_target = find_user_by_id(db, target_id)
        if not found_target:
            return {"status": "error", "info": "Пользователь с таким ID не найден"}
        if found_target == from_u:
            return {"status": "error", "info": "Нельзя добавить самого себя"}
        if found_target in db['friends'].get(from_u, []):
            return {"status": "error", "info": "Уже в контактах"}

        db['friends'].setdefault(from_u, []).append(found_target)
        db['friends'].setdefault(found_target, []).append(from_u)
        save_db(db)
        return {
            "status": "success",
            "info": f"{found_target} добавлен в контакты!",
            "friends": db['friends'][from_u]
        }

    def _handle_save_settings(self, req, db):
        u = req.get('from_user')
        if u not in db['users']:
            return {"status": "error", "info": "Пользователь не найден"}

        new_nick = sanitize_text(req.get('new_nick', '').strip())
        new_pass = req.get('new_pass', '').strip()
        new_avatar = req.get('new_avatar', '').strip()

        if new_pass:
            if len(new_pass) < 4:
                return {"status": "error", "info": "Пароль минимум 4 символа"}
            db['users'][u]['pass'] = new_pass

        if new_avatar is not None:
            db['users'][u]['avatar'] = new_avatar

        if new_nick and new_nick != u:
            if new_nick in db['users']:
                return {"status": "error", "info": "Никнейм уже занят"}
            db['users'][new_nick] = db['users'].pop(u)
            if u in db['friends']:
                db['friends'][new_nick] = db['friends'].pop(u)
            for friend, f_list in db['friends'].items():
                db['friends'][friend] = [new_nick if x == u else x for x in f_list]
            for key in list(db['chats'].keys()):
                p1, p2 = key.split(':')
                if p1 == u.lower() or p2 == u.lower():
                    new_p1 = new_nick.lower() if p1 == u.lower() else p1
                    new_p2 = new_nick.lower() if p2 == u.lower() else p2
                    new_key = f"{new_p1}:{new_p2}"
                    db['chats'][new_key] = db['chats'].pop(key)

        save_db(db)
        return {"status": "success", "info": "Настройки сохранены"}

    def _handle_get_chat(self, req, db):
        u1 = req.get('from_user', '')
        u2 = req.get('target', '')
        key = get_chat_key(u1, u2)
        history = db['chats'].get(key, [])
        requester = u1.lower().strip()
        # Скрываем сообщения, удалённые этим пользователем "у себя"
        visible_history = [
            {k: v for k, v in msg.items() if k != 'deleted_for'}
            for msg in history
            if requester not in msg.get('deleted_for', [])
        ]
        return {"status": "success", "history": visible_history}

    def _handle_send_msg(self, req, db):
        u1 = req.get('from_user', '')
        u2 = req.get('target', '')
        text = sanitize_text(req.get('text', ''))
        image = req.get('image', None)

        if not text and not image:
            return {"status": "error", "info": "Пустое сообщение"}

        key = get_chat_key(u1, u2)
        msg_obj = {
            "id": uuid.uuid4().hex,
            "from": u1,
            "text": text,
            "image": image,
            "time": time.strftime("%H:%M"),
            "deleted_for": []
        }
        db['chats'].setdefault(key, []).append(msg_obj)

        if u1 in db['users']:
            db['users'][u1]['msg_count'] = db['users'][u1].get('msg_count', 0) + 1

        save_db(db)
        broadcast_obj = {k: v for k, v in msg_obj.items() if k != 'deleted_for'}
        notify_clients(key, broadcast_obj)
        return {"status": "success", "id": msg_obj["id"]}

    def _handle_delete_message(self, req, db):
        """Удаление сообщения только у запрашивающего пользователя (не влияет на собеседника)"""
        from_u = req.get('from_user', '')
        target = req.get('target', '')
        msg_id = req.get('msg_id', '')
        if not from_u or not target or not msg_id:
            return {"status": "error", "info": "Некорректный запрос"}

        key = get_chat_key(from_u, target)
        chat = db['chats'].get(key, [])
        requester = from_u.lower().strip()
        found = False
        for msg in chat:
            if msg.get('id') == msg_id:
                found = True
                deleted_for = msg.setdefault('deleted_for', [])
                if requester not in deleted_for:
                    deleted_for.append(requester)
                break

        if not found:
            return {"status": "error", "info": "Сообщение не найдено"}

        save_db(db)
        return {"status": "success", "info": "Сообщение удалено у вас"}

    def _handle_delete_user(self, req, db):
        from_u = req.get('from_user')
        target_u = req.get('target_user')

        if from_u != 'sys_adm1n':
            return {"status": "error", "info": "Отказано в доступе"}
        if target_u not in db['users']:
            return {"status": "error", "info": "Пользователь не найден"}

        del db['users'][target_u]
        if target_u in db['friends']:
            del db['friends'][target_u]
        for friend, f_list in db['friends'].items():
            db['friends'][friend] = [x for x in f_list if x != target_u]

        save_db(db)
        return {"status": "success", "info": f"Пользователь {target_u} удалён", "users_list": db['users']}

    def _handle_get_users(self, req, db):
        from_u = req.get('from_user')
        u_data = db['users'].get(from_u, {})
        rank = u_data.get('rank', 1)
        if rank >= 3 or from_u in ('sys_adm1n', 'SYSTEM_MANAGER'):
            return {"status": "success", "users_list": db['users']}
        return {"status": "error", "info": "Отказано в доступе"}


def parse_args():
    parser = argparse.ArgumentParser(description="SPUTN1K / Orbit Messenger Server")
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="IP-адрес для привязки сервера. По умолчанию 0.0.0.0 — сервер слушает "
             "на ВСЕХ сетевых интерфейсах машины (обычно это и есть то, что нужно). "
             "Указывайте конкретный IP только если хотите ограничить приём подключений "
             "одним конкретным локальным адресом машины."
    )
    parser.add_argument("--http-port", type=int, default=7272, help="Порт HTTP API (по умолчанию 7272)")
    parser.add_argument("--ws-port", type=int, default=7273, help="Порт WebSocket (по умолчанию 7273)")
    return parser.parse_args()


def main():
    global HTTP_PORT, WS_PORT, BIND_HOST
    args = parse_args()
    BIND_HOST = args.host
    HTTP_PORT = args.http_port
    WS_PORT = args.ws_port

    ws_thread = threading.Thread(target=run_ws_server, daemon=True)
    ws_thread.start()

    print("=" * 60)
    print("[*] SPUTN1K / Orbit Messenger Server")
    if BIND_HOST == "0.0.0.0":
        local_ips = get_local_ips()
        print(f"[*] Слушает на всех интерфейсах (0.0.0.0), порты {HTTP_PORT}/{WS_PORT}")
        if local_ips:
            print("[*] В десктоп-клиенте, для подключения из локальной сети, укажите один из этих IP:")
            for ip in local_ips:
                print(f"      -> {ip}")
        print("[*] 127.0.0.1 — только для подключения с этой же машины.")
        print("[*] Для доступа из интернета через статический IP роутера:")
        print("      1) настройте на роутере проброс портов (port forwarding)")
        print(f"         {HTTP_PORT}/tcp и {WS_PORT}/tcp -> IP этой машины в локальной сети;")
        print("      2) внешние клиенты подключаются по публичному/статическому IP роутера,")
        print("         локальные клиенты — по локальному IP машины (см. список выше).")
    else:
        print(f"[*] Слушает строго на {BIND_HOST}:{HTTP_PORT} / {BIND_HOST}:{WS_PORT}")
    print("=" * 60)

    with socketserver.TCPServer((BIND_HOST, HTTP_PORT), OrbitHandler) as httpd:
        print(f"[*] HTTP API сервер запущен на {BIND_HOST}:{HTTP_PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Сервер остановлен.")


if __name__ == "__main__":
    main()

