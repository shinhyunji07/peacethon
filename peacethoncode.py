import streamlit as st
import json
import os
import base64
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
        "profiles": st.session_state.profiles,
        "chat_messages": GLOBAL_CHAT_STORE,
        "sns_posts": st.session_state.sns_posts
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
# 3. 페이지 설정 및 Custom CSS (카카오톡 스타일 버블)
# ==========================================
st.set_page_config(page_title="통일 톡톡 (Tongil Talk)", page_icon="🕊️", layout="wide")

# 카카오톡 스타일 말풍선 디자인 적용
st.markdown("""
<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 10px;
    }
    
    /* 공통 말풍선 스타일 */
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
    
    /* 상대방 메시지 (왼쪽 정렬, 파스텔 빨강/분홍) */
    .other-user {
        align-self: flex-start;
    }
    .other-user .message-info {
        text-align: left;
    }
    .other-user .message-bubble {
        background-color: #FFECEC; /* 파스텔 레드/핑 */
        color: #5C1D1D;
        border-top-left-radius: 2px;
    }

    /* 내 메시지 (오른쪽 정렬, 파스텔 파랑) */
    .my-user {
        align-self: flex-end;
    }
    .my-user .message-info {
        text-align: right;
    }
    .my-user .message-bubble {
        background-color: #E8F2FF; /* 파스텔 블루 */
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

# ==========================================
# 4. 삭제 확인 모달 팝업 Dialog 정의
# ==========================================
@st.dialog("⚠️ 프로필 삭제")
def confirm_delete_profile(profile_idx, profile_name):
    st.write(f"정말로 **'{profile_name}'** 프로필을 삭제하시겠습니까?")
    st.caption("이 작업은 되돌릴 수 없으며, 로컬 저장 파일에서도 함께 삭제됩니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("네, 삭제합니다", type="primary", use_container_width=True):
            del st.session_state.profiles[profile_idx]
            save_data()
            st.success("프로필이 삭제되었습니다.")
            st.rerun()
    with col2:
        if st.button("취소", use_container_width=True):
            st.rerun()

@st.dialog("⚠️ 대화방 전체 초기화")
def confirm_clear_chat():
    st.write("정말로 대화방의 모든 메시지를 삭제하시겠습니까?")
    st.caption("이 작업은 되돌릴 수 없으며, 저장된 모든 대화 내역이 제거됩니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("네, 모두 삭제합니다", type="primary", use_container_width=True):
            GLOBAL_CHAT_STORE.clear()
            save_data()
            st.rerun()
    with col2:
        if st.button("취소", use_container_width=True):
            st.rerun()

# ==========================================
# 5. 초고속 실시간 카카오톡 스타일 채팅 Fragment (0.5초 감지)
# ==========================================
@st.fragment(run_every=0.5)
def render_live_chat():
    c_col1, c_col2, c_col3, c_col4 = st.columns([2, 1, 1, 1])
    
    with c_col1:
        st.subheader("💬 실시간 소통 채팅방")
        st.caption("⚡ 카카오톡 스타일의 좌/우 실시간 채팅창입니다.")
        
    with c_col2:
        if st.button("🔄 대화 새로고침", use_container_width=True):
            st.rerun(scope="fragment")

    with c_col3:
        if st.button("⬅️ 뒤로가기", use_container_width=True):
            st.session_state.page_step = "menu"
            st.rerun()

    with c_col4:
        if GLOBAL_CHAT_STORE:
            if st.button("🗑️ 초기화", use_container_width=True):
                confirm_clear_chat()

    st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")

    # 카카오톡 스타일 채팅 박스
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
                
                chat_html += f'''
                <div class="message-wrapper {wrapper_class}">
                    <div class="message-info">{msg['avatar']} <b>{msg['author']}</b> ({msg['role']})</div>
                    <div class="message-bubble">{msg['content']}</div>
                </div>
                '''
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

    if prompt := st.chat_input("메시지를 입력하세요..."):
        new_msg = {
            "avatar": st.session_state.avatar_emoji,
            "author": st.session_state.user_nickname,
            "role": st.session_state.user_role,
            "content": prompt
        }
        GLOBAL_CHAT_STORE.append(new_msg)
        save_data()
        st.rerun(scope="fragment")

# ==========================================
# STEP 1: 프로필 선택 및 생성 화면
# ==========================================
if st.session_state.page_step == "profile":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("🕊️ 통일 톡톡")
        st.subheader("프로필을 선택하거나 생성해주세요")
        st.caption("남북 청년들의 자유로운 소통 공간에 오신 것을 환영합니다.")
        st.divider()

        profile_options = [f"{p['avatar']} {p['nickname']} ({p['role']})" for p in st.session_state.profiles]
        
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
                        confirm_delete_profile(selected_idx, selected_profile_str)
                
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
        st.title("🕊️ 통일 톡톡")
        st.subheader(f"반갑습니다, {st.session_state.avatar_emoji} {st.session_state.user_nickname}님!")
        st.write("원하시는 활동을 선택해주세요.")
        st.divider()

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("💬 실시간 채팅방\n\n자유로운 실시간 대화 나누기", use_container_width=True, type="primary"):
                st.session_state.selected_menu = "chat"
                st.session_state.page_step = "main"
                st.rerun()

        with btn_col2:
            if st.button("📸 인스타 스타일 SNS\n\n사진 및 일상 공유하기", use_container_width=True):
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
    
    with nav_col1:
        st.title("🕊️ 통일 톡톡")
        st.caption(f"접속 프로필: {st.session_state.avatar_emoji} **{st.session_state.user_nickname}** ({st.session_state.user_role})")
    
    with nav_col2:
        other_menu = "sns" if st.session_state.selected_menu == "chat" else "chat"
        other_menu_label = "📸 SNS 피드로" if st.session_state.selected_menu == "chat" else "💬 실시간 채팅으로"
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
        st.subheader("📸 일상 피드 (SNS)")

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

                st.markdown(f"#### {post['avatar']} **{post['author']}** <span style='font-size:12px; color:gray;'>({post['role']} · {post['time']})</span>", unsafe_allow_html=True)

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
                        st.markdown(f"**{c['avatar']} {c['author']}**: {c['content']} <span style='font-size:10px; color:gray;'>({c['time']})</span>", unsafe_allow_html=True)

                    with st.form(key=f"comment_form_{post.get('id', idx)}"):
                        comment_text = st.text_input("댓글을 남겨보세요...", key=f"c_in_{post.get('id', idx)}")
                        c_submit = st.form_submit_button("댓글 작성")
                        
                        if c_submit and comment_text.strip():
                            new_comment = {
                                "author": st.session_state.user_nickname,
                                "avatar": st.session_state.avatar_emoji,
                                "content": comment_text.strip(),
                                "time": datetime.now().strftime("%m/%d %H:%M")
                            }
                            post["comments"].append(new_comment)
                            save_data()
                            st.rerun()

                st.markdown("---")
