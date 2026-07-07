# -*- coding: utf-8 -*-
"""Starsail 站点配置。"""

STARSAIL_APP_URL = "https://starsail.vip/"

LOGIN_WINDOW_WIDTH = 420
LOGIN_WINDOW_HEIGHT = 480
CHAT_WINDOW_WIDTH = 1200
CHAT_WINDOW_HEIGHT = 700

ENABLE_CALL_FEATURES = False

STARSAIL_LOGIN_FAIL_REASONS = frozenset({
    "login_form", "loading", "no_shell", "not_starsail", "error",
})

STARSAIL_SHELL_VERIFY_JS = r"""
(function() {
    try {
        const href = (location.href || '').toLowerCase();
        if (!href.includes('starsail.vip')) {
            return JSON.stringify({ok: false, reason: 'not_starsail'});
        }
        const visible = (el) => {
            if (!el) return false;
            const r = el.getBoundingClientRect();
            const st = getComputedStyle(el);
            return r.width > 8 && r.height > 8 && st.visibility !== 'hidden' && st.display !== 'none';
        };
        const loginPanel = document.querySelector('.login-panel');
        if (visible(loginPanel)) {
            return JSON.stringify({ok: false, reason: 'login_form'});
        }
        const chatLayout = document.querySelector('.chat-layout');
        if (visible(chatLayout)) {
            return JSON.stringify({ok: true, reason: 'chat_layout'});
        }
        const loading = document.querySelector('.loading-container');
        if (visible(loading)) {
            return JSON.stringify({ok: false, reason: 'loading'});
        }
        return JSON.stringify({ok: false, reason: 'no_shell'});
    } catch (e) {
        return JSON.stringify({ok: false, reason: 'error'});
    }
})();
"""

STARSAIL_SHELL_CSS = r"""
/* 登录页：隐藏手机/邮箱登录与去注册 */
.login-tabs, .login-switch-btn { display: none !important; }

/* 自动登入：隐藏原登录页（含整页背景与卡片），由客户端遮罩接管 */
html[data-starsail-busy="1"] .login-page,
html[data-starsail-busy="1"] .login-panel {
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    position: fixed !important;
    left: -10000px !important;
    top: 0 !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
}
html[data-starsail-client="1"] body {
    background: #f3f3f3 !important;
}
html[data-starsail-client="1"] #starsail-login-busy-overlay {
    display: flex !important;
}
html[data-starsail-chat-ready="1"] #starsail-login-busy-overlay {
    display: none !important;
}
#starsail-login-busy-overlay {
    position: fixed;
    inset: 0;
    z-index: 2147483647;
    display: none;
    align-items: center;
    justify-content: center;
    background: #f3f3f3;
    flex-direction: column;
}
html[data-uikit-theme="dark"] #starsail-login-busy-overlay,
html[data-uikit-theme="dark"][data-starsail-client="1"] body {
    background: #1e1e1e;
}
.starsail-login-busy-card {
    text-align: center;
    padding: 28px 36px;
}
.starsail-login-busy-spinner {
    width: 36px;
    height: 36px;
    margin: 0 auto 16px;
    border: 3px solid rgba(37, 99, 235, 0.18);
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: starsail-busy-spin 0.75s linear infinite;
}
@keyframes starsail-busy-spin {
    to { transform: rotate(360deg); }
}
.starsail-login-busy-text {
    font-size: 16px;
    font-weight: 600;
    color: #1a1f2e;
    letter-spacing: 0.02em;
}
.starsail-bouncy-dots {
    display: inline-flex;
    align-items: flex-end;
    gap: 4px;
    margin-left: 2px;
    height: 1em;
    vertical-align: baseline;
}
.starsail-bouncy-dots i {
    display: inline-block;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: currentColor;
    animation: starsail-dot-bounce 0.72s cubic-bezier(.45,.05,.55,.95) infinite;
}
.starsail-bouncy-dots i:nth-child(1) { animation-delay: 0s; }
.starsail-bouncy-dots i:nth-child(2) { animation-delay: 0.12s; }
.starsail-bouncy-dots i:nth-child(3) { animation-delay: 0.24s; }
@keyframes starsail-dot-bounce {
    0%, 70%, 100% { transform: translateY(0); }
    35% { transform: translateY(-7px); }
}
html[data-uikit-theme="dark"] .starsail-login-busy-text {
    color: #f3f4f6;
}

/* 聊天页：铺满窗口 */
.chat-layout {
    width: 100vw !important;
    height: 100vh !important;
    max-width: none !important;
    max-height: none !important;
    aspect-ratio: auto !important;
    margin: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
}

/* 浅色：仅修正对方气泡与背景撞色，界面交给 Starsail 原生 UIKit */
html[data-uikit-theme="light"],
html:not([data-uikit-theme="dark"]) {
    --uikit-bg-color-bubble-reciprocal: #ffffff;
    --uikit-bg-color-bubble-own: #95caff;
}

.uikit-text-message {
    font-size: 14px !important;
    line-height: 1.55 !important;
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Segoe UI", sans-serif !important;
}
.uikit-message-input .tiptap,
.uikit-input-wrapper__tiptap-editor,
.uikit-message-input .ProseMirror {
    font-size: 14px !important;
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Segoe UI", sans-serif !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    overflow-wrap: anywhere !important;
    word-break: break-all !important;
    white-space: pre-wrap !important;
}
.uikit-message-input {
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: visible !important;
}
.uikit-message-input__wrapper,
.uikit-input-wrapper {
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: visible !important;
}
/* 引用条在输入框上方（position:absolute; bottom:100%），父级不能 overflow:hidden */
.uikit-quoted__message__preview {
    z-index: 40 !important;
    overflow: visible !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    left: 10px !important;
    right: 10px !important;
    bottom: calc(100% - 2px) !important;
    padding: 0 !important;
    gap: 10px !important;
    align-items: center !important;
    background: transparent !important;
    box-shadow: none !important;
    animation: starsail-quote-in 0.18s ease-out !important;
}
@keyframes starsail-quote-in {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.uikit-quoted__message__preview__content {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 9px 12px 9px 11px !important;
    border-radius: 14px 14px 6px 6px !important;
    border: 1px solid #e2e8f0 !important;
    border-bottom: none !important;
    border-left: 3px solid #147aff !important;
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
    box-shadow: 0 -1px 6px rgba(15, 23, 42, 0.05) !important;
}
html[data-uikit-theme=dark] .uikit-quoted__message__preview__content {
    border-color: #3a3c42 !important;
    border-left-color: #4086ff !important;
    background: linear-gradient(180deg, #2a2b30 0%, #25262a 100%) !important;
    box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.22) !important;
}
.uikit-quoted__message__preview__content--header {
    margin-bottom: 2px !important;
}
.uikit-quoted__message__preview__content--title {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #147aff !important;
    line-height: 1.35 !important;
}
html[data-uikit-theme=dark] .uikit-quoted__message__preview__content--title {
    color: #6ba3ff !important;
}
.uikit-quoted__message__preview__content--text {
    font-size: 13px !important;
    line-height: 1.45 !important;
    color: #64748b !important;
    -webkit-line-clamp: 2 !important;
    display: -webkit-box !important;
    -webkit-box-orient: vertical !important;
    overflow: hidden !important;
}
html[data-uikit-theme=dark] .uikit-quoted__message__preview__content--text {
    color: #9aa3b2 !important;
}
.uikit-quoted__message__preview__close {
    pointer-events: auto !important;
    z-index: 41 !important;
    flex: 0 0 28px !important;
    width: 28px !important;
    height: 28px !important;
    margin: 0 !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: rgba(100, 116, 139, 0.12) !important;
    color: #94a3b8 !important;
    font-size: 15px !important;
    line-height: 1 !important;
    transition: background 0.15s, color 0.15s !important;
}
.uikit-quoted__message__preview__close:hover {
    background: rgba(100, 116, 139, 0.2) !important;
    color: #475569 !important;
}
html[data-uikit-theme=dark] .uikit-quoted__message__preview__close {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #9aa3b2 !important;
}
html[data-uikit-theme=dark] .uikit-quoted__message__preview__close:hover {
    background: rgba(255, 255, 255, 0.14) !important;
    color: #e8eaed !important;
}
/* 有引用时，输入框上圆角收窄，视觉上连成一体 */
.uikit-message-input:has(.uikit-quoted__message__preview) {
    padding-top: 6px !important;
}
.uikit-message-input:has(.uikit-quoted__message__preview) .uikit-input-wrapper {
    border-top-left-radius: 6px !important;
    border-top-right-radius: 6px !important;
}

/* 劫持原 TUI 表情按钮，仅隐藏其弹出列表，Unicode 面板挂在原按钮上 */
.uikit-emoji-picker {
    position: relative !important;
    display: inline-flex !important;
    visibility: visible !important;
    pointer-events: auto !important;
}
.uikit-emoji-picker__list {
    display: none !important;
    pointer-events: none !important;
    visibility: hidden !important;
}
.starsail-uni-emoji__panel {
    position: fixed;
    z-index: 2147483646;
    width: 320px;
    max-height: 260px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 8px;
    display: none;
    grid-template-columns: repeat(8, 1fr);
    gap: 2px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    pointer-events: auto;
}
html[data-uikit-theme="dark"] .starsail-uni-emoji__panel {
    background: #2b2b2b;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}
.starsail-uni-emoji__panel.is-open {
    display: grid;
}
.starsail-uni-emoji__item {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 22px;
    line-height: 32px;
    padding: 0;
    border-radius: 6px;
}
.starsail-uni-emoji__item:hover {
    background: rgba(0, 0, 0, 0.06);
}
html[data-uikit-theme="dark"] .starsail-uni-emoji__item:hover {
    background: rgba(255, 255, 255, 0.08);
}

.uikit-message-list__container {
    padding-left: 16px !important;
    padding-right: 16px !important;
    padding-bottom: 14px !important;
}

/* 气泡宽度：短句收窄，长句最多 70% */
.uikit-message-layout__content,
.uikit-message-layout__content--left,
.uikit-message-layout__content--right {
    flex: 1 1 auto !important;
    width: auto !important;
    max-width: 100% !important;
    min-width: 0 !important;
}
.uikit-message-layout__body,
.uikit-message-layout__body--left,
.uikit-message-layout__body--right {
    width: fit-content !important;
    max-width: 70% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}
.uikit-message-layout__bubble {
    flex: 0 0 auto !important;
    width: max-content !important;
    max-width: 100% !important;
    min-width: 0 !important;
}
.uikit-message-bubble,
.uikit-text-message {
    display: block !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}
.uikit-text-message__content {
    white-space: pre-wrap !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
}

/* 隐藏未接通的语音 / 视频 / 红包 */
.uikit-audio-call-picker,
.uikit-audio-call-picker__button,
.uikit-video-call-picker,
.uikit-video-call-picker__button,
.red-packet-action,
button.red-packet-action,
button[aria-label="红包"],
button[title="红包"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* 深色：同步变量（对方气泡略提亮以免融入背景） */
html[data-uikit-theme=dark],
html[data-uikit-theme=dark] body,
html[data-uikit-theme=dark] #root {
    background-color: #131417 !important;
    color: #ffffffed !important;
}
html[data-uikit-theme=dark] {
    --uikit-bg-color-default: #131417;
    --uikit-bg-color-topbar: #131417;
    --uikit-bg-color-operate: #1f2024;
    --uikit-bg-color-function: #3a3c42;
    --uikit-bg-color-input: #2b2c30;
    --uikit-bg-color-dialog: #1f2024;
    --uikit-bg-color-dialog-module: #2b2c30;
    --uikit-bg-color-entrycard: #2b2c30;
    --uikit-bg-color-bottombar: #2b2c30;
    --uikit-bg-color-bubble-reciprocal: #3a3c42;
    --uikit-bg-color-bubble-own: #5c9dff;
    --uikit-text-color-primary: #ffffffed;
    --uikit-text-color-secondary: #ffffff8c;
    --uikit-text-color-tertiary: #ffffff4d;
    --uikit-text-color-button: #fff;
    --uikit-text-color-link: #4086ff;
    --uikit-stroke-color-primary: #3a3c42;
    --uikit-stroke-color-secondary: #2b2c30;
    --uikit-list-color-default: #1f2024;
    --uikit-list-color-hover: #2b2c30;
    --uikit-button-color-primary-default: #4086ff;
    --uikit-button-color-secondary-default: #3a3c42;
    --uikit-button-color-secondary-hover: #2b2c30;
}
html[data-uikit-theme=dark] .chat-layout,
html[data-uikit-theme=dark] .chat-layout.dark {
    background-color: #131417 !important;
    box-shadow: none !important;
}
html[data-uikit-theme=dark] .side-tab,
html[data-uikit-theme=dark] .side-tab.dark {
    background-color: #3a3c42 !important;
}
html[data-uikit-theme=dark] .side-tab .tab-item:hover {
    background-color: #ffffff14 !important;
}
html[data-uikit-theme=dark] .conversation-list-panel {
    background-color: #1f2024 !important;
}
html[data-uikit-theme=dark] .chat-content-panel,
html[data-uikit-theme=dark] .chat-main {
    background-color: #131417 !important;
}
html[data-uikit-theme=dark] .empty-placeholder {
    background-color: #131417 !important;
    border-left-color: #3a3c42 !important;
    color: #ffffff8c !important;
}
html[data-uikit-theme=dark] .empty-title {
    color: #ffffffed !important;
}
html[data-uikit-theme=dark] .empty-subtitle {
    color: #ffffff8c !important;
}
.empty-placeholder {
    gap: 0 !important;
    padding: 12px 20px 20px !important;
}
.empty-placeholder .empty-icon {
    font-size: 40px !important;
    line-height: 1 !important;
    margin-bottom: 18px !important;
    opacity: 0.42 !important;
    filter: grayscale(0.15);
}
.empty-placeholder .empty-title,
.empty-placeholder .empty-subtitle {
    font-size: 0 !important;
    line-height: 0 !important;
    color: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
}
.empty-placeholder .empty-title::after {
    content: "如今我努力奔跑";
    display: block;
    font-size: 15px !important;
    line-height: 1.5 !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    color: #3f4a5a !important;
    text-align: center !important;
    margin-bottom: 8px !important;
}
.empty-placeholder .empty-subtitle::after {
    content: "不过是为了追上那个曾经被寄予厚望的自己";
    display: block;
    font-size: 13px !important;
    line-height: 1.75 !important;
    font-weight: 400 !important;
    letter-spacing: 0.02em !important;
    color: #7a8494 !important;
    text-align: center !important;
    max-width: 300px !important;
    margin: 0 auto !important;
    padding: 0 8px !important;
    white-space: normal !important;
}
html[data-uikit-theme=dark] .empty-placeholder .empty-title::after {
    color: #e8eaed !important;
}
html[data-uikit-theme=dark] .empty-placeholder .empty-subtitle::after {
    color: #9aa3b2 !important;
}
html[data-uikit-theme=dark] .uikit-message-list {
    background-color: #1f2024 !important;
}
html[data-uikit-theme=dark] .login-page {
    background-color: #131417 !important;
}
html[data-uikit-theme=dark] .login-panel {
    background-color: #1f2024 !important;
    color: #ffffffed !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45) !important;
}
html[data-uikit-theme=dark] .login-field input {
    background-color: #2b2c30 !important;
    color: #ffffffed !important;
    border-color: #3a3c42 !important;
}
html[data-uikit-theme=dark] .login-button {
    background-color: #4086ff !important;
    color: #fff !important;
}

/* 发送按钮 */
.starsail-send-btn {
    flex: 0 0 auto;
    align-self: center;
    height: 36px;
    padding: 0 18px;
    margin-left: 4px;
    border: none;
    border-radius: 8px;
    background: #147aff;
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}
.starsail-send-btn:hover { background: #0f6ae6; }
.starsail-send-btn:active { background: #0c5ccb; }

/* 默认禁止选中界面文字；消息区、输入框等仍可复制 */
html, body, #root, .chat-layout {
    -webkit-user-select: none !important;
    user-select: none !important;
}
.uikit-message-list,
.uikit-message-list *,
.uikit-message-input,
.uikit-message-input *,
.login-field input,
.login-field textarea,
.uikit-SearchResults__message-detail-content,
.uikit-SearchResults__message-detail-content * {
    -webkit-user-select: text !important;
    user-select: text !important;
}
"""

