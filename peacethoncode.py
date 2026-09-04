import streamlit as st
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="통일 톡톡 (Tongil Talk)", page_icon="🕊️", layout="centered")

# 세션 상태(Session State) 초기화
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "sns_posts" not in st.session_state:
    st.session_state.sns_posts = []

# 사이드바 UI 설정
st.sidebar.title("🕊️ 통일 톡톡")
st.sidebar.markdown("남북 청년들의 자유로운 소통 공간")

user_role = st.sidebar.radio(
    "어떤 프로필로 참여하시겠습니까?", 
    ["🇰🇷 남한 청년", "🇰🇵 북한 청년"]
)

avatar_emoji = "🇰🇷" if "남한" in user_role else "🇰🇵"

st.sidebar.divider()
menu = st.sidebar.radio("메뉴 이동", ["💬 실시간 소통 채팅창", "📝 일상 나눔 미니 SNS"])

# 1. 실시간 채팅창 화면
if menu == "💬 실시간 소통 채팅창":
    st.title("💬 남북 청년 소통 채팅방")
    st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")
    
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

# 2. 미니 SNS 게시판 화면
elif menu == "📝 일상 나눔 미니 SNS":
    st.title("📝 자유로운 일상 나눔")
    st.write("오늘 하루는 어땠나요? 소소한 일상부터 궁금했던 점까지 자유롭게 올려주세요.")
    
    with st.expander("✨ 새로운 게시글 작성하기", expanded=True):
        with st.form("new_post_form"):
            post_title = st.text_input("제목을 적어주세요")
            post_content = st.text_area("내용을 입력해주세요")
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
                    
    st.divider()
    
    if not st.session_state.sns_posts:
        st.info("아직 등록된 게시글이 없습니다. 첫 번째 글의 주인공이 되어보세요!")
    else:
        for idx, post in enumerate(st.session_state.sns_posts):
            st.markdown(f"**{post['title']}**")
            st.caption(f"{post['avatar']} {post['author']} | 🕒 {post['time']}")
            st.write(post['content'])
            st.markdown("---")