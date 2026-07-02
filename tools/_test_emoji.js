
(function initStarsailUniEmoji() {
    try {
        const host = (location.hostname || '').toLowerCase();
        if (!host.includes('starsail.vip')) return;
        if (window.__starsailUniEmojiInstalled) return;
        window.__starsailUniEmojiInstalled = true;

        const PANEL_ID = 'starsail-uni-emoji-panel';
        const EMOJIS = [
            '😀','😃','😄','😁','😆','😅','🤣','😂',
            '🙂','🙃','😉','😊','😇','🥰','😍','🤩',
            '😘','😗','😙','😚','😋','😛','😝','😜',
            '🤪','🤨','🧐','🤓','😎','🥸','😏','😒',
            '😞','😔','😟','😕','🙁','☹️','😣','😖',
            '😫','😩','🥺','😢','😭','😤','😠','😡',
            '🤬','🤯','😳','🥵','🥶','😱','😨','😰',
            '😥','😓','🤗','🤔','🤭','🤫','🤥','😶',
            '👍','👎','👏','🙌','👋','🤚','🖐️','🤝',
            '🙏','❤️','🧡','💛','💚','💙','💜','🖤',
            '💔','💕','💞','💓','💗','💖','💘','💝',
            '💋','🌹','🌸','🌺','🍀','🌿','🍎','🍊',
            '🍓','🍕','🍔','🍟','☕','🍺','🎂','🎁',
            '🎉','🎊','⚽','🏀','🎯','🎵','🎮','📱',
            '💻','💡','✨','🔥','💯','👊','🤞','😌',
            '😴','🤫',
        ];

        let panelAnchor = null;
        let activeInputBox = null;

        const hideNativeEmojiLists = () => {
            document.querySelectorAll('.uikit-emoji-picker__list').forEach((el) => {
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                el.style.setProperty('pointer-events', 'none', 'important');
            });
        };

        const findEditor = (box) => {
            if (!box) return null;
            return box.querySelector('.ProseMirror')
                || box.querySelector('.tiptap')
                || box.querySelector('[contenteditable="true"]');
        };

        const insertUnicodeEmoji = (editor, emoji) => {
            if (!editor || !emoji) return;
            editor.focus();
            try {
                if (document.execCommand('insertText', false, emoji)) {
                    editor.dispatchEvent(new InputEvent('input', {
                        bubbles: true,
                        cancelable: true,
                        inputType: 'insertText',
                        data: emoji,
                    }));
                    return;
                }
            } catch (e) {}
            try {
                const sel = window.getSelection();
                if (sel && sel.rangeCount > 0) {
                    const range = sel.getRangeAt(0);
                    range.deleteContents();
                    const node = document.createTextNode(emoji);
                    range.insertNode(node);
                    range.setStartAfter(node);
                    range.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
                editor.dispatchEvent(new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: emoji,
                }));
            } catch (e) {}
        };

        const getPanel = () => document.getElementById(PANEL_ID);

        const closePanel = () => {
            const panel = getPanel();
            if (!panel) return;
            panel.classList.remove('is-open');
            panel.style.display = 'none';
            panelAnchor = null;
        };

        const positionPanel = (panel, anchor) => {
            if (!panel || !anchor) return;
            const rect = anchor.getBoundingClientRect();
            const panelWidth = 320;
            const panelHeight = Math.min(260, panel.scrollHeight || 260);
            let left = rect.left;
            let top = rect.top - panelHeight - 8;
            if (top < 8) top = rect.bottom + 8;
            if (left + panelWidth > window.innerWidth - 8) {
                left = window.innerWidth - panelWidth - 8;
            }
            if (left < 8) left = 8;
            panel.style.left = left + 'px';
            panel.style.top = top + 'px';
        };

        const ensurePanel = () => {
            let panel = getPanel();
            if (panel) return panel;
            panel = document.createElement('div');
            panel.id = PANEL_ID;
            panel.className = 'starsail-uni-emoji__panel';
            panel.setAttribute('role', 'listbox');
            panel.setAttribute('aria-label', '表情');
            EMOJIS.forEach((emoji) => {
                const item = document.createElement('button');
                item.type = 'button';
                item.className = 'starsail-uni-emoji__item';
                item.setAttribute('role', 'option');
                item.textContent = emoji;
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const box = activeInputBox || document.querySelector('.uikit-message-input');
                    insertUnicodeEmoji(findEditor(box), emoji);
                    closePanel();
                });
                panel.appendChild(item);
            });
            document.body.appendChild(panel);
            return panel;
        };

        const togglePanel = (anchor, box) => {
            const panel = ensurePanel();
            activeInputBox = box;
            const isOpen = panel.classList.contains('is-open');
            if (isOpen && panelAnchor === anchor) {
                closePanel();
                return;
            }
            panelAnchor = anchor;
            panel.classList.add('is-open');
            panel.style.display = 'grid';
            positionPanel(panel, anchor);
        };

        const hijackNativePicker = () => {
            const box = document.querySelector('.uikit-message-input');
            if (!box) return false;
            if (!box.querySelector('.uikit-emoji-picker')) return false;
            hideNativeEmojiLists();
            return true;
        };

        if (!window.__starsailEmojiClickDelegate) {
            window.__starsailEmojiClickDelegate = true;
            document.addEventListener('click', (e) => {
                const target = e.target;
                if (!(target instanceof Element)) return;

                const icon = target.closest('.uikit-emoji-picker__icon');
                if (icon) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    const box = document.querySelector('.uikit-message-input');
                    hideNativeEmojiLists();
                    togglePanel(icon, box);
                    return;
                }

                if (!target.closest('#' + PANEL_ID)) {
                    closePanel();
                }
            }, true);
            document.addEventListener('pointerdown', (e) => {
                if (e.target instanceof Element && e.target.closest('.uikit-emoji-picker__icon')) {
                    e.stopPropagation();
                }
            }, true);
        }

        const tick = () => {
            hideNativeEmojiLists();
            hijackNativePicker();
            const panel = getPanel();
            if (panel && panel.classList.contains('is-open') && panelAnchor) {
                positionPanel(panel, panelAnchor);
            }
        };

        window.__starsailUniEmojiTick = tick;

        window.addEventListener('resize', () => {
            const panel = getPanel();
            if (panel && panel.classList.contains('is-open') && panelAnchor) {
                positionPanel(panel, panelAnchor);
            }
        });

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', tick);
        } else {
            tick();
        }

        let mountTimer = null;
        const scheduleTick = () => {
            if (mountTimer) return;
            mountTimer = setTimeout(() => {
                mountTimer = null;
                tick();
            }, 200);
        };

        try {
            new MutationObserver(scheduleTick).observe(document.documentElement, {
                childList: true,
                subtree: true,
            });
        } catch (e) {}

        setInterval(tick, 2000);
    } catch (e) {}
})();
