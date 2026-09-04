import streamlit as st
import json
import os
import base64
from datetime import datetime

# 데이터 저장 파일 경로 설정
DATA_FILE = "tongil_talk_data.json"

# ==========================================
# 1. 메모리 기반 초고속 글로벌 메시지 버퍼
# ==========================================
@st.cache_resource
def get_global_chat_store():
    return []

GLOBAL_CHAT_STORE = get_global_chat_store()

# ==========================================
# 2. 파일 데이터 로드 및 저장 함수
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
# 3. 이미지 Base64 및 뱃지 유틸리티 함수
# ==========================================
def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode()
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    return None

def get_flag_badge(role):
    if "남한" in role:
        return '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f1f0-1f1f7.svg" style="width:16px; height:16px; vertical-align:-2px; margin-right:3px;">'
    else:
        return '<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f1f0-1f1f5.svg" style="width:16px; height:16px; vertical-align:-2px; margin-right:3px;">'

# ==========================================
# 4. 페이지 설정 및 UI CSS
# ==========================================
st.set_page_config(page_title="PUAC IT-DA(잇다)", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
    /* 타이틀 강조 전용 스타일 */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .brand-subtitle {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }

    /* 채팅 스타일 */
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
        font-size: 12px;
        color: #555;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .message-bubble {
        padding: 10px 14px;
        border-radius: 15px;
        font-size: 14px;
        line-height: 1.4;
        word-break: break-word;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.04);
    }
    
    .other-user {
        align-self: flex-start;
    }
    .other-user .message-info {
        text-align: left;
        justify-content: flex-start;
    }
    .other-user .message-bubble {
        background-color: #FFF5F5;
        color: #611313;
        border-top-left-radius: 2px;
        border: 1px solid #FFD6D6;
    }

    .my-user {
        align-self: flex-end;
    }
    .my-user .message-info {
        text-align: right;
        justify-content: flex-end;
    }
    .my-user .message-bubble {
        background-color: #F0F7FF;
        color: #0F2D59;
        border-top-right-radius: 2px;
        border: 1px solid #D6E8FF;
    }
    
    div[data-testid="stExpander"], div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px;
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
# 5. 실시간 채팅 내역 프래그먼트
# ==========================================
@st.fragment(run_every=1)
def render_chat_messages():
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
                flag_img = get_flag_badge(msg.get("role", ""))
                
                chat_html += (
                    f'<div class="message-wrapper {wrapper_class}">'
                    f'<div class="message-info">{flag_img} <b>{msg["author"]}</b> <span style="font-size:11px; color:#777;">({msg["role"]})</span></div>'
                    f'<div class="message-bubble">{msg["content"]}</div>'
                    f'</div>'
                )
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

# ==========================================
# 6. 메인 채팅 레이아웃 함수
# ==========================================
def render_live_chat():
    c_col1, c_col2, c_col3, c_col4 = st.columns([2, 1, 1, 1])
    
    with c_col1:
        st.subheader("💬 실시간 소통 라운지")
        st.caption("⚡ 전체 화면 깜빡임 없이 1초마다 실시간 대화가 동기화됩니다.")
        
    with c_col2:
        if st.button("🔄 수동 동기화", use_container_width=True):
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

    render_chat_messages()

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

