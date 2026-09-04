import streamlit as st
from datetime import datetime

# 페이지 기본 설정 (2분할 화면을 위해 layout="wide"로 변경)
st.set_page_config(page_title="통일 톡톡 (Tongil Talk)", page_icon="🕊️", layout="wide")

# 세션 상태(Session State) 초기화
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "sns_posts" not in st.session_state:
    st.session_state.sns_posts = []

# 사이드바 UI 설정 (프로필 선택)
st.sidebar.title("🕊️ 통일 톡톡")
st.sidebar.markdown("남북 청년들의 자유로운 소통 공간")

user_role = st.sidebar.radio(
    "어떤 프로필로 참여하시겠습니까?", 
    ["🇰🇷 남한 청년", "🇰🇵 북한 청년"]
)

avatar_emoji = "🇰🇷" if "남한" in user_role else "🇰🇵"

# 메인 헤더
st.title("🕊️ 통일 톡톡: 남북 청년 소통 공간")
st.caption("실시간 대화와 일상 나눔을 한눈에 확인해보세요.")
st.divider()

# 메인 화면 중앙 2분할 레이아웃
left_col, right_col = st.columns([1, 1], gap="medium")

# 1. 왼쪽 영역: 실시간 채팅창
with left_col:
    st.subheader("💬 실시간 소통 채팅방")
    st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")
    
    # 채팅 스크롤 영역
    chat_box = st.container(height=450)
    with chat_box:
        if not st.session_state.chat_messages:
            st.caption("아직 대화 내역이 없습니다. 메시지를 입력해보세요!")
        for msg in st.session_state.chat_messages:
            with st.chat_message("user", avatar=msg["avatar"]):
                st.markdown(f"**{msg['author']}**")
                st.write(msg["content"])
                
    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.chat_messages.append({
            "avatar": avatar_emoji,
            "author": user_role,
            "content": prompt
        })
        st.rerun()

# 2. 오른쪽 영역: 미니 SNS 게시판
with right_col:
    st.subheader("📝 자유로운 일상 나눔 SNS")
    
    with st.expander("✨ 새로운 게시글 작성하기", expanded=False):
        with st.form("new_post_form"):
            post_title = st.text_input("제목을 적어주세요")
            post_content = st.text_area("내용을 입력해주세요", height=100)
            submitted = st.form_submit_button("게시글 올리기")
            
            if submitted:
                if post_title.strip() and post_content.strip():
                    st.session_state.sns_posts.insert(0, {
                        "author": user_role,
                        "avatar": avatar_emoji,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "title": post_title,
                        "content": post_content
                    })
                    st.success("게시글이 성공적으로 등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("제목과 내용을 모두 입력해주세요.")
                    
    # 게시글 스크롤 영역
    sns_box = st.container(height=450)
    with sns_box:
        if not st.session_state.sns_posts:
            st.info("아직 등록된 게시글이 없습니다. 첫 번째 글의 주인공이 되어보세요!")
        else:
            for idx, post in enumerate(st.session_state.sns_posts):
                st.markdown(f"### {post['title']}")
                st.caption(f"{post['avatar']} {post['author']} | 🕒 {post['time']}")
                st.write(post['content'])
                st.markdown("---")
