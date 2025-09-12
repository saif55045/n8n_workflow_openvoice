import streamlit as st
import requests
import base64
import io
import PyPDF2
import json
from pathlib import Path

# Configure Streamlit page
st.set_page_config(
    page_title="OpenVoice TTS & Voice Cloning",
    page_icon="🎤",
    layout="wide"
)

# App title and description
st.title("🎤 OpenVoice TTS & Voice Cloning")
st.markdown("Convert text to speech using default voice or clone your own voice!")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")
n8n_webhook_url = st.sidebar.text_input(
    "n8n Webhook URL", 
    value="http://localhost:5678/webhook/tts",
    help="The n8n webhook endpoint URL"
)

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Text Input")
    
    # Tab interface for different input methods
    tab1, tab2 = st.tabs(["✍️ Manual Text", "📄 Upload File"])
    
    with tab1:
        text_input = st.text_area(
            "Enter your text here:",
            height=200,
            placeholder="Type or paste your text here...",
            help="Enter the text you want to convert to speech"
        )
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload a text or PDF file",
            type=['txt', 'pdf'],
            help="Upload a .txt or .pdf file to extract text from"
        )
        
        extracted_text = ""
        file_content = None
        file_name = None
        
        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_type = file_name.lower().split('.')[-1]
            
            if file_type == 'txt':
                # Read text file
                file_content = uploaded_file.read().decode('utf-8')
                extracted_text = file_content
                st.success(f"✅ Text file loaded: {file_name}")
                
            elif file_type == 'pdf':
                # Read PDF file
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
                    
                    file_content = text_content
                    extracted_text = text_content
                    st.success(f"✅ PDF file loaded: {file_name}")
                    
                except Exception as e:
                    st.error(f"❌ Error reading PDF: {str(e)}")
            
            # Show preview of extracted text
            if extracted_text:
                st.subheader("📖 Extracted Text Preview")
                st.text_area(
                    "Preview:", 
                    value=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                    height=150,
                    disabled=True
                )

with col2:
    st.header("🎵 Voice Options")
    
    # Voice selection
    voice_option = st.radio(
        "Choose voice type:",
        ["🔊 Default Voice", "🎭 Custom Voice (Clone)"],
        help="Select whether to use the default voice or clone a custom voice"
    )
    
    use_custom_voice = voice_option == "🎭 Custom Voice (Clone)"
    
    # Voice file upload for custom voice
    voice_file = None
    if use_custom_voice:
        st.subheader("🎤 Upload Voice Sample")
        voice_file = st.file_uploader(
            "Upload your voice sample",
            type=['wav', 'mp3', 'flac'],
            help="Upload a clear voice sample (10-30 seconds recommended)"
        )
        
        if voice_file:
            st.success(f"✅ Voice sample loaded: {voice_file.name}")
            # Show audio player for preview
            st.audio(voice_file, format='audio/wav')
    
    # Generation settings
    st.subheader("⚙️ Settings")
    language = st.selectbox(
        "Language:",
        ["EN", "ES", "FR", "ZH", "JA", "KO"],
        help="Select the language for speech generation"
    )

# Generation section
st.header("🚀 Generate Audio")

# Get final text to process
final_text = ""
if uploaded_file and extracted_text:
    final_text = extracted_text
elif text_input:
    final_text = text_input

# Validation and generation button
if final_text.strip():
    st.info(f"📊 Text length: {len(final_text)} characters")
    
    if use_custom_voice and not voice_file:
        st.warning("⚠️ Please upload a voice sample for custom voice generation")
        generate_button_disabled = True
    else:
        generate_button_disabled = False
    
    # Generate button
    if st.button(
        "🎵 Generate Audio", 
        disabled=generate_button_disabled,
        help="Click to generate audio from your text"
    ):
        with st.spinner("🔄 Generating audio... This may take a moment."):
            try:
                # Prepare request data
                request_data = {
                    "text": final_text,
                    "use_custom_voice": use_custom_voice,
                    "language": language
                }
                
                # Add file content if uploaded
                if uploaded_file and file_content:
                    request_data["file_content"] = file_content
                    request_data["file_name"] = file_name
                
                # Prepare files for multipart upload
                files = {}
                if voice_file and use_custom_voice:
                    # Convert uploaded file to base64 for JSON transmission
                    voice_content = voice_file.read()
                    voice_base64 = base64.b64encode(voice_content).decode('utf-8')
                    request_data["voice_file"] = voice_base64
                
                # Send request to n8n webhook
                response = requests.post(
                    n8n_webhook_url,
                    json={"body": request_data},
                    timeout=120,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                    except json.JSONDecodeError:
                        st.error("❌ Invalid JSON response from server")
                        st.text(f"Response content: {response.text}")
                        st.stop()
                    
                    if result.get("success", False):
                        st.success("✅ Audio generated successfully!")
                        
                        # Display results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("🎵 Generated Audio")
                            audio_url = result.get("audio_url")
                            
                            if audio_url:
                                # Download and play audio
                                try:
                                    audio_response = requests.get(audio_url)
                                    if audio_response.status_code == 200:
                                        st.audio(audio_response.content, format='audio/wav')
                                        
                                        # Download button
                                        st.download_button(
                                            label="💾 Download Audio",
                                            data=audio_response.content,
                                            file_name=f"generated_audio_{result.get('voice_type', 'default')}.wav",
                                            mime="audio/wav"
                                        )
                                    else:
                                        st.error("❌ Could not load audio file")
                                except Exception as e:
                                    st.error(f"❌ Error loading audio: {str(e)}")
                        
                        with col2:
                            st.subheader("📊 Generation Info")
                            st.info(f"**Voice Type:** {result.get('voice_type', 'default')}")
                            st.info(f"**Text Length:** {len(result.get('text_used', ''))} characters")
                            st.info(f"**Language:** {language}")
                            
                            # Show processed text preview
                            if result.get('text_used'):
                                with st.expander("📝 Processed Text"):
                                    st.text(result['text_used'][:300] + "..." if len(result['text_used']) > 300 else result['text_used'])
                    
                    else:
                        st.error(f"❌ Generation failed: {result.get('message', 'Unknown error')}")
                        if result.get('error'):
                            st.error(f"Error details: {result['error']}")
                
                else:
                    st.error(f"❌ Request failed with status code: {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. The audio generation is taking longer than expected.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Please ensure n8n is running and the webhook URL is correct.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

else:
    st.warning("⚠️ Please enter text or upload a file to generate audio.")

# Status section
st.header("📊 System Status")

# Check service status
status_col1, status_col2 = st.columns(2)

with status_col1:
    st.subheader("🔧 OpenVoice API")
    try:
        api_response = requests.get("http://localhost:8000/health", timeout=5)
        if api_response.status_code == 200:
            st.success("✅ API is running")
            api_data = api_response.json()
            st.caption(f"Service: {api_data.get('service', 'N/A')}")
        else:
            st.error("❌ API is not responding correctly")
    except:
        st.error("❌ API is not accessible")

with status_col2:
    st.subheader("🔄 n8n Webhook")
    try:
        # Simple test to check if n8n is reachable
        test_response = requests.get("http://localhost:5678", timeout=5)
        if test_response.status_code in [200, 404]:  # 404 is normal for n8n root
            st.success("✅ n8n is running")
        else:
            st.warning("⚠️ n8n may not be running")
    except:
        st.error("❌ n8n is not accessible")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🎤 <strong>OpenVoice TTS & Voice Cloning System</strong></p>
        <p>Powered by OpenVoice, n8n, and Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
)