STARSAIL_SHELL_CSS_JS = (
    "(function(){"
    "var CSS=" + repr(STARSAIL_SHELL_CSS) + ";"
    "function injectStyle(){"
    "if(!document.documentElement)return;"
    "var s=document.getElementById('starsail-shell-style');"
    "if(!s){"
    "s=document.createElement('style');"
    "s.id='starsail-shell-style';"
    "document.documentElement.appendChild(s);"
    "}"
    "if(s.getAttribute('data-starsail-css-ver')!=='empty-quote-v5'){"
    "s.setAttribute('data-starsail-css-ver','empty-quote-v5');"
    "}"
    "s.textContent=CSS;"
    "}"
    "window.__starsailApplyTheme=function(light){"
    "var theme=light?'light':'dark';"
    "var dark=theme==='dark';"
    "try{document.documentElement.setAttribute('data-uikit-theme',theme);}catch(e){}"
    "try{if(document.body)document.body.setAttribute('data-uikit-theme',theme);}catch(e){}"
    "try{var root=document.getElementById('root');if(root)root.setAttribute('data-uikit-theme',theme);}catch(e){}"
    "document.querySelectorAll('.chat-layout').forEach(function(el){"
    "el.classList.toggle('dark',dark);"
    "el.setAttribute('data-uikit-theme',theme);"
    "});"
    "document.querySelectorAll('.side-tab').forEach(function(el){"
    "el.classList.toggle('dark',dark);"
    "el.setAttribute('data-uikit-theme',theme);"
    "});"
    "try{localStorage.setItem('starsail-shell-theme',theme);}catch(e){}"
    "window.__starsailShellThemeLight=!!light;"
    "};"
    "window.__starsailPendingThemeLight=null;"
    "injectStyle();"
    "function findEditor(box){"
    "return box.querySelector('.ProseMirror')"
    "||box.querySelector('.tiptap')"
    "||box.querySelector('[contenteditable=\"true\"]');"
    "}"
    "function sendMessage(box){"
    "var nativeBtn=box.querySelector('.uikit-send-button:not(.uikit-send-button--disabled)');"
    "if(nativeBtn){nativeBtn.click();return;}"
    "var ed=findEditor(box);"
    "if(!ed)return;"
    "ed.focus();"
    "['keydown','keypress','keyup'].forEach(function(type){"
    "var ev=new KeyboardEvent(type,{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true,cancelable:true});"
    "ed.dispatchEvent(ev);"
    "});"
    "}"
    "function addSendButton(){"
    "var box=document.querySelector('.uikit-message-input');"
    "if(!box)return;"
    "if(box.querySelector('.starsail-send-btn'))return;"
    "var wrap=box.querySelector('.uikit-message-input__wrapper')||box;"
    "var btn=document.createElement('button');"
    "btn.type='button';"
    "btn.className='starsail-send-btn';"
    "btn.textContent='\u53d1\u9001';"
    "btn.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();sendMessage(box);});"
    "wrap.appendChild(btn);"
    "}"
    "function hideDisabledFeatures(){"
    "var sel='.uikit-audio-call-picker,.uikit-audio-call-picker__button,"
    ".uikit-video-call-picker,.uikit-video-call-picker__button,"
    ".red-packet-action,button.red-packet-action';"
    "document.querySelectorAll(sel).forEach(function(el){"
    "el.style.setProperty('display','none','important');"
    "el.style.setProperty('visibility','hidden','important');"
    "el.style.setProperty('pointer-events','none','important');"
    "});"
    "document.querySelectorAll('button[aria-label],button[title],[role=\"button\"][aria-label]').forEach(function(el){"
    "var t=((el.getAttribute('aria-label')||'')+(el.getAttribute('title')||'')).toLowerCase();"
    "if(/红包|red.?packet|语音通话|视频通话|audio.?call|video.?call/.test(t)){"
    "el.style.setProperty('display','none','important');"
    "el.style.setProperty('visibility','hidden','important');"
    "el.style.setProperty('pointer-events','none','important');"
    "}"
    "});"
    "}"
    "function patchEmptyChatPlaceholder(){"
    "var root=document.querySelector('.empty-placeholder');"
    "if(!root)return;"
    "var title=root.querySelector('.empty-title');"
    "var sub=root.querySelector('.empty-subtitle');"
    "var wantTitle='\u5982\u4eca\u6211\u52aa\u529b\u5954\u8dd1';"
    "var wantSub='\u4e0d\u8fc7\u662f\u4e3a\u4e86\u8ffd\u4e0a\u90a3\u4e2a\u66fe\u7ecf\u88ab\u5bc4\u4e88\u539a\u671b\u7684\u81ea\u5df1';"
    "if(title){title.textContent=wantTitle;}"
    "if(sub){sub.textContent=wantSub;}"
    "root.setAttribute('data-starsail-empty-quote','v3');"
    "}"
    "function tick(){"
    "injectStyle();"
    "hideDisabledFeatures();"
    "addSendButton();"
    "patchEmptyChatPlaceholder();"
    "if(typeof window.__starsailUniEmojiTick==='function'){"
    "try{window.__starsailUniEmojiTick();}catch(e){}"
    "}"
    "if(window.__starsailPendingThemeLight!==null){"
    "window.__starsailApplyTheme(window.__starsailPendingThemeLight);"
    "window.__starsailPendingThemeLight=null;"
    "}else if(!window.__starsailThemeBootstrapped){"
    "window.__starsailThemeBootstrapped=true;"
    "try{"
    "var t=localStorage.getItem('starsail-shell-theme');"
    "if(t==='dark'||t==='light')window.__starsailApplyTheme(t==='light');"
    "}catch(e){}"
    "}"
    "}"
    "if(document.readyState==='loading'){"
    "document.addEventListener('DOMContentLoaded',tick);"
    "}else{tick();}"
    "var __shellTickTimer=null;"
    "function scheduleShellTick(){"
    "if(__shellTickTimer)return;"
    "__shellTickTimer=setTimeout(function(){__shellTickTimer=null;tick();},350);"
    "}"
    "try{new MutationObserver(scheduleShellTick).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}"
    "setInterval(tick,2500);"
    "})();"
)

