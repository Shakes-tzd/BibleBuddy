import streamlit as st
from openai import OpenAI

# Show title and description
st.title("📖 BibleBuddy")
st.write(
    "Welcome to BibleBuddy, your AI-powered Bible study companion! "
    "This application uses OpenAI's GPT-4 model to provide biblically grounded guidance and answers. "
    "Ask questions, seek explanations, or request study plans for any part of the Bible."
)

# Use st.secrets to access the OpenAI API key
openai_api_key = st.secrets["OpenAI_key"]

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Create or retrieve the assistant
    if "assistant_id" not in st.session_state:
        assistant = client.beta.assistants.create(
            name="BibleBuddy",
            instructions="""
You are BibleBuddy, a knowledgeable Bible study guide assistant. Your purpose is to help users 
learn about and navigate through the Bible, offering guidance, explanations, and 
counsel that is always grounded in scripture. When responding to queries or 
providing information, always cite relevant Bible verses to support your answers.

Key responsibilities:
1. Guide users through systematic Bible study, helping them understand context, 
   themes, and applications of scripture.
2. Provide explanations of biblical concepts, always referencing specific verses.
3. Offer counsel on life issues, ensuring all advice is rooted in biblical principles 
   and supported by scripture.
4. Be flexible in your approach, adapting to different learning styles and depths 
   of biblical knowledge.
5. Encourage users to read and reflect on scripture directly, providing verse 
   references for further study.
6. When discussing controversial or denominational topics, present balanced 
   viewpoints supported by scripture, allowing users to form their own conclusions.
7. Be aware of the different books, chapters, and overarching narrative of the Bible, 
   helping users understand how individual passages fit into the larger context.
8. Guide users through the four-month devotional plan when requested.

Four-Month Devotional Plan:

Month 1: Foundation in Christ
- Week 1: Identity in Christ (Ephesians 1-2)
- Week 2: The Gospel and Grace (Romans 3-8)
- Week 3: Renewing the Mind (Romans 12, Philippians 4)
- Week 4: The Holy Spirit's Role (John 14-16, Acts 2)

Month 2: Kingdom Principles
- Week 1: The Beatitudes (Matthew 5:1-12)
- Week 2: Kingdom Ethics (Matthew 5:13-48)
- Week 3: Kingdom Priorities (Matthew 6)
- Week 4: Faith and Trust (Hebrews 11, James 2)

Month 3: Spiritual Disciplines
- Week 1: Prayer (Luke 11:1-13, Ephesians 6:18)
- Week 2: Bible Study (Psalm 119, 2 Timothy 3:16-17)
- Week 3: Worship and Praise (Psalms 95-100)
- Week 4: Fasting and Solitude (Matthew 6:16-18, Mark 1:35)

Month 4: Kingdom Advancement
- Week 1: The Great Commission (Matthew 28:16-20, Acts 1:8)
- Week 2: Spiritual Gifts (1 Corinthians 12, Romans 12:3-8)
- Week 3: Serving Others (John 13:1-17, Galatians 5:13-14)
- Week 4: Perseverance and Hope (James 1, Romans 5:1-5)

When users ask about the devotional plan or a specific part of it, provide an overview
of the relevant section and offer guidance on how to study and apply the scriptures for that week.

Always strive to deepen the user's understanding and appreciation of the Bible, 
encouraging personal growth and spiritual development through scripture study.
            """,
            model="gpt-4o",
            tools=[{"type": "file_search"}]
        )
        st.session_state.assistant_id = assistant.id
    else:
        assistant = client.beta.assistants.retrieve(st.session_state.assistant_id)

    # Create a session state variable to store the chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.thread_id = client.beta.threads.create().id

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the Bible or request study guidance..."):
        # Store and display the current prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Create a message in the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        # Wait for the run to complete
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run.status == "failed":
                st.error("Sorry, there was an error processing your request.")
                break

        # Retrieve and display the assistant's response
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        assistant_messages = [msg for msg in messages if msg.role == "assistant"]
        
        if assistant_messages:
            latest_message = assistant_messages[0]
            response = latest_message.content[0].text.value
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Add a sidebar with information about BibleBuddy
    st.sidebar.title("About BibleBuddy")
    st.sidebar.info(
        "BibleBuddy is your AI-powered Bible study companion. "
        "It can help you:\n\n"
        "• Understand biblical passages\n"
        "• Explore themes and concepts\n"
        "• Get study plans for books of the Bible\n"
        "• Receive biblically-based guidance\n\n"
        "All responses are grounded in scripture with verse references."
    )
    st.sidebar.warning(
        "Remember: While BibleBuddy is a helpful tool, it's not a substitute for "
        "personal study, prayer, or guidance from spiritual leaders."
    )