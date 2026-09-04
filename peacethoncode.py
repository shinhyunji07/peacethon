import streamlit as st
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="통일 톡톡 (Tongil Talk)", page_icon="🕊️", layout="wide")

# 세션 상태(Session State) 초기화
if "page_step" not in st.session_state:
    st.session_state.page_step = "profile"  # profile -> menu -> main (chat or sns)
if "user_nickname" not in st.session_state:
    st.session_state.user_nickname = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "🇰🇷 남한 청년"
if "avatar_emoji" not in st.session_state:
    st.session_state.avatar_emoji = "🇰🇷"
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "chat"  # 'chat' 또는 'sns'

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "sns_posts" not in st.session_state:
    st.session_state.sns_posts = []

# ==========================================
# STEP 1: 프로필 입력 화면
# ==========================================
if st.session_state.page_step == "profile":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("🕊️ 통일 톡톡")
        st.subheader("프로필을 설정해주세요")
        st.caption("남북 청년들의 자유로운 소통 공간에 오신 것을 환영합니다.")
        st.divider()

        nickname_input = st.text_input("사용할 닉네임을 입력하세요", value=st.session_state.user_nickname)
        role_input = st.radio("소속을 선택해주세요", ["🇰🇷 남한 청년", "🇰🇵 북한 청년"])

        if st.button("다음으로 이동 ➡️", use_container_width=True, type="primary"):
            if not nickname_input.strip():
                st.warning("닉네임을 입력해 주세요!")
            else:
                st.session_state.user_nickname = nickname_input
                st.session_state.user_role = role_input
                st.session_state.avatar_emoji = "🇰🇷" if "남한" in role_input else "🇰🇵"
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
        if st.button("⬅️ 프로필 수정하기", use_container_width=True):
            st.session_state.page_step = "profile"
            st.rerun()

# ==========================================
# STEP 3: 메인 화면 (채팅 or SNS 선택)
# ==========================================
elif st.session_state.page_step == "main":
    # 상단 헤더 및 메뉴 전환 버튼
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.title("🕊️ 통일 톡톡")
        st.caption(f"접속 프로필: {st.session_state.avatar_emoji} **{st.session_state.user_nickname}** ({st.session_state.user_role})")
    with top_col2:
        if st.button("🔄 메뉴 선택으로 이동"):
            st.session_state.page_step = "menu"
            st.rerun()

    st.divider()

    # 1. 채팅창 화면 선택 시
    if st.session_state.selected_menu == "chat":
        st.subheader("💬 실시간 소통 채팅방")
        st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")

        chat_box = st.container(height=450)
        with chat_box:
            if not st.session_state.chat_messages:
                st.caption("아직 대화 내역이 없습니다. 메시지를 입력해보세요!")
            for msg in st.session_state.chat_messages:
                with st.chat_message("user", avatar=msg["avatar"]):
                    st.markdown(f"**{msg['author']}** ({msg['role']})")
                    st.write(msg["content"])

        if prompt := st.chat_input("메시지를 입력하세요..."):
            st.session_state.chat_messages.append({
                "avatar": st.session_state.avatar_emoji,
                "author": st.session_state.user_nickname,
                "role": st.session_state.user_role,
                "content": prompt
            })
            st.rerun()

    # 2. SNS 게시판 화면 선택 시
    elif st.session_state.selected_menu == "sns":
        st.subheader("📝 자유로운 일상 나눔 SNS")

        with st.expander("✨ 새로운 게시글 작성하기", expanded=False):
            with st.form("new_post_form"):
                post_title = st.text_input("제목을 적어주세요")
                post_content = st.text_area("내용을 입력해주세요", height=100)
                submitted = st.form_submit_button("게시글 올리기")

                if submitted:
                    if post_title.strip() and post_content.strip():
                        st.session_state.sns_posts.insert(0, {
                            "author": st.session_state.user_nickname,
                            "role": st.session_state.user_role,
                            "avatar": st.session_state.avatar_emoji,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "title": post_title,
                            "content": post_content
                        })
                        st.success("게시글이 성공적으로 등록되었습니다!")
                        st.rerun()
                    else:
                        st.warning("제목과 내용을 모두 입력해주세요.")

        sns_box = st.container(height=450)
        with sns_box:
            if not st.session_state.sns_posts:
                st.info("아직 등록된 게시글이 없습니다. 첫 번째 글의 주인공이 되어보세요!")
            else:
                for post in st.session_state.sns_posts:
                    st.markdown(f"### {post['title']}")
                    st.caption(f"{post['avatar']} {post['author']} ({post['role']}) | 🕒 {post['time']}")
                    st.write(post['content'])
                    st.markdown("---")