STARSAIL_NOTIFY_JS = r"""
(function initStarsailMessageNotify() {
    try {
        const host = (location.hostname || '').toLowerCase();
        if (!host.includes('starsail.vip')) return;
        if (window.__starsailNotifyInstalled) return;
        window.__starsailNotifyInstalled = true;

        const convMap = Object.create(null);
        const pending = [];
        const recentNotifyAt = Object.create(null);
        let primed = false;
        let priming = false;
        let lastBadgeCount = -1;
        const NOTIFY_DEDUP_MS = 2500;
        let runtimeDiscoverDone = false;
        let sdkHooksInstalled = false;
        let lastDomScanAt = 0;

        const scheduleNotifyTick = (() => {
            let timer = null;
            return (waitMs) => {
                if (timer) return;
                timer = setTimeout(() => {
                    timer = null;
                    tick();
                }, waitMs || 180);
            };
        })();

        const findFiber = (dom) => {
            if (!dom) return null;
            const key = Object.keys(dom).find((k) =>
                k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$')
            );
            return key ? dom[key] : null;
        };

        const pickChatChannel = (val) => {
            if (!val || typeof val !== 'object') return null;
            if (typeof val.getSnapshot === 'function'
                && typeof val.subscribe === 'function'
                && val.convStore) {
                return val;
            }
            return null;
        };

        const pickChatEngine = (val) => {
            if (!val || typeof val !== 'object') return null;
            if (typeof val.getTotalUnreadMessageCount === 'function'
                && val.chat
                && typeof val.chat.on === 'function') {
                return val;
            }
            if (typeof val.on === 'function'
                && typeof val.getTotalUnreadMessageCount === 'function') {
                return {
                    chat: val,
                    EVENT: val.EVENT,
                    getTotalUnreadMessageCount: () => val.getTotalUnreadMessageCount(),
                };
            }
            if (val.client) return pickChatEngine(val.client);
            return null;
        };

        const scanRuntimeValue = (val, seen, depth) => {
            if (val === null || val === undefined) return;
            if ((depth || 0) > 8) return;
            const t = typeof val;
            if (t !== 'object' && t !== 'function') return;
            if (seen.has(val)) return;
            seen.add(val);
            const channel = pickChatChannel(val);
            if (channel) window.__starsailChatChannel = channel;
            const engine = pickChatEngine(val);
            if (engine) window.__starsailChatEngine = engine;
            if (window.__starsailChatChannel && window.__starsailChatEngine) return;
            if (Array.isArray(val)) {
                for (let i = 0; i < val.length && i < 40; i++) {
                    scanRuntimeValue(val[i], seen, (depth || 0) + 1);
                }
                return;
            }
            try {
                const keys = Object.keys(val);
                for (let i = 0; i < keys.length && i < 30; i++) {
                    scanRuntimeValue(val[keys[i]], seen, (depth || 0) + 1);
                }
            } catch (e) {}
        };

        const discoverRuntime = (force) => {
            if (!force && runtimeDiscoverDone) {
                return !!(window.__starsailChatChannel || window.__starsailChatEngine);
            }
            if (window.__starsailChatChannel && window.__starsailChatEngine) {
                runtimeDiscoverDone = true;
                return true;
            }
            const roots = [
                document.querySelector('.chat-layout'),
                document.getElementById('root'),
            ].filter(Boolean);
            const visited = new Set();
            const seen = new Set();
            let steps = 0;
            const maxSteps = 2500;
            for (const root of roots) {
                let fiber = findFiber(root);
                const stack = [];
                if (fiber) stack.push(fiber);
                while (stack.length && steps < maxSteps) {
                    fiber = stack.pop();
                    if (!fiber || visited.has(fiber)) continue;
                    visited.add(fiber);
                    steps += 1;
                    let hook = fiber.memoizedState;
                    while (hook) {
                        scanRuntimeValue(hook.memoizedState, seen, 0);
                        if (window.__starsailChatChannel && window.__starsailChatEngine) {
                            runtimeDiscoverDone = true;
                            return true;
                        }
                        hook = hook.next;
                    }
                    if (fiber.child) stack.push(fiber.child);
                    if (fiber.sibling) stack.push(fiber.sibling);
                }
            }
            runtimeDiscoverDone = true;
            return !!(window.__starsailChatChannel || window.__starsailChatEngine);
        };

        const getChannelSnapshot = () => {
            try {
                const ch = window.__starsailChatChannel;
                return ch && typeof ch.getSnapshot === 'function' ? ch.getSnapshot() : null;
            } catch (e) {
                return null;
            }
        };

        const readStoreUnreadCount = () => {
            try {
                const snap = getChannelSnapshot();
                if (snap && snap.totalUnreadCount > 0) return snap.totalUnreadCount;
                const eng = window.__starsailChatEngine;
                if (eng && typeof eng.getTotalUnreadMessageCount === 'function') {
                    const n = eng.getTotalUnreadMessageCount();
                    if (typeof n === 'number' && n > 0) return n;
                }
            } catch (e) {}
            return 0;
        };

        const readStarsailUnreadCount = () => {
            let count = 0;
            try {
                document.querySelectorAll(
                    '.uikit-conversationPreview__unread, .uikit-avatar-badge__unread'
                ).forEach((el) => {
                    const t = (el.innerText || el.textContent || '').trim();
                    const n = parseInt(t, 10);
                    if (!isNaN(n) && n > 0) count += n;
                    else if (el.classList.contains('uikit-avatar-badge__unread--dot')) count += 1;
                    else if (t) count += 1;
                });
                if (!count) {
                    count = document.querySelectorAll(
                        '.uikit-conversationPreview--unread'
                    ).length;
                }
            } catch (e) {}
            if (count > 0) return count;
            try { return readStoreUnreadCount(); } catch (e) { return 0; }
        };

        const syncBadge = (countOverride) => {
            const count = (typeof countOverride === 'number' && countOverride >= 0)
                ? countOverride
                : (window.__teamsReadUnreadCount ? window.__teamsReadUnreadCount() : 0);
            if (count === lastBadgeCount) return;
            lastBadgeCount = count;
            if (typeof window.__externalNotificationCallback !== 'function') return;
            try { window.__externalNotificationCallback('unread', '', '', count); } catch (e) {}
        };

        const origReadUnread = window.__teamsReadUnreadCount;
        window.__teamsReadUnreadCount = function() {
            const starsail = readStarsailUnreadCount();
            if (starsail > 0) return starsail;
            if (typeof origReadUnread === 'function') return origReadUnread();
            return 0;
        };

        const postNotify = (sender, msg, unreadHint) => {
            if (window.__TEAMS_NOTIFICATIONS_OFF) return;
            if (priming) return;
            const bodyHash = (() => {
                let h = 2166136261;
                const s = String(msg || '');
                for (let i = 0; i < s.length; i++) {
                    h ^= s.charCodeAt(i);
                    h = Math.imul(h, 16777619);
                }
                return (h >>> 0).toString(16);
            })();
            const soundKey = String(sender || '') + '|' + bodyHash;
            const now = Date.now();
            if (recentNotifyAt[soundKey] && now - recentNotifyAt[soundKey] < NOTIFY_DEDUP_MS) {
                return;
            }
            recentNotifyAt[soundKey] = now;
            const count = window.__teamsReadUnreadCount ? window.__teamsReadUnreadCount() : 0;
            const stableId = 'starsail_' + bodyHash;
            const payload = [
                'teams_notify',
                String(sender || '新消息'),
                stableId + '|' + String(msg || '新消息'),
                count,
            ];
            if (typeof window.__externalNotificationCallback !== 'function') {
                pending.push(payload);
                return;
            }
            try { window.__externalNotificationCallback(...payload); } catch (e) {}
        };

        const flushPending = () => {
            if (typeof window.__externalNotificationCallback !== 'function') return;
            while (pending.length) {
                const p = pending.shift();
                try { window.__externalNotificationCallback(...p); } catch (e) {}
            }
        };
        setInterval(flushPending, 1000);

        const getConversationItems = () => {
            const items = document.querySelectorAll('.uikit-conversationPreview');
            if (items.length) return items;
            return document.querySelectorAll('.uikit-conversationItem');
        };

        const readConversationUnread = (item) => {
            let unread = 0;
            const unreadEl = item.querySelector('.uikit-conversationPreview__unread');
            if (unreadEl) {
                const n = parseInt((unreadEl.innerText || unreadEl.textContent || '').trim(), 10);
                unread = isNaN(n) ? 1 : n;
            } else if (item.classList.contains('uikit-conversationPreview--unread')) {
                unread = 1;
            }
            if (!unread) {
                const badge = item.querySelector('.uikit-avatar-badge__unread');
                if (badge) {
                    const n = parseInt((badge.innerText || badge.textContent || '').trim(), 10);
                    unread = isNaN(n) ? 1 : n;
                }
            }
            return unread;
        };

        const updateConvEntry = (key, abstract, unread, convId) => {
            if (!key) return;
            const prev = convMap[key];
            const prevAbstract = prev ? (prev.abstract || '') : '';
            const prevUnread = prev ? (prev.unread || 0) : 0;
            const cid = convId || (prev && prev.convId) || '';
            convMap[key] = { abstract, unread, convId: cid };
            if (!primed || priming) return;

            const abstractChanged = !!(abstract && abstract !== prevAbstract);
            const unreadIncreased = unread > prevUnread;
            const shouldNotify = () => {
                if (!isChatPaneVisible()) return true;
                const activeId = getActiveConversationId();
                if (!activeId) return true;
                if (!cid) return true;
                return cid !== activeId;
            };

            if (!prev && unread > 0) {
                postNotify(key, abstract || '新消息', unread);
                return;
            }
            if (unreadIncreased && shouldNotify()) {
                postNotify(key, abstract || '新消息', unread);
                return;
            }
            if (abstractChanged && unread > 0 && shouldNotify()) {
                postNotify(key, abstract, unread);
            }
        };

        const scanStoreConversations = () => {
            const snap = getChannelSnapshot();
            if (!snap || !Array.isArray(snap.conversationList) || !snap.conversationList.length) {
                return false;
            }
            snap.conversationList.forEach((conv) => {
                const cid = String(conv.conversationID || '').trim();
                const key = cid || String(conv.title || conv.showName || '').trim();
                const abstract = String(
                    conv.lastMessage?.messageForShow
                    || conv.abstract
                    || conv.lastMessage?.payload?.text
                    || ''
                ).trim();
                const unread = Number(conv.unreadCount) || 0;
                updateConvEntry(key, abstract, unread, cid);
            });
            return true;
        };

        const scanConversations = () => {
            const items = getConversationItems();
            if (items.length) {
                const now = Date.now();
                if (now - lastDomScanAt < 100) return true;
                lastDomScanAt = now;
                items.forEach((item) => {
                    const titleEl = item.querySelector('.uikit-conversationPreview__title');
                    const key = (titleEl && titleEl.innerText.trim())
                        || (item.getAttribute('aria-label') || '').trim().slice(0, 60)
                        || String(item.innerText || '').slice(0, 80);
                    const abstractEl = item.querySelector('.uikit-conversationPreview__abstract');
                    const abstract = abstractEl ? abstractEl.innerText.trim() : '';
                    const unread = readConversationUnread(item);
                    updateConvEntry(key, abstract, unread, '');
                });
                return true;
            }
            if (!window.__starsailChatChannel && !window.__starsailChatEngine) return false;
            return scanStoreConversations();
        };

        let ticking = false;

        const isChatPaneVisible = () => {
            const input = document.querySelector('.uikit-message-input');
            const list = document.querySelector('.uikit-message-list');
            if (!input || !list) return false;
            const r = input.getBoundingClientRect();
            if (r.width < 8 || r.height < 8) return false;
            const st = getComputedStyle(input);
            return st.display !== 'none' && st.visibility !== 'hidden' && parseFloat(st.opacity || '1') > 0.05;
        };

        const getActiveConversationId = () => {
            const snap = getChannelSnapshot();
            return snap && snap.activeConversationID ? String(snap.activeConversationID) : '';
        };

        const resolveMessageConversationId = (msg) => {
            if (!msg) return '';
            const direct = String(msg.conversationID || msg.conversationId || '').trim();
            if (direct) return direct;
            const to = String(msg.to || msg.toAccount || '').trim();
            const from = String(msg.from || msg.fromAccount || '').trim();
            if (to && (to.startsWith('GROUP') || to.startsWith('C2C'))) return to;
            if (msg.groupID) {
                const gid = String(msg.groupID);
                return gid.startsWith('GROUP') ? gid : 'GROUP' + gid;
            }
            if (to) return to.startsWith('GROUP') ? to : 'GROUP' + to;
            if (from) return from.startsWith('C2C') ? from : 'C2C' + from;
            return '';
        };

        const shouldRingForMessage = (msg) => {
            if (!msg || msg.flow === 'out' || msg.isRead) return false;
            if (!isChatPaneVisible()) return true;
            const activeId = getActiveConversationId();
            if (!activeId) return true;
            const msgConv = resolveMessageConversationId(msg);
            if (!msgConv) return true;
            return msgConv !== activeId;
        };

        const messagePreview = (msg) => {
            if (!msg) return '新消息';
            if (msg.messageForShow) return String(msg.messageForShow);
            const payload = msg.payload || {};
            if (payload.text) return String(payload.text);
            if (payload.description) return String(payload.description);
            return '新消息';
        };

        const notifyIncomingMessages = (list) => {
            const arr = Array.isArray(list) ? list : [list];
            let rang = false;
            arr.forEach((msg) => {
                if (!shouldRingForMessage(msg)) return;
                const sender = String(msg.nick || msg.nameCard || msg.from || '新消息');
                postNotify(sender, messagePreview(msg), 1);
                rang = true;
            });
            return rang;
        };

        const scanIncomingMessages = () => {
            document.querySelectorAll('.uikit-message-layout--left').forEach((el) => {
                if (el.hasAttribute('data-starsail-notified')) return;
                el.setAttribute('data-starsail-notified', 'true');
            });
        };

        const tick = () => {
            if (ticking) return;
            ticking = true;
            try {
                scanConversations();
                scanIncomingMessages();
                syncBadge();
                flushPending();
            } finally {
                ticking = false;
            }
        };

        const installSdkHooks = () => {
            if (sdkHooksInstalled) return;
            sdkHooksInstalled = true;
            discoverRuntime(true);
            const eng = window.__starsailChatEngine;
            if (eng && eng.chat && !window.__starsailSdkChatHooked) {
                window.__starsailSdkChatHooked = true;
                const chat = eng.chat;
                const EVT = eng.EVENT || chat.EVENT || {};
                const onMsg = EVT.MESSAGE_RECEIVED || 'onMessageReceived';
                const onUnread = EVT.TOTAL_UNREAD_MESSAGE_COUNT_UPDATED
                    || 'onTotalUnreadMessageCountUpdated';
                const onConv = EVT.CONVERSATION_LIST_UPDATED || 'onConversationListUpdated';
                const handleMsg = (list) => {
                    notifyIncomingMessages(list);
                    scheduleNotifyTick(primed ? 80 : 60);
                };
                const handleUnread = (count) => {
                    const n = (typeof count === 'number') ? count : readStoreUnreadCount();
                    syncBadge(n);
                    if (!ticking) {
                        scanConversations();
                        flushPending();
                    }
                };
                try {
                    chat.on(onMsg, handleMsg);
                    chat.on(onUnread, handleUnread);
                    chat.on(onConv, () => scheduleNotifyTick(120));
                } catch (e) {}
            }
            const ch = window.__starsailChatChannel;
            if (ch && !window.__starsailChannelHooked) {
                window.__starsailChannelHooked = true;
                ch.subscribe(() => scheduleNotifyTick(120));
            }
        };

        const primeBaseline = () => {
            if (primed) return;
            installSdkHooks();
            document.querySelectorAll('.uikit-message-layout--left').forEach((el) => {
                el.setAttribute('data-starsail-notified', 'true');
            });
            priming = true;
            scanConversations();
            priming = false;
            primed = true;
            syncBadge();
        };

        const startObserver = () => {
            const root = document.querySelector('.chat-layout') || document.body;
            if (!root) {
                setTimeout(startObserver, 500);
                return;
            }
            installSdkHooks();
            try {
                const obs = new MutationObserver(() => scheduleNotifyTick(220));
                obs.observe(root, { childList: true, subtree: true });
                window.__starsailNotifyObserver = obs;
            } catch (e) {}
            if (!window.__starsailNotifyInterval) {
                window.__starsailNotifyInterval = setInterval(tick, 800);
            }
            setTimeout(primeBaseline, 400);
            tick();
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', startObserver);
        } else {
            startObserver();
        }
    } catch (e) {}
})();
"""

STARSAIL_EMOJI_JS = r"""
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
        let savedEditorRange = null;

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

        const isSelectionInEditor = (editor) => {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0 || !editor) return false;
            const node = sel.anchorNode;
            return !!(node && editor.contains(node));
        };

        const saveEditorSelection = (editor) => {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0 || !editor) return;
            const range = sel.getRangeAt(0);
            if (!editor.contains(range.commonAncestorContainer)) return;
            savedEditorRange = range.cloneRange();
        };

        const placeCursorAtEnd = (editor) => {
            if (!editor) return;
            const range = document.createRange();
            range.selectNodeContents(editor);
            range.collapse(false);
            const sel = window.getSelection();
            if (!sel) return;
            sel.removeAllRanges();
            sel.addRange(range);
            savedEditorRange = range.cloneRange();
        };

        const restoreEditorSelection = (editor) => {
            if (!editor) return;
            editor.focus();
            const sel = window.getSelection();
            if (!sel) return;
            if (savedEditorRange) {
                try {
                    const start = savedEditorRange.startContainer;
                    const inEditor = editor.contains(start)
                        || (start && start.parentNode && editor.contains(start.parentNode));
                    if (inEditor) {
                        sel.removeAllRanges();
                        sel.addRange(savedEditorRange);
                        return;
                    }
                } catch (e) {}
            }
            placeCursorAtEnd(editor);
        };

        const insertUnicodeEmoji = (editor, emoji) => {
            if (!editor || !emoji) return;
            restoreEditorSelection(editor);
            try {
                if (document.execCommand('insertText', false, emoji)) {
                    saveEditorSelection(editor);
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
                    savedEditorRange = range.cloneRange();
                } else {
                    editor.appendChild(document.createTextNode(emoji));
                    placeCursorAtEnd(editor);
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
                item.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                });
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
            const editor = findEditor(box);
            if (editor) saveEditorSelection(editor);
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
            document.addEventListener('selectionchange', () => {
                const box = activeInputBox || document.querySelector('.uikit-message-input');
                const editor = findEditor(box);
                if (editor && isSelectionInEditor(editor)) {
                    saveEditorSelection(editor);
                }
            });
            document.addEventListener('input', (e) => {
                if (!(e.target instanceof Element)) return;
                const box = e.target.closest('.uikit-message-input');
                if (!box) return;
                const editor = findEditor(box);
                if (editor && editor.contains(e.target)) {
                    saveEditorSelection(editor);
                }
            }, true);
            document.addEventListener('click', (e) => {
                const target = e.target;
                if (!(target instanceof Element)) return;

                const icon = target.closest('.uikit-emoji-picker__icon');
                const picker = !icon ? target.closest('.uikit-emoji-picker') : null;
                const anchor = icon || (picker && !target.closest('.uikit-emoji-picker__list') ? picker : null);
                if (anchor) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    const box = document.querySelector('.uikit-message-input');
                    hideNativeEmojiLists();
                    togglePanel(anchor, box);
                    return;
                }

                if (!target.closest('#' + PANEL_ID)) {
                    closePanel();
                }
            }, true);
            document.addEventListener('pointerdown', (e) => {
                if (!(e.target instanceof Element)) return;
                if (e.target.closest('.uikit-emoji-picker__icon')) {
                    const box = document.querySelector('.uikit-message-input');
                    const editor = findEditor(box);
                    if (editor) saveEditorSelection(editor);
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
"""

