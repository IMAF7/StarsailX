# -*- coding: utf-8 -*-
"""聊天图片本地缓存：加载时落盘，复制时从本地读取。"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import threading
from typing import Dict, Optional

from PyQt6.QtGui import QGuiApplication, QImage, QPixmap


class ChatImageCache:
    """按账号缓存聊天图片，url -> 本地文件。"""

    _MIME_EXT = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
    }

    def __init__(self, cache_dir: str):
        self._dir = os.path.join(cache_dir, "chat_images")
        self._index_path = os.path.join(self._dir, "index.json")
        self._lock = threading.RLock()
        self._index: Dict[str, str] = {}
        self._pending: Dict[str, dict] = {}
        os.makedirs(self._dir, exist_ok=True)
        self._load_index()
        self._prune_invalid_entries()

    @staticmethod
    def _url_key(url: str) -> str:
        return hashlib.sha256((url or "").encode("utf-8", errors="ignore")).hexdigest()[:32]

    @classmethod
    def _ext_from_mime(cls, mime: str) -> str:
        m = (mime or "").split(";", 1)[0].strip().lower()
        return cls._MIME_EXT.get(m, ".part")

    @staticmethod
    def _detect_format(raw: bytes) -> Optional[str]:
        if len(raw) >= 8 and raw[:8] == b"\x89PNG\r\n\x1a\n":
            return "png"
        if len(raw) >= 3 and raw[:3] == b"\xff\xd8\xff":
            return "jpeg"
        if len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
            return "webp"
        if len(raw) >= 6 and raw[:6] in (b"GIF87a", b"GIF89a"):
            return "gif"
        if len(raw) >= 2 and raw[:2] == b"BM":
            return "bmp"
        return None

    @classmethod
    def _ext_from_format(cls, fmt: Optional[str]) -> str:
        return {
            "png": ".png",
            "jpeg": ".jpg",
            "webp": ".webp",
            "gif": ".gif",
            "bmp": ".bmp",
        }.get(fmt or "", ".bin")

    def _load_index(self) -> None:
        try:
            if os.path.isfile(self._index_path):
                with open(self._index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self._index = {str(k): str(v) for k, v in data.items()}
        except Exception:
            self._index = {}

    def _save_index(self) -> None:
        try:
            tmp = self._index_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._index, f, ensure_ascii=False)
            os.replace(tmp, self._index_path)
        except Exception:
            pass

    def _read_raw(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def _image_from_raw(self, raw: bytes) -> Optional[QImage]:
        if not raw:
            return None
        fmt = self._detect_format(raw)
        if fmt == "png" and len(raw) < 24:
            return None
        img = QImage()
        if img.loadFromData(raw):
            return img
        if fmt and img.loadFromData(raw, fmt.upper() if fmt != "jpeg" else "JPEG"):
            return img
        return None

    def _remove_file_quiet(self, path: str) -> None:
        try:
            if path and os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass

    def _remove_entry(self, image_url: str) -> None:
        key = self._url_key(image_url)
        with self._lock:
            fn = self._index.pop(key, None)
        if fn:
            self._remove_file_quiet(os.path.join(self._dir, fn))
            self._save_index()

    def _commit_file(self, image_url: str, path: str) -> bool:
        try:
            raw = self._read_raw(path)
        except Exception:
            self._remove_file_quiet(path)
            return False
        fmt = self._detect_format(raw)
        if not fmt or not self._image_from_raw(raw):
            self._remove_file_quiet(path)
            return False
        key = self._url_key(image_url)
        filename = f"{key}{self._ext_from_format(fmt)}"
        final_path = os.path.join(self._dir, filename)
        try:
            if os.path.normcase(path) != os.path.normcase(final_path):
                if os.path.isfile(final_path):
                    os.remove(final_path)
                os.replace(path, final_path)
            elif not os.path.isfile(final_path):
                with open(final_path, "wb") as f:
                    f.write(raw)
        except Exception:
            try:
                with open(final_path, "wb") as f:
                    f.write(raw)
                if os.path.normcase(path) != os.path.normcase(final_path):
                    self._remove_file_quiet(path)
            except Exception:
                self._remove_file_quiet(path)
                return False
        with self._lock:
            self._index[key] = filename
            self._save_index()
        return True

    def _prune_invalid_entries(self) -> None:
        stale_keys = []
        with self._lock:
            items = list(self._index.items())
        for key, fn in items:
            path = os.path.join(self._dir, fn)
            if not os.path.isfile(path):
                stale_keys.append(key)
                continue
            try:
                raw = self._read_raw(path)
            except Exception:
                stale_keys.append(key)
                self._remove_file_quiet(path)
                continue
            if not self._detect_format(raw) or not self._image_from_raw(raw):
                stale_keys.append(key)
                self._remove_file_quiet(path)
        if stale_keys:
            with self._lock:
                for key in stale_keys:
                    self._index.pop(key, None)
                self._save_index()

    def has(self, image_url: str) -> bool:
        return self.path_for(image_url) is not None

    def path_for(self, image_url: str) -> Optional[str]:
        if not image_url:
            return None
        key = self._url_key(image_url)
        with self._lock:
            fn = self._index.get(key)
        if not fn:
            return None
        path = os.path.join(self._dir, fn)
        if not os.path.isfile(path) or os.path.getsize(path) <= 0:
            return None
        try:
            raw = self._read_raw(path)
        except Exception:
            return None
        if not self._detect_format(raw) or not self._image_from_raw(raw):
            self._remove_entry(image_url)
            return None
        return path

    def begin(self, image_url: str, total_size: int, mime_type: str = "image/png") -> str:
        if not image_url:
            return ""
        key = self._url_key(image_url)
        path = os.path.join(self._dir, f"{key}.part")
        with self._lock:
            old = self._pending.get(key)
            if old:
                try:
                    old["fh"].close()
                except Exception:
                    pass
                self._remove_file_quiet(old.get("path", ""))
            fh = open(path, "wb")
            self._pending[key] = {
                "url": image_url,
                "path": path,
                "total": max(0, int(total_size or 0)),
                "received": 0,
                "fh": fh,
                "mime": mime_type or "image/png",
            }
        return key

    def append(self, session_id: str, b64_chunk: str) -> None:
        if not session_id or not b64_chunk:
            return
        with self._lock:
            pending = self._pending.get(session_id)
            if not pending:
                return
            try:
                raw = base64.b64decode(b64_chunk, validate=False)
            except Exception:
                return
            if not raw:
                return
            pending["fh"].write(raw)
            pending["received"] += len(raw)

    def finish(self, session_id: str) -> bool:
        with self._lock:
            pending = self._pending.pop(session_id, None)
        if not pending:
            return False
        path = pending.get("path", "")
        try:
            pending["fh"].flush()
            pending["fh"].close()
        except Exception:
            pass
        if not path or not os.path.isfile(path) or os.path.getsize(path) <= 0:
            self._remove_file_quiet(path)
            return False
        return self._commit_file(pending["url"], path)

    def cache_from_data_url(self, image_url: str, data_url: str) -> bool:
        if not image_url or not data_url:
            return False
        try:
            payload = data_url
            if payload.startswith("data:"):
                payload = payload.split(",", 1)[1]
            raw = base64.b64decode(payload, validate=False)
            if not raw:
                return False
            key = self._url_key(image_url)
            part_path = os.path.join(self._dir, f"{key}.part")
            with open(part_path, "wb") as f:
                f.write(raw)
            return self._commit_file(image_url, part_path)
        except Exception:
            return False

    def copy_to_clipboard(self, image_url: str) -> bool:
        path = self.path_for(image_url)
        if not path:
            return False
        try:
            raw = self._read_raw(path)
            img = self._image_from_raw(raw)
            if img is None or img.isNull():
                self._remove_entry(image_url)
                return False
            pix = QPixmap.fromImage(img)
            if pix.isNull():
                return False
            QGuiApplication.clipboard().setPixmap(pix)
            return True
        except Exception:
            return False