# ==========================================
# STEP 1: 프로필 선택 및 생성 화면
# ==========================================
if st.session_state.page_step == "profile":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="brand-title">🕊️ PUAC IT-DA(잇다)</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">남북 청년의 마음과 내일을 이어가는 소통 플랫폼</div>', unsafe_allow_html=True)
        
        st.subheader("프로필을 선택하거나 생성해주세요")
        st.divider()

        profile_options = [f"[{p['role'].split()[0]}] {p['nickname']} ({p['role']})" for p in st.session_state.profiles]
        
        if profile_options:
            st.markdown("### 👤 기존 프로필 접속")
            selected_profile_str = st.selectbox(
                "이미 생성된 프로필 중 선택하세요", 
                options=profile_options
            )
            
            selected_idx = profile_options.index(selected_profile_str)
            selected_profile = st.session_state.profiles[selected_idx]

            login_pw_input = st.text_input("비밀번호를 입력하세요", type="password", key="login_pw")

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                if st.button("선택한 프로필로 입장하기 ➡️", use_container_width=True, type="primary"):
                    saved_pw = selected_profile.get("password", "")
                    if saved_pw and login_pw_input != saved_pw:
                        st.error("비밀번호가 올바르지 않습니다.")
                    else:
                        st.session_state.user_nickname = selected_profile["nickname"]
                        st.session_state.user_role = selected_profile["role"]
                        st.session_state.avatar_emoji = selected_profile["avatar"]
                        st.session_state.page_step = "menu"
                        st.rerun()

            with btn_col2:
                if st.button("🗑️ 프로필 삭제", use_container_width=True):
                    saved_pw = selected_profile.get("password", "")
                    if saved_pw and login_pw_input != saved_pw:
                        st.error("비밀번호가 올바르지 않아 삭제할 수 없습니다.")
                    else:
                        del st.session_state.profiles[selected_idx]
                        save_data()
                        st.success("프로필이 삭제되었습니다.")
                        st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()

        st.markdown("### ✨ 새 프로필 생성")
        nickname_input = st.text_input("새로 사용할 닉네임을 입력하세요", value="", key="new_nickname")
        password_input = st.text_input("비밀번호를 설정하세요", type="password", key="new_pw")
        role_input = st.radio("소속을 선택해주세요", ["🇰🇷 남한 청년", "🇰🇵 북한 청년"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("새 프로필로 생성 및 입장 ➡️", use_container_width=True):
            clean_nickname = nickname_input.strip()
            clean_pw = password_input.strip()
            
            if not clean_nickname:
                st.warning("닉네임을 입력해 주세요!")
            elif not clean_pw:
                st.warning("비밀번호를 입력해 주세요!")
            else:
                existing_nicknames = [p["nickname"].lower() for p in st.session_state.profiles]
                
                if clean_nickname.lower() in existing_nicknames:
                    st.error(f"이미 존재하는 닉네임('{clean_nickname}')입니다. 다른 닉네임을 사용해 주세요.")
                else:
                    avatar = "🇰🇷" if "남한" in role_input else "🇰🇵"
                    new_profile = {
                        "nickname": clean_nickname,
                        "password": clean_pw,
                        "role": role_input,
                        "avatar": avatar
                    }
                    
                    st.session_state.profiles.append(new_profile)
                    save_data()
                    
                    st.session_state.user_nickname = clean_nickname
                    st.session_state.user_role = role_input
                    st.session_state.avatar_emoji = avatar
                    st.session_state.page_step = "menu"
                    st.rerun()

# ==========================================
# STEP 2: 메뉴 선택 화면
# ==========================================
elif st.session_state.page_step == "menu":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        flag_img = get_flag_badge(st.session_state.user_role)
        st.markdown('<div class="brand-title">🕊️ PUAC IT-DA(잇다)</div>', unsafe_allow_html=True)
        st.markdown(f"### 반갑습니다, {flag_img} **{st.session_state.user_nickname}**님!", unsafe_allow_html=True)
        st.write("원하시는 활동을 선택해주세요.")
        st.divider()

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("💬 실시간 라운지\n\n자유로운 실시간 대화 나누기", use_container_width=True, type="primary"):
                st.session_state.selected_menu = "chat"
                st.session_state.page_step = "main"
                st.rerun()

        with btn_col2:
            if st.button("📸 일상 스토리 (SNS)\n\n사진 및 스토리 공유하기", use_container_width=True):
                st.session_state.selected_menu = "sns"
                st.session_state.page_step = "main"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ 뒤로가기 (프로필 변경)", use_container_width=True):
            st.session_state.page_step = "profile"
            st.rerun()

# ==========================================
# STEP 3: 메인 화면 (채팅 or SNS 선택)
# ==========================================
elif st.session_state.page_step == "main":
    nav_col1, nav_col2, nav_col3 = st.columns([2, 1, 1])
    
    flag_img = get_flag_badge(st.session_state.user_role)
    with nav_col1:
        st.markdown('<h3 style="margin:0; padding:0;">🕊️ PUAC IT-DA(잇다)</h3>', unsafe_allow_html=True)
        st.markdown(f"접속 프로필: {flag_img} **{st.session_state.user_nickname}** ({st.session_state.user_role})", unsafe_allow_html=True)
    
    with nav_col2:
        other_menu = "sns" if st.session_state.selected_menu == "chat" else "chat"
        other_menu_label = "📸 일상 스토리로" if st.session_state.selected_menu == "chat" else "💬 실시간 라운지로"
        if st.button(f"🔄 {other_menu_label}", use_container_width=True):
            st.session_state.selected_menu = other_menu
            st.rerun()

    with nav_col3:
        if st.button("⬅️ 뒤로가기 (메뉴 선택)", use_container_width=True):
            st.session_state.page_step = "menu"
            st.rerun()

    st.divider()

    # 1. 채팅창 화면
    if st.session_state.selected_menu == "chat":
        render_live_chat()

    # 2. SNS 피드 화면
    elif st.session_state.selected_menu == "sns":
        st.subheader("📸 일상 스토리 (SNS)")

        with st.expander("✨ 새 피드 작성하기 (사진 첨부)", expanded=False):
            post_content = st.text_area("내용을 입력해주세요", height=90, key="post_content_input")
            uploaded_img = st.file_uploader("사진을 올려보세요 (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

            if st.button("게시하기 🚀", type="primary"):
                if post_content.strip() or uploaded_img is not None:
                    img_b64 = image_to_base64(uploaded_img)
                    new_post = {
                        "id": int(datetime.now().timestamp() * 1000),
                        "author": st.session_state.user_nickname,
                        "role": st.session_state.user_role,
                        "avatar": st.session_state.avatar_emoji,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "content": post_content,
                        "image": img_b64,
                        "likes": [],
                        "comments": []
                    }
                    st.session_state.sns_posts.insert(0, new_post)
                    save_data()
                    st.success("피드가 등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("내용이나 사진 중 하나는 작성해 주세요.")

        latest_data = load_data()
        st.session_state.sns_posts = latest_data.get("sns_posts", [])

        if not st.session_state.sns_posts:
            st.info("아직 등록된 피드가 없습니다. 첫 사진의 주인공이 되어보세요!")
        else:
            current_user = st.session_state.user_nickname

            for idx, post in enumerate(st.session_state.sns_posts):
                if "likes" not in post:
                    post["likes"] = []
                if "comments" not in post:
                    post["comments"] = []

                post_flag = get_flag_badge(post.get("role", ""))
                st.markdown(f"#### {post_flag} **{post['author']}** <span style='font-size:12px; color:gray;'>({post['role']} · {post['time']})</span>", unsafe_allow_html=True)

                if post.get("image"):
                    st.image(post["image"], use_container_width=True)

                if post.get("content"):
                    st.write(post["content"])

                like_count = len(post["likes"])
                has_liked = current_user in post["likes"]

                col_like, col_comment_count = st.columns([1, 4])
                
                with col_like:
                    like_btn_label = f"❤️ {like_count}" if has_liked else f"🤍 {like_count}"
                    if st.button(like_btn_label, key=f"like_{post.get('id', idx)}"):
                        if has_liked:
                            post["likes"].remove(current_user)
                        else:
                            post["likes"].append(current_user)
                        save_data()
                        st.rerun()

                with st.expander(f"💬 댓글 {len(post['comments'])}개 보기 / 달기"):
                    for c in post["comments"]:
                        c_flag = get_flag_badge(c.get("role", st.session_state.user_role))
                        st.markdown(f"**{c_flag} {c['author']}**: {c['content']} <span style='font-size:10px; color:gray;'>({c['time']})</span>", unsafe_allow_html=True)

                    with st.form(key=f"comment_form_{post.get('id', idx)}"):
                        comment_text = st.text_input("댓글을 남겨보세요...", key=f"c_in_{post.get('id', idx)}")
                        c_submit = st.form_submit_button("댓글 작성")
                        
                        if c_submit and comment_text.strip():
                            new_comment = {
                                "author": st.session_state.user_nickname,
                                "avatar": st.session_state.avatar_emoji,
                                "role": st.session_state.user_role,
                                "content": comment_text.strip(),
                                "time": datetime.now().strftime("%m/%d %H:%M")
                            }
                            post["comments"].append(new_comment)
                            save_data()
                            st.rerun()

                st.markdown("---")