STARSAIL_INTERACTION_JS = r"""
(function initStarsailInteraction() {
    try {
        const host = (location.hostname || '').toLowerCase();
        if (!host.includes('starsail.vip')) return;
        if (window.__starsailInteractionInstalled) return;
        window.__starsailInteractionInstalled = true;

        const blockZoomWheel = (e) => {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        };
        window.addEventListener('wheel', blockZoomWheel, { passive: false, capture: true });
        window.addEventListener('keydown', (e) => {
            if (!(e.ctrlKey || e.metaKey)) return;
            const k = e.key;
            if (k === '=' || k === '+' || k === '-' || k === '_' || k === '0') {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        }, true);

        const showToast = (message, isError) => {
            let el = document.getElementById('starsail-shell-toast');
            if (!el && document.body) {
                el = document.createElement('div');
                el.id = 'starsail-shell-toast';
                el.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);'
                    + 'z-index:2147483646;pointer-events:none;color:#fff;padding:8px 16px;border-radius:8px;';
                document.body.appendChild(el);
            }
            if (!el) return;
            el.textContent = message;
            el.style.background = isError ? 'rgba(220,53,69,.9)' : 'rgba(0,0,0,.8)';
            el.style.display = 'block';
            clearTimeout(window.__starsailShellToastTimer);
            window.__starsailShellToastTimer = setTimeout(() => {
                el.style.display = 'none';
            }, 2000);
        };

        const cachedUrls = window.__starsailCachedImageUrls
            || (window.__starsailCachedImageUrls = new Set());

        const getApi = () => {
            if (typeof window.connectTeamsBridge === 'function') {
                try { window.connectTeamsBridge(); } catch (e) {}
            }
            return (window.qtwebview2 && window.qtwebview2.api) ? window.qtwebview2.api : null;
        };

        const uint8ToBase64 = (bytes) => {
            let bin = '';
            const step = 0x8000;
            for (let i = 0; i < bytes.length; i += step) {
                bin += String.fromCharCode.apply(null, bytes.subarray(i, i + step));
            }
            return btoa(bin);
        };

        const waitBridgeReady = async (maxMs) => {
            const deadline = Date.now() + (maxMs || 4000);
            while (Date.now() < deadline) {
                if (typeof window.connectTeamsBridge === 'function') {
                    try { window.connectTeamsBridge(); } catch (e) {}
                }
                if (window.__starsailCopyCachedImage) return true;
                await new Promise((resolve) => setTimeout(resolve, 80));
            }
            return false;
        };

        const uploadImageCache = async (url, blob) => {
            if (!url || !blob || !blob.size || cachedUrls.has(url)) return true;
            if (!await waitBridgeReady()) return false;
            try {
                if (!window.__starsailBeginCacheImage) return false;
                const mime = (blob.type && blob.type.startsWith('image/')) ? blob.type : 'image/png';
                const buf = await blob.arrayBuffer();
                const bytes = new Uint8Array(buf);
                const chunkSize = 24000;
                const sessionId = await window.__starsailBeginCacheImage(url, bytes.length, mime);
                if (!sessionId) return false;
                for (let i = 0; i < bytes.length; i += chunkSize) {
                    const slice = bytes.subarray(i, Math.min(i + chunkSize, bytes.length));
                    await window.__starsailAppendCacheImage(sessionId, uint8ToBase64(slice));
                }
                const ok = await window.__starsailFinishCacheImage(sessionId);
                if (ok) cachedUrls.add(url);
                return !!ok;
            } catch (e) {
                return false;
            }
        };

        const fetchImageBlob = async (url, img) => {
            if (!url) return null;
            try {
                const resp = await fetch(url, { credentials: 'include', cache: 'force-cache' });
                if (resp.ok) {
                    const blob = await resp.blob();
                    if (blob && blob.size) return blob;
                }
            } catch (e) {}
            try {
                const blob = await new Promise((resolve, reject) => {
                    const xhr = new XMLHttpRequest();
                    xhr.open('GET', url, true);
                    xhr.responseType = 'blob';
                    xhr.onload = () => {
                        if (xhr.status >= 200 && xhr.status < 300 && xhr.response && xhr.response.size) {
                            resolve(xhr.response);
                        } else {
                            reject(new Error('xhr failed'));
                        }
                    };
                    xhr.onerror = () => reject(new Error('xhr error'));
                    xhr.send();
                });
                if (blob && blob.size) return blob;
            } catch (e) {}
            try {
                if (img && img.complete && (img.naturalWidth || img.width)) {
                    const w = img.naturalWidth || img.width;
                    const h = img.naturalHeight || img.height;
                    const c = document.createElement('canvas');
                    c.width = w;
                    c.height = h;
                    c.getContext('2d').drawImage(img, 0, 0);
                    const blob = await new Promise((resolve) => {
                        c.toBlob((b) => resolve(b), 'image/png', 0.92);
                    });
                    if (blob && blob.size) return blob;
                }
            } catch (e) {}
            return null;
        };

        const ensureImageCached = async (url, img) => {
            if (!url || cachedUrls.has(url)) return true;
            const blob = await fetchImageBlob(url, img);
            if (!blob) return false;
            return uploadImageCache(url, blob);
        };

        window.__starsailCacheImageByUrl = async (url) => {
            if (!url) return false;
            let img = null;
            const base = String(url).split('?')[0];
            document.querySelectorAll('img').forEach((el) => {
                if (img) return;
                const src = el.currentSrc || el.src || '';
                if (src === url || src.split('?')[0] === base) img = el;
            });
            return ensureImageCached(url, img);
        };

        const copyImage = async (img) => {
            const url = img.currentSrc || img.src || '';
            if (!url) {
                showToast('无图片地址', true);
                return;
            }
            if (!await waitBridgeReady()) {
                showToast('复制失败', true);
                return;
            }
            await ensureImageCached(url, img);
            try {
                if (window.__starsailCopyCachedImage && await window.__starsailCopyCachedImage(url)) {
                    showToast('已复制');
                    return;
                }
            } catch (e) {}
            cachedUrls.delete(url);
            await ensureImageCached(url, img);
            try {
                if (window.__starsailCopyCachedImage && await window.__starsailCopyCachedImage(url)) {
                    showToast('已复制');
                    return;
                }
            } catch (e) {}
            if (window.__teamsCopyImageUrl) {
                try { window.__teamsCopyImageUrl(url); } catch (e) {}
                showToast('正在复制…');
                return;
            }
            showToast('复制失败', true);
        };

        const findImgFromTarget = (target) => {
            if (!target) return null;
            if (target.tagName === 'IMG') return target;
            if (typeof target.closest !== 'function') return null;
            const direct = target.closest('img');
            if (direct) return direct;
            const host = target.closest('.uikit-image-message, .uikit-image-preview');
            return host ? host.querySelector('img') : null;
        };

        const isChatImage = (img) => {
            if (!img || img.tagName !== 'IMG') return false;
            if (img.closest(
                '.uikit-avatar, .side-tab, .conversation-list-panel, '
                + '.login-page, .login-panel, .uikit-face-message'
            )) {
                return false;
            }
            if (!img.closest(
                '.uikit-message-list, .chat-main, .chat-content-panel, .uikit-image-preview'
            )) {
                return false;
            }
            const src = (img.currentSrc || img.src || '').toLowerCase();
            if (!src || src.endsWith('.svg')) return false;
            if (src.includes('emoji_') || src.includes('/emoji/') || src.includes('emoticon')) {
                return false;
            }
            const w = img.naturalWidth || img.width || img.offsetWidth || 0;
            const h = img.naturalHeight || img.height || img.offsetHeight || 0;
            if (w > 0 && h > 0 && w < 36 && h < 36) return false;
            return true;
        };

        window.__starsailCopyImageFromUri = (imageUrl) => {
            if (!imageUrl) {
                showToast('无图片地址', true);
                return;
            }
            let matched = null;
            const base = String(imageUrl).split('?')[0];
            document.querySelectorAll('img').forEach((img) => {
                if (matched) return;
                const src = img.currentSrc || img.src || '';
                if (src === imageUrl || src.split('?')[0] === base) {
                    if (isChatImage(img)) matched = img;
                }
            });
            if (matched) {
                copyImage(matched);
                return;
            }
            (async () => {
                if (!await waitBridgeReady()) {
                    showToast('复制失败', true);
                    return;
                }
                await window.__starsailCacheImageByUrl(imageUrl);
                try {
                    if (window.__starsailCopyCachedImage && await window.__starsailCopyCachedImage(imageUrl)) {
                        showToast('已复制');
                        return;
                    }
                } catch (e) {}
                if (window.__teamsCopyImageUrl) {
                    try { window.__teamsCopyImageUrl(imageUrl); } catch (e2) {}
                    showToast('正在复制…');
                    return;
                }
                showToast('复制失败', true);
            })();
        };

        const isImagePreviewOpen = () => {
            const pv = document.querySelector('.uikit-image-preview');
            if (!pv) return false;
            const st = getComputedStyle(pv);
            const r = pv.getBoundingClientRect();
            return r.width > 8 && r.height > 8
                && st.display !== 'none'
                && st.visibility !== 'hidden'
                && st.opacity !== '0';
        };

        const findPreviewImage = (target) => {
            if (!target || typeof target.closest !== 'function') return null;
            const pv = target.closest('.uikit-image-preview');
            if (!pv || !isImagePreviewOpen()) return null;
            return pv.querySelector('.uikit-image-preview__img')
                || pv.querySelector('img')
                || findImgFromTarget(target);
        };

        window.__starsailCopyImageFromPoint = (x, y) => {
            if (!isImagePreviewOpen()) return false;
            const el = document.elementFromPoint(x, y);
            const img = findPreviewImage(el);
            if (!img) return false;
            copyImage(img);
            return true;
        };

        const onImageContextMenu = (e) => {
            const img = findPreviewImage(e.target);
            if (!img) return;
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            copyImage(img);
            return false;
        };

        const onImageLoadCache = (img) => {
            if (!isChatImage(img)) return;
            const url = img.currentSrc || img.src || '';
            if (!url || cachedUrls.has(url)) return;
            ensureImageCached(url, img);
        };

        const scanChatImages = () => {
            document.querySelectorAll('img').forEach((img) => {
                if (!isChatImage(img)) return;
                if (img.complete && (img.naturalWidth || img.width)) {
                    onImageLoadCache(img);
                    return;
                }
                if (!img.hasAttribute('data-starsail-cache-hook')) {
                    img.setAttribute('data-starsail-cache-hook', '1');
                    img.addEventListener('load', () => onImageLoadCache(img), { once: true });
                }
            });
        };

        const bootImageCopy = () => {
            if (window.__starsailImageCopyBooted) return;
            window.__starsailImageCopyBooted = true;
            document.addEventListener('contextmenu', onImageContextMenu, true);
            window.addEventListener('contextmenu', onImageContextMenu, true);
            scanChatImages();
            if (window.__starsailImgCacheObserver) {
                window.__starsailImgCacheObserver.disconnect();
            }
            let imgScanTimer = null;
            const scheduleImgScan = () => {
                if (imgScanTimer) return;
                imgScanTimer = setTimeout(() => {
                    imgScanTimer = null;
                    scanChatImages();
                }, 400);
            };
            window.__starsailImgCacheObserver = new MutationObserver(scheduleImgScan);
            const imgRoot = document.querySelector('.chat-layout')
                || document.querySelector('.uikit-message-list')
                || document.body;
            if (imgRoot) {
                window.__starsailImgCacheObserver.observe(imgRoot, {
                    childList: true,
                    subtree: true,
                });
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', bootImageCopy);
        } else {
            bootImageCopy();
        }
        setInterval(() => {
            if (!window.__starsailImageCopyBooted && document.body) bootImageCopy();
        }, 5000);
    } catch (e) {}
})();
"""

STARSAIL_ESC_CHAT_JS = r"""
(function initStarsailEscBackToList() {
    try {
        const host = (location.hostname || '').toLowerCase();
        if (!host.includes('starsail.vip')) return;
        if (window.__starsailEscBackHook) return;
        window.__starsailEscBackHook = true;

        const visible = (el) => {
            if (!el) return false;
            const r = el.getBoundingClientRect();
            const st = getComputedStyle(el);
            return r.width > 8 && r.height > 8
                && st.visibility !== 'hidden'
                && st.display !== 'none'
                && st.opacity !== '0';
        };

        const findFiber = (dom) => {
            if (!dom) return null;
            const key = Object.keys(dom).find((k) =>
                k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$')
            );
            return key ? dom[key] : null;
        };

        const pickSetActiveConversation = (snap) => {
            if (!snap || typeof snap !== 'object') return null;
            if (typeof snap.setActiveConversation === 'function') return snap.setActiveConversation;
            return null;
        };

        const discoverSetActiveConversation = () => {
            if (typeof window.__starsailSetActiveConversation === 'function') {
                return window.__starsailSetActiveConversation;
            }
            const roots = [
                document.querySelector('.chat-layout'),
                document.querySelector('.chat-main'),
                document.querySelector('.uikit-message-input'),
                document.querySelector('.uikit-conversationPreview--active'),
                document.querySelector('.conversation-list-panel'),
                document.getElementById('root'),
            ].filter(Boolean);
            const visited = new Set();
            for (const root of roots) {
                let fiber = findFiber(root);
                const stack = [];
                while (fiber) {
                    if (visited.has(fiber)) {
                        fiber = stack.pop();
                        continue;
                    }
                    visited.add(fiber);
                    let hook = fiber.memoizedState;
                    while (hook) {
                        const fn = pickSetActiveConversation(hook.memoizedState);
                        if (fn) {
                            window.__starsailSetActiveConversation = fn;
                            return fn;
                        }
                        hook = hook.next;
                    }
                    if (fiber.child) stack.push(fiber.child);
                    if (fiber.sibling) stack.push(fiber.sibling);
                    fiber = stack.pop();
                }
            }
            return null;
        };

        const isInActiveChat = () => {
            if (!document.querySelector('.chat-layout')) return false;
            const activeItem = document.querySelector('.uikit-conversationPreview--active');
            const msgInput = document.querySelector('.uikit-message-input');
            const msgList = document.querySelector('.uikit-message-list');
            if (!activeItem && !visible(msgInput)) return false;
            if (visible(msgInput) || visible(msgList)) return true;
            return !!activeItem;
        };

        const hasBlockingOverlay = () => {
            const selectors = [
                '.red-packet-modal',
                '.red-packet-detail',
                '.uikit-group-call-dialog',
                '[role="dialog"]',
                '.uikit-chat-setting',
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (visible(el)) return true;
            }
            return false;
        };

        const clickBackIfAny = () => {
            const back = document.querySelector(
                '.uikit-chat-header__back-icon button, '
                + '.uikit-chat-header__back-icon .icon-button, '
                + '.uikit-chat-header__back-icon, '
                + '.tui-kit-icon-back'
            );
            if (!back) return false;
            try {
                back.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                back.click();
                return true;
            } catch (e) {
                return false;
            }
        };

        window.__starsailEscCloseChat = function starsailEscCloseChat() {
            try {
                if (!isInActiveChat() || hasBlockingOverlay()) return false;
                if (clickBackIfAny()) return true;
                const setActive = discoverSetActiveConversation();
                if (setActive) {
                    setActive('');
                    return true;
                }
            } catch (e) {}
            return false;
        };

        window.addEventListener('keydown', function onStarsailEsc(e) {
            try {
                if (!e || e.key !== 'Escape' || e.defaultPrevented) return;
                if (!isInActiveChat() || hasBlockingOverlay()) return;
                const closed = window.__starsailEscCloseChat();
                if (closed) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }
            } catch (err) {}
        }, true);
    } catch (e) {}
})();
"""

STARSAIL_LOGIN_JS_TEMPLATE = r"""
(function() {
    const account = __ACCOUNT_JSON__;
    const password = __PASSWORD_JSON__;
    const alreadySubmitted = __SUBMITTED_JSON__;
    const visible = (el) => el && el.offsetParent !== null
        && getComputedStyle(el).visibility !== 'hidden';
    const setVal = (el, val) => {
        if (!el) return;
        el.focus();
        try {
            const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
            if (desc && desc.set) desc.set.call(el, val);
            else el.value = val;
        } catch (e) { el.value = val; }
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
    };
    const clickEl = (el) => {
        if (!el || !visible(el)) return false;
        try { el.click(); return true; } catch (e) { return false; }
    };
    const detectLoginError = () => {
        const panel = document.querySelector('.login-panel');
        const chunks = [];
        if (panel) chunks.push(panel.innerText || '');
        if (document.body) chunks.push(document.body.innerText || '');
        const body = chunks.join(' ').slice(0, 1800);
        const patterns = [
            /账号.{0,10}不存在/,
            /密码.{0,12}(不正确|错误|有误|无效)/,
            /账号.{0,10}(或|和).{0,10}密码.{0,10}(错误|不正确|有误)/,
            /登录失败/,
            /账号.{0,10}(错误|无效|不正确|有误)/,
            /incorrect.{0,12}password/i,
            /user.{0,12}not.{0,12}(found|exist)/i,
            /invalid.{0,12}(account|password|credentials)/i,
        ];
        for (let i = 0; i < patterns.length; i++) {
            const m = body.match(patterns[i]);
            if (m) return m[0];
        }
        if (panel) {
            const nodes = panel.querySelectorAll(
                '[class*="error"],[class*="alert"],[role="alert"],.login-error,.error-text'
            );
            for (let j = 0; j < nodes.length; j++) {
                const el = nodes[j];
                if (!visible(el)) continue;
                const t = (el.innerText || '').trim();
                if (t && t.length > 0 && t.length < 120) return t;
            }
        }
        return '';
    };
    const panel = document.querySelector('.login-panel');
    if (!panel) return JSON.stringify({ok: false, step: 'wait'});
    const inputs = panel.querySelectorAll('.login-field input');
    if (inputs.length < 2) return JSON.stringify({ok: false, step: 'wait'});
    const accountInput = inputs[0];
    const passInput = inputs[1];
    const loginBtn = panel.querySelector('.login-button');
    const errText = detectLoginError();
    if (errText) {
        return JSON.stringify({ok: false, step: 'login_error', message: errText});
    }
    if (alreadySubmitted) {
        return JSON.stringify({ok: false, step: 'submitted_wait'});
    }
    const curAccount = (accountInput.value || '').trim();
    if (!curAccount || curAccount.toLowerCase() !== String(account).toLowerCase()) {
        setVal(accountInput, account);
    }
    if (password && visible(passInput)) {
        setVal(passInput, password);
    }
    if (loginBtn && visible(loginBtn)) {
        clickEl(loginBtn);
        return JSON.stringify({ok: false, step: 'submitted'});
    }
    return JSON.stringify({ok: false, step: 'wait'});
})();
"""

STARSAIL_LOGIN_BUSY_JS = r"""
(function() {
    if (window.__starsailLoginBusyReady) return;
    window.__starsailLoginBusyReady = true;
    var hostOk = false;
    try {
        hostOk = /starsail\.vip/i.test(location.hostname || '');
    } catch (e) {}
    if (!hostOk) return;

    var root = document.documentElement;
    root.setAttribute('data-starsail-client', '1');
    root.setAttribute('data-starsail-busy', '1');

    var crit = document.createElement('style');
    crit.id = 'starsail-busy-critical';
    crit.textContent = [
        'html[data-starsail-client="1"],html[data-starsail-client="1"] body{background:#f3f3f3!important}',
        'html[data-starsail-client="1"] .login-page,',
        'html[data-starsail-client="1"] .login-panel{opacity:0!important;',
        'visibility:hidden!important;pointer-events:none!important;',
        'position:fixed!important;left:-10000px!important;width:1px!important;',
        'height:1px!important;overflow:hidden!important}',
        '#starsail-login-busy-overlay{position:fixed;inset:0;z-index:2147483647;',
        'display:flex!important;align-items:center;justify-content:center;',
        'background:#f3f3f3;flex-direction:column}',
        'html[data-starsail-chat-ready="1"] #starsail-login-busy-overlay{display:none!important}',
        '.starsail-login-busy-spinner{width:36px;height:36px;margin:0 auto 16px;',
        'border:3px solid rgba(37,99,235,.18);border-top-color:#2563eb;',
        'border-radius:50%;animation:starsail-busy-spin .75s linear infinite}',
        '@keyframes starsail-busy-spin{to{transform:rotate(360deg)}}',
        '.starsail-login-busy-text{font-size:16px;font-weight:600;color:#1a1f2e}',
        '.starsail-bouncy-dots{display:inline-flex;align-items:flex-end;gap:4px;',
        'margin-left:2px;height:1em;vertical-align:baseline}',
        '.starsail-bouncy-dots i{display:inline-block;width:5px;height:5px;',
        'border-radius:50%;background:currentColor;',
        'animation:starsail-dot-bounce .72s cubic-bezier(.45,.05,.55,.95) infinite}',
        '.starsail-bouncy-dots i:nth-child(1){animation-delay:0s}',
        '.starsail-bouncy-dots i:nth-child(2){animation-delay:.12s}',
        '.starsail-bouncy-dots i:nth-child(3){animation-delay:.24s}',
        '@keyframes starsail-dot-bounce{0%,70%,100%{transform:translateY(0)}',
        '35%{transform:translateY(-7px)}}'
    ].join('');
    if (root.firstChild) root.insertBefore(crit, root.firstChild);
    else root.appendChild(crit);

    function ensureOverlay() {
        var ov = document.getElementById('starsail-login-busy-overlay');
        if (!ov) {
            ov = document.createElement('div');
            ov.id = 'starsail-login-busy-overlay';
            ov.innerHTML = '<div class="starsail-login-busy-card">'
                + '<div class="starsail-login-busy-spinner"></div>'
                + '<div class="starsail-login-busy-text">正在登入中'
                + '<span class="starsail-bouncy-dots">'
                + '<i></i><i></i><i></i></span></div></div>';
        }
        var host = document.body || root;
        if (ov.parentNode !== host) host.appendChild(ov);
        else host.appendChild(ov);
        return ov;
    }
    ensureOverlay();

    function showBusy() {
        try {
            root.removeAttribute('data-starsail-chat-ready');
            root.setAttribute('data-starsail-busy', '1');
            ensureOverlay();
        } catch (e) {}
    }
    function hideBusy() {
        try {
            root.setAttribute('data-starsail-chat-ready', '1');
            root.removeAttribute('data-starsail-busy');
        } catch (e) {}
    }
    window.__starsailShowLoginBusy = showBusy;
    window.__starsailHideLoginBusy = hideBusy;
    window.__starsailBusyActive = function() {
        try {
            var chat = document.querySelector('.chat-layout');
            if (chat) {
                var login = document.querySelector('.login-page, .login-panel');
                if (login) {
                    var ls = getComputedStyle(login);
                    var loginVisible = ls
                        && ls.display !== 'none'
                        && ls.visibility !== 'hidden'
                        && parseFloat(ls.opacity || '1') > 0.05
                        && login.offsetParent !== null;
                    if (loginVisible) {
                        showBusy();
                        return 'busy';
                    }
                }
                return 'chat';
            }
            if (root.getAttribute('data-starsail-busy') === '1') return 'busy';
            var ov = document.getElementById('starsail-login-busy-overlay');
            if (ov) {
                var st = getComputedStyle(ov);
                if (st && st.display !== 'none' && st.visibility !== 'hidden') return 'busy';
            }
            if (document.querySelector('.login-page, .login-panel')) {
                showBusy();
                return 'busy';
            }
            return 'wait';
        } catch (e) {
            return 'wait';
        }
    };

    try {
        var obs = new MutationObserver(function() {
            try {
                if (document.querySelector('.chat-layout')) return;
                if (document.querySelector('.login-page') || document.querySelector('.login-panel')) {
                    showBusy();
                }
            } catch (e) {}
        });
        obs.observe(root, { childList: true, subtree: true });
        setInterval(function() {
            try {
                if (document.querySelector('.chat-layout')) return;
                if (document.querySelector('.login-page') || document.querySelector('.login-panel')) {
                    showBusy();
                }
            } catch (e) {}
        }, 120);
    } catch (e) {}
})();
"""
