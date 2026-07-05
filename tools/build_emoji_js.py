# -*- coding: utf-8 -*-
"""Regenerate STARSAIL_EMOJI_JS (Unicode picker, no send interception)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
site_config = ROOT / "starsailx" / "site_config.py"

EMOJIS = [
    "\U0001F600", "\U0001F603", "\U0001F604", "\U0001F601", "\U0001F606", "\U0001F605", "\U0001F923", "\U0001F602",
    "\U0001F642", "\U0001F643", "\U0001F609", "\U0001F60A", "\U0001F607", "\U0001F970", "\U0001F60D", "\U0001F929",
    "\U0001F618", "\U0001F617", "\U0001F619", "\U0001F61A", "\U0001F60B", "\U0001F61B", "\U0001F61D", "\U0001F61C",
    "\U0001F92A", "\U0001F928", "\U0001F9D0", "\U0001F913", "\U0001F60E", "\U0001F978", "\U0001F60F", "\U0001F612",
    "\U0001F61E", "\U0001F614", "\U0001F622", "\U0001F62D", "\U0001F624", "\U0001F620", "\U0001F621", "\U0001F92C",
    "\U0001F92F", "\U0001F631", "\U0001F628", "\U0001F630", "\U0001F625", "\U0001F613", "\U0001F917", "\U0001F914",
    "\U0001F44D", "\U0001F44E", "\U0001F44F", "\U0001F64C", "\U0001F44B", "\u270B", "\U0001F91A", "\U0001F91D",
    "\U0001F64F", "\u2764\uFE0F", "\U0001F9E1", "\U0001F49B", "\U0001F49A", "\U0001F499", "\U0001F49C", "\U0001F5A4",
    "\U0001F494", "\U0001F495", "\U0001F496", "\U0001F497", "\U0001F498", "\U0001F49D", "\U0001F48B", "\U0001F339",
    "\U0001F338", "\U0001F33B", "\U0001F340", "\U0001F331", "\U0001F34E", "\U0001F34A", "\U0001F353", "\U0001F355",
    "\U0001F354", "\U0001F35F", "\u2615", "\U0001F37A", "\U0001F382", "\U0001F381", "\U0001F389", "\U0001F38A",
    "\u26BD", "\U0001F3C0", "\U0001F3AF", "\U0001F3B5", "\U0001F3AE", "\U0001F4F1", "\U0001F4BB", "\U0001F4A1",
    "\u2728", "\U0001F525", "\U0001F4AF", "\U0001F44A", "\U0001F91E", "\U0001F60C", "\U0001F634", "\U0001F92B",
]

emoji_literals = ",\n            ".join(f"'{e}'" for e in EMOJIS)

block = f'''STARSAIL_EMOJI_JS = r"""
(function initStarsailUniEmoji() {{
    try {{
        const host = (location.hostname || '').toLowerCase();
        if (!host.includes('starsail.vip')) return;
        if (window.__starsailUniEmojiInstalled) return;
        window.__starsailUniEmojiInstalled = true;

        const EMOJIS = [
            {emoji_literals},
        ];

        const hideNativeEmojiPickers = () => {{
            document.querySelectorAll(
                '.uikit-emoji-picker,.uikit-emoji-picker__icon,.uikit-emoji-picker__list'
            ).forEach((el) => {{
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                el.style.setProperty('pointer-events', 'none', 'important');
            }});
        }};

        const findEditor = (box) => {{
            if (!box) return null;
            return box.querySelector('.ProseMirror')
                || box.querySelector('.tiptap')
                || box.querySelector('[contenteditable="true"]');
        }};

        const insertUnicodeEmoji = (editor, emoji) => {{
            if (!editor || !emoji) return;
            editor.focus();
            try {{
                if (document.execCommand('insertText', false, emoji)) {{
                    return;
                }}
            }} catch (e) {{}}
            try {{
                const sel = window.getSelection();
                if (sel && sel.rangeCount > 0) {{
                    const range = sel.getRangeAt(0);
                    range.deleteContents();
                    const node = document.createTextNode(emoji);
                    range.insertNode(node);
                    range.setStartAfter(node);
                    range.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(range);
                }}
                editor.dispatchEvent(new InputEvent('input', {{
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: emoji,
                }}));
            }} catch (e) {{}}
        }};

        const closeAllPanels = (except) => {{
            document.querySelectorAll('.starsail-uni-emoji__panel.is-open').forEach((panel) => {{
                if (panel !== except) panel.classList.remove('is-open');
            }});
        }};

        const mountEmojiPicker = () => {{
            const box = document.querySelector('.uikit-message-input');
            if (!box || box.querySelector('.starsail-uni-emoji')) return false;

            const nativePicker = box.querySelector('.uikit-emoji-picker');
            let anchor = (nativePicker && nativePicker.parentElement)
                || box.querySelector('.uikit-message-input__toolbar')
                || box.querySelector('.uikit-attachment-picker')
                || box.querySelector('.uikit-message-input__actions')
                || box.querySelector('.uikit-message-input__wrapper')
                || box;
            if (!anchor) return false;

            const wrap = document.createElement('div');
            wrap.className = 'starsail-uni-emoji';

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'starsail-uni-emoji__btn';
            btn.setAttribute('aria-label', '\\u8868\\u60c5');
            btn.setAttribute('title', '\\u8868\\u60c5');
            btn.textContent = '\\u{{1F60A}}';

            const panel = document.createElement('div');
            panel.className = 'starsail-uni-emoji__panel';
            panel.setAttribute('role', 'listbox');
            panel.setAttribute('aria-label', '\\u8868\\u60c5');

            EMOJIS.forEach((emoji) => {{
                const item = document.createElement('button');
                item.type = 'button';
                item.className = 'starsail-uni-emoji__item';
                item.setAttribute('role', 'option');
                item.textContent = emoji;
                item.addEventListener('click', (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    insertUnicodeEmoji(findEditor(box), emoji);
                    panel.classList.remove('is-open');
                }});
                panel.appendChild(item);
            }});

            btn.addEventListener('click', (e) => {{
                e.preventDefault();
                e.stopPropagation();
                const open = panel.classList.contains('is-open');
                closeAllPanels(panel);
                panel.classList.toggle('is-open', !open);
            }});

            wrap.appendChild(btn);
            wrap.appendChild(panel);

            if (nativePicker && nativePicker.parentElement === anchor) {{
                anchor.insertBefore(wrap, nativePicker);
            }} else {{
                anchor.appendChild(wrap);
            }}
            hideNativeEmojiPickers();
            return true;
        }};

        const isChatReady = () => {{
            const layout = document.querySelector('.chat-layout');
            const input = document.querySelector('.uikit-message-input');
            if (!layout || !input) return false;
            const r = layout.getBoundingClientRect();
            if (r.width < 8 || r.height < 8) return false;
            const st = getComputedStyle(layout);
            return st.display !== 'none' && st.visibility !== 'hidden';
        }};

        const tick = () => {{
            if (!isChatReady()) return;
            hideNativeEmojiPickers();
            mountEmojiPicker();
        }};

        document.addEventListener('click', (e) => {{
            const target = e.target;
            if (!(target instanceof Element)) return;
            if (target.closest('.starsail-uni-emoji')) return;
            closeAllPanels(null);
        }}, true);

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', tick);
        }} else {{
            tick();
        }}

        let mountTimer = null;
        const scheduleTick = () => {{
            if (mountTimer) return;
            mountTimer = setTimeout(() => {{
                mountTimer = null;
                tick();
            }}, 300);
        }};

        try {{
            new MutationObserver(scheduleTick).observe(document.documentElement, {{
                childList: true,
                subtree: true,
            }});
        }} catch (e) {{}}

        setInterval(tick, 2500);
    }} catch (e) {{}}
}})();
"""
'''

text = site_config.read_text(encoding="utf-8")
marker = "STARSAIL_EMOJI_JS = "
if marker not in text:
    raise SystemExit("STARSAIL_EMOJI_JS not found in site_config.py")
start = text.index(marker)
end = text.index('STARSAIL_INTERACTION_JS = ', start)
site_config.write_text(text[:start] + block + "\n" + text[end:], encoding="utf-8")
print("updated STARSAIL_EMOJI_JS", len(block))
