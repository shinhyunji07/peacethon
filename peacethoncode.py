# ==========================================
# 5. 실시간 카카오톡 스타일 채팅 Fragment (0.5초 감지)
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
        if not st.session_state.confirm_clear_mode:
            if st.button("🗑️ 초기화", use_container_width=True, disabled=len(GLOBAL_CHAT_STORE) == 0):
                st.session_state.confirm_clear_mode = True
                st.rerun(scope="fragment")
        else:
            if st.button("🚨 정말 초기화?", type="primary", use_container_width=True):
                GLOBAL_CHAT_STORE.clear()
                save_data()
                st.session_state.confirm_clear_mode = False
                st.rerun(scope="fragment")

    if st.session_state.confirm_clear_mode:
        warn_col1, warn_col2 = st.columns([3, 1])
        with warn_col1:
            st.warning("⚠️ 버튼을 한 번 더 누르면 대화 내역이 완전히 삭제됩니다!")
        with warn_col2:
            if st.button("취소", use_container_width=True):
                st.session_state.confirm_clear_mode = False
                st.rerun(scope="fragment")
    else:
        st.info("서로를 존중하는 따뜻한 대화를 나누어 보세요.")

    chat_box = st.container(height=420)
    with chat_box:
        if not GLOBAL_CHAT_STORE:
            st.caption("아직 대화 내역이 없습니다. 메시지를 입력해보세요!")
        else:
            current_user = st.session_state.user_nickname
            
            # HTML 생성을 들여쓰기 없는 한 줄 형태로 조합
            chat_html = '<div class="chat-container">'
            for msg in GLOBAL_CHAT_STORE:
                is_me = (msg["author"] == current_user)
                wrapper_class = "my-user" if is_me else "other-user"
                
                # 공백/줄바꿈을 최소화하여 Streamlit이 코드 블록으로 파싱하는 것을 방지
                chat_html += (
                    f'<div class="message-wrapper {wrapper_class}">'
                    f'<div class="message-info">{msg["avatar"]} <b>{msg["author"]}</b> ({msg["role"]})</div>'
                    f'<div class="message-bubble">{msg["content"]}</div>'
                    f'</div>'
                )
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
