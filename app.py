import streamlit as st
from gtts import gTTS
import tempfile
import time
import openai

class BloggingGeniusApp:
    def __init__(self):
        st.set_page_config(
            page_title="Blogging Genius",
            page_icon='🧑‍🏫',
            layout='centered',
            initial_sidebar_state='collapsed'
        )
        
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except KeyError:
            st.error("❌ OPENAI_API_KEY not found in Streamlit secrets. Please add it there.")
            st.stop()
        
        openai.api_key = api_key  # Set global OpenAI API key

        self.language_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de"
        }

    def get_openai_response(self, input_text, no_words, seo_words, language):
        template = f"""
Write a well-structured blog about "{input_text}" in {language}.

- The blog must be written entirely in {language}.  
- The blog should be approximately {no_words} words.  
- Emphasize the following SEO keywords: {seo_words}.  
- Use proper headings, bullet points, and paragraphs.  
- Ensure a natural conclusion that wraps up the topic properly.  
- The final paragraph should summarize the blog and leave the reader with key takeaways.  
- Do not stop mid-sentence. Ensure the response ends at a logical point.
"""

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": template}
            ],
            max_tokens=int(no_words) * 4,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def generate_summary(self, blog_content, language):
        summary_prompt = f"Summarize the following blog in {language} in 2-3 sentences:\n\n{blog_content}"

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=150,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def generate_audio(self, text, language):
        if language not in self.language_map:
            st.error(f"❌ Audio generation is not available for {language}. Please select English, Spanish, French, or German.")
            return None

        tts = gTTS(text, lang=self.language_map[language])
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio_file.name)
        return temp_audio_file.name

    def get_seo_keywords(self, input_text):
        return [f"Best {input_text} tips", f"How to improve {input_text}", f"Why {input_text} matters"]

    def display_ui(self):
        hour = time.localtime().tm_hour
        greeting = (
            "Good Morning, Genius!" if hour < 12 else
            "Good Afternoon, Genius!" if hour < 18 else
            "Good Evening, Genius!"
        )
        st.markdown(f"<h1 style='color:#34b7f1;'>{greeting} Welcome to Blogging Genius ✨</h1>", unsafe_allow_html=True)

        input_text = st.text_input("🌟 Enter the Blog Topic", placeholder="E.g., Argentina's Wildlife")
        col1, col2 = st.columns([5, 5])
        with col1:
            no_words = st.number_input('📝 Number of Words', min_value=50, max_value=1000, step=50, value=200)
        with col2:
            seo_words = st.text_input('🔑 SEO Keywords (comma separated)', placeholder="E.g., wildlife, Argentina, nature")

        language = st.selectbox("🌍 Choose Language", ["English", "Spanish", "French", "German"])
        show_outline = st.checkbox("Show Blog Outline")
        submit = st.button("Generate Blog ✨", use_container_width=True)

        return input_text, no_words, seo_words, language, submit, show_outline

    def run(self):
        st.markdown("""
        <style>
        body { background-color: #f0f0f5; font-family: 'Arial', sans-serif; }
        h1 { color: #34b7f1; font-size: 3em; font-weight: bold; text-align: center; }
        .stButton>button {
            background-color: #34b7f1; color: white; border-radius: 8px; font-weight: bold; padding: 10px; width: 100%;
        }
        .stButton>button:hover { background-color: #1f8cba; }
        .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>select {
            background-color: #f2f2f2; border-radius: 5px; padding: 10px; font-size: 1em;
        }
        .stProgress>div>div { background-color: #34b7f1; }
        </style>
        """, unsafe_allow_html=True)

        input_text, no_words, seo_words, language, submit, show_outline = self.display_ui()

        st.sidebar.subheader("💡 SEO Suggestions")
        seo_suggestions = self.get_seo_keywords(input_text)
        st.sidebar.write(seo_suggestions)

        if show_outline and input_text and seo_words:
            seo_list = [k.strip() for k in seo_words.split(',')] if seo_words else []
            outline = f""" 
- **Introduction:** Overview of {input_text}
- **Main Sections:**
"""
            for i, keyword in enumerate(seo_list[:3], start=1):
                outline += f"    - Section {i}: Explanation of {keyword}\n"
            outline += "- **Conclusion:** Wrapping up the blog and summarizing key points."
            st.write(outline)

        if submit:
            if not input_text.strip():
                st.error("Please enter a blog topic.")
                return
            if not seo_words.strip():
                st.warning("You didn't provide SEO keywords, the blog may be less effective.")
            with st.spinner("Generating your blog..."):
                blog_content = self.get_openai_response(input_text, no_words, seo_words, language)

                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time.sleep(0.01)

            st.subheader("📝 Generated Blog:")
            st.markdown(blog_content)

            summary = self.generate_summary(blog_content, language)
            st.subheader(f"🔍 Blog Summary in {language}:")
            st.markdown(summary)

            audio_file = self.generate_audio(blog_content, language)
            if audio_file:
                st.audio(audio_file, format="audio/mp3", start_time=0.0)

            st.download_button(
                label="📥 Download as TXT",
                data=blog_content,
                file_name="generated_blog.txt",
                mime="text/plain"
            )

            variation = st.radio("Generate another version?", options=["No", "Yes"])
            if variation == "Yes":
                new_blog_content = self.get_openai_response(input_text, no_words, seo_words, language)
                st.write(new_blog_content)

        st.markdown("""
        <style>
        .floating-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #34b7f1;
            color: white;
            border-radius: 50%;
            padding: 15px;
            font-size: 22px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: transform 0.2s ease-in-out;
            cursor: pointer;
            border: none;
        }
        .floating-button:hover {
            background-color: #1f8cba;
            transform: scale(1.1);
        }
        </style>
        <button class="floating-button" onclick="window.location.reload();">🔄</button>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    app = BloggingGeniusApp()
    app.run()











