import streamlit as st
import json
import os
import base64
import time
from datetime import datetime

# 데이터 저장 파일 경로 설정
DATA_FILE = "tongil_talk_data.json"

# ==========================================
# 0. 메모리 기반 초고속 글로벌 메시지 버퍼
# ==========================================
@st.cache_resource
def get_global_chat_store():
    return []

GLOBAL_CHAT_STORE = get_global_chat_store()

# ==========================================
# 1. 파일 데이터 로드 및 저장 함수
# ==========================================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "profiles" not in data:
                    data["profiles"] = []
                if "sns_posts" not in data:
                    data["sns_posts"] = []
                if "chat_messages" not in data:
                    data["chat_messages"] = []
                return data
        except Exception as e:
            st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
    return {"profiles": [], "chat_messages": [], "sns_posts": []}

def save_data():
    data = {
        "profiles": st.session_state.get("profiles", []),
        "chat_messages": GLOBAL_CHAT_STORE,
        "sns_posts": st.session_state.get("sns_posts", [])
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

initial_data = load_data()
if not GLOBAL_CHAT_STORE and initial_data.get("chat_messages"):
    GLOBAL_CHAT_STORE.extend(initial_data.get("chat_messages"))

# ==========================================
# 2. 이미지 Base64 변환 유틸리티 함수
# ==========================================
def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode()
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    return None

# ==========================================
# 3. 페이지 설정 및 Custom CSS
# ==========================================
st.set_page_config(page_title="통일 톡톡 (Tongil Talk)", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 10px;
    }
    
    .message-wrapper {
        display: flex;
        flex-direction: column;
        max-width: 70%;
    }
    
    .message-info {
        font-size: 11px;
        color: #666;
        margin-bottom: 3px;
    }
    
    .message-bubble {
        padding: 10px 14px;
        border-radius: 15px;
        font-size: 14px;
        line-height: 1.4;
        word-break: break-word;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.1);
    }
    
    .other-user {
        align-self: flex-start;
    }
    .other-user .message-info {
        text-align: left;
    }
    .other-user .message-bubble {
        background-color: #FFECEC;
        color: #5C1D1D;
        border-top-left-radius: 2px;
    }

    .my-user {
        align-self: flex-end;
    }
    .my-user .message-info {
        text-align: right;
    }
    .my-user .message-bubble {
        background-color: #E8F2FF;
        color: #1A365D;
        border-top-right-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)

if "profiles" not in st.session_state:
    st.session_state.profiles = initial_data.get("profiles", [])
if "page_step" not in st.session_state:
    st.session_state.page_step = "profile"
if "user_nickname" not in st.session_state:
    st.session_state.user_nickname = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "🇰🇷 남한 청년"
if "avatar_emoji" not in st.session_state:
    st.session_state.avatar_emoji = "🇰🇷"
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "chat"

if "sns_posts" not in st.session_state:
    st.session_state.sns_posts = initial_data.get("sns_posts", [])

if "confirm_clear_mode" not in st.session_state:
    st.session_state.confirm_clear_mode = False

# ==========================================
# 4. 실시간 카카오톡 스타일 채팅 함수
# ==========================================
def render_live_chat():
    c_col1, c_col2, c_col3, c_col4 = st.columns([2, 1, 1, 1])
    
    with c_col1:
        st.subheader("💬 실시간 소통 채팅방")
        st.caption("⚡ 메시지 작성 후 Enter를 누르면 상대방에게 즉시 전달됩니다.")
        
    with c_col2:
        if st.button("🔄 실시간 동기화", use_container_width=True):
            st.rerun()

    with c_col3:
        if st.button("⬅️ 뒤로가기", use_container_width=True):
            st.session_state.page_step = "menu"
            st.rerun()

    with c_col4:
        if not st.session_state.confirm_clear_mode:
            if st.button("🗑️ 초기화", use_container_width=True, disabled=len(GLOBAL_CHAT_STORE) == 0):
                st.session_state.confirm_clear_mode = True
                st.rerun()
        else:
            if st.button("🚨 정말 초기화?", type="primary", use_container_width=True):
                GLOBAL_CHAT_STORE.clear()
                save_data()
                st.session_state.confirm_clear_mode = False
                st.rerun()

    if st.session_state.confirm_clear_mode:
        warn_col1, warn_col2 = st.columns([3, 1])
        with warn_col1:
            st.warning("⚠️ 버튼을 한 번 더 누르면 대화 내역이 완전히 삭제됩니다!")
        with warn_col2:
            if st.button("취소", use_container_width=True):
                st.session_state.confirm_clear_mode = False
                st.rerun()
    else:
        st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")

    # 채팅 메시지 렌더링
    chat_box = st.container(height=420)
    with chat_box:
        if not GLOBAL_CHAT_STORE:
            st.caption("아직 대화 내역이 없습니다. 메시지를 입력해보세요!")
        else:
            current_user = st.session_state.user_nickname
            chat_html = '<div class="chat-container">'
            for msg in GLOBAL_CHAT_STORE:
                is_me = (msg["author"] == current_user)
                wrapper_class = "my-user" if is_me else "other-user"
                chat_html += (
                    f'<div class="message-wrapper {wrapper_class}">'
                    f'<div class="message-info">{msg["avatar"]} <b>{msg["author"]}</b> ({msg["role"]})</div>'
                    f'<div class="message-bubble">{msg["content"]}</div>'
                    f'</div>'
                )
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

    # 입력 폼
    if prompt := st.chat_input("메시지를 입력하세요..."):
        new_msg = {
            "avatar": st.session_state.avatar_emoji,
            "author": st.session_state.user_nickname,
            "role": st.session_state.user_role,
            "content": prompt
        }
        GLOBAL_CHAT_STORE.append(new_msg)
        save_data()
        st.rerun()

    # 경량화된 실시간 갱신 트리거 (타이핑 방해 최소화)
    st.components.v1.html(
        """
        <script>
            setTimeout(function() {
                const active = window.parent.document.activeElement;
                const isTyping = active && (active.tagName === 'TEXTAREA' || active.tagName === 'INPUT');
                if (!isTyping) {
                    window.parent.postMessage({type: 'streamlit:rerun'}, '*');
                }
            }, 1500);
        </script>
        """,
        height=0
    )

# ==========================================
# STEP 1: 프로필 선택 및 생성 화면
# ==========================================
if st.session
