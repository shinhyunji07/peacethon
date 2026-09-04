import streamlit as st
import json
import os
import time
from datetime import datetime

# 데이터 저장 파일 경로 설정
DATA_FILE = "tongil_talk_data.json"

# ==========================================
# 1. 파일 데이터 로드 및 저장 함수
# ==========================================
def load_data():
    """로컬 JSON 파일에서 프로필, 채팅 및 게시글 데이터 로드"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "profiles" not in data:
                    data["profiles"] = []
                return data
        except Exception as e:
            st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
    return {"profiles": [], "chat_messages": [], "sns_posts": []}

def save_data():
    """현재 세션 상태의 데이터를 로컬 JSON 파일에 저장"""
    data = {
        "profiles": st.session_state.profiles,
        "chat_messages": st.session_state.chat_messages,
        "sns_posts": st.session_state.sns_posts
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

# ==========================================
# 2. 페이지 설정 및 세션 상태(Session State) 초기화
# ==========================================
st.set_page_config(page_title="통일 톡톡 (Tongil Talk)", page_icon="🕊️", layout="wide")

# 저장된 파일 데이터 가져오기
initial_data = load_data()

if "profiles" not in st.session_state:
    st.session_state.profiles = initial_data.get("profiles", [])
if "page_step" not in st.session_state:
    st.session_state.page_step = "profile"  # profile -> menu -> main
if "user_nickname" not in st.session_state:
    st.session_state.user_nickname = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "🇰🇷 남한 청년"
if "avatar_emoji" not in st.session_state:
    st.session_state.avatar_emoji = "🇰🇷"
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "chat"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = initial_data.get("chat_messages", [])
if "sns_posts" not in st.session_state:
    st.session_state.sns_posts = initial_data.get("sns_posts", [])

# ==========================================
# 3. 삭제 확인 모달 팝업 Dialog 정의
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
    st.caption("이 작업은 되돌릴 수 없으며, 저장된 모든 대화 내역이 로컬 파일에서도 함께 삭제됩니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("네, 모두 삭제합니다", type="primary", use_container_width=True):
            st.session_state.chat_messages = []
            save_data()
            st.rerun()
    with col2:
        if st.button("취소", use_container_width=True):
            st.rerun()

# ==========================================
# 4. 실시간 독립 채팅용 Fragment 함수 (자동/수동 새로고침 적용)
# ==========================================
@st.fragment(run_every=2)
def render_live_chat():
    """페이지 전체를 새로고침하지 않고 채팅 영역만 2초 간격으로 로컬 파일과 동기화"""
    # 파일에서 최신 채팅 내역을 불러와 세션 업데이트
    latest_data = load_data()
    st.session_state.chat_messages = latest_data.get("chat_messages", [])

    # 상단 제어 바 (새로고침, 뒤로가기, 초기화 버튼)
    c_col1, c_col2, c_col3, c_col4 = st.columns([2, 1, 1, 1])
    
    with c_col1:
        st.subheader("💬 실시간 소통 채팅방")
        st.caption("⚡ 2초마다 다른 사용자의 메시지가 자동 반영됩니다.")
        
    with c_col2:
        if st.button("🔄 대화 새로고침", use_container_width=True):
            st.rerun(scope="fragment")

    with c_col3:
        if st.button("⬅️ 뒤로가기", use_container_width=True):
            st.session_state.page_step = "menu"
            st.rerun()

    with c_col4:
        if st.session_state.chat_messages:
            if st.button("🗑️ 초기화", use_container_width=True):
                confirm_clear_chat()

    st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")

    # 채팅 메시지 출력 박스
    chat_box = st.container(height=420)
    with chat_box:
        if not st.session_state.chat_messages:
            st.caption("아직 대화 내역이 없습니다. 메시지를 입력해보세요!")
        for msg in st.session_state.chat_messages:
            with st.chat_message("user", avatar=msg["avatar"]):
                st.markdown(f"**{msg['author']}** ({msg['role']})")
                st.write(msg["content"])

    # 메시지 입력 창
    if prompt := st.chat_input("메시지를 입력하세요..."):
        new_msg = {
            "avatar": st.session_state.avatar_emoji,
            "author": st.session_state.user_nickname,
            "role": st.session_state.user_role,
            "content": prompt
        }
        st.session_state.chat_messages.append(new_msg)
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
            st.markdown("### 👤 기존 프로필 선택")
            selected_profile_str = st.selectbox(
                "이미 생성된 프로필 중 선택하세요", 
                options=profile_options
            )
            
            selected_idx = profile_options.index(selected_profile_str)
            selected_profile = st.session_state.profiles[selected_idx]

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                if st.button("선택한 프로필로 입장하기 ➡️", use_container_width=True, type="primary"):
                    st.session_state.user_nickname = selected_profile["nickname"]
                    st.session_state.user_role = selected_profile["role"]
                    st.session_state.avatar_emoji = selected_profile["avatar"]
                    st.session_state.page_step = "menu"
                    st.rerun()

            with btn_col2:
                if st.button("🗑️ 프로필 삭제", use_container_width=True):
                    confirm_delete_profile(selected_idx, selected_profile_str)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()

        st.markdown("### ✨ 새 프로필 생성")
        nickname_input = st.text_input("새로 사용할 닉네임을 입력하세요", value="")
        role_input = st.radio("소속을 선택해주세요", ["🇰🇷 남한 청년", "🇰🇵 북한 청년"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("새 프로필로 생성 및 입장 ➡️", use_container_width=True):
            clean_nickname = nickname_input.strip()
            
            if not clean_nickname:
                st.warning("닉네임을 입력해 주세요!")
            else:
                existing_nicknames = [p["nickname"].lower() for p in st.session_state.profiles]
                
                if clean_nickname.lower() in existing_nicknames:
                    st.error(f"이미 존재하는 닉네임('{clean_nickname}')입니다. 다른 닉네임을 사용하거나 위에서 프로필을 선택해 주세요.")
                else:
                    avatar = "🇰🇷" if "남한" in role_input else "🇰🇵"
                    new_profile = {
                        "nickname": clean_nickname,
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
            if st.button("📝 자유 게시판 (SNS)\n\n일상 정보와 생각 공유하기", use_container_width=True):
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
        other_menu_label = "📝 자유 게시판으로" if st.session_state.selected_menu == "chat" else "💬 실시간 채팅으로"
        if st.button(f"🔄 {other_menu_label}", use_container_width=True):
            st.session_state.selected_menu = other_menu
            st.rerun()

    with nav_col3:
        if st.button("⬅️ 뒤로가기 (메뉴 선택)", use_container_width=True):
            st.session_state.page_step = "menu"
            st.rerun()

    st.divider()

    # 1. 채팅창 화면 (Fragment 기반 실시간 채팅 실행)
    if st.session_state.selected_menu == "chat":
        render_live_chat()

    # 2. SNS 게시판 화면
    elif st.session_state.selected_menu == "sns":
        st.subheader("📝 자유로운 일상 나눔 SNS")

        with st.expander("✨ 새로운 게시글 작성하기", expanded=False):
            with st.form("new_post_form"):
                post_title = st.text_input("제목을 적어주세요")
                post_content = st.text_area("내용을 입력해주세요", height=100)
                submitted = st.form_submit_button("게시글 올리기")

                if submitted:
                    if post_title.strip() and post_content.strip():
                        new_post = {
                            "author": st.session_state.user_nickname,
                            "role": st.session_state.user_role,
                            "avatar": st.session_state.avatar_emoji,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "title": post_title,
                            "content": post_content
                        }
                        st.session_state.sns_posts.insert(0, new_post)
                        save_data()
                        st.success("게시글이 성공적으로 등록되었습니다!")
                        st.rerun()
                    else:
                        st.warning("제목과 내용을 모두 입력해주세요.")

        sns_box = st.container(height=450)
        with sns_box:
            # SNS 목록 최신화
            latest_data = load_data()
            st.session_state.sns_posts = latest_data.get("sns_posts", [])
            
            if not st.session_state.sns_posts:
                st.info("아직 등록된 게시글이 없습니다. 첫 번째 글의 주인공이 되어보세요!")
            else:
                for post in st.session_state.sns_posts:
                    st.markdown(f"### {post['title']}")
                    st.caption(f"{post['avatar']} {post['author']} ({post['role']}) | 🕒 {post['time']}")
                    st.write(post['content'])
                    st.markdown("---")
