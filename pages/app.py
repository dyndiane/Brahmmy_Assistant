import streamlit as st
from PIL import Image
from controller import detect_image
import os
from langchain_core.messages import HumanMessage, AIMessage
from controller import load_pdf_documents, load_db, create_or_append_db,create_chain, process_chat, split_documents
import speech_recognition as sr
import pyttsx3
import threading
import cv2
import numpy as np
from datetime import datetime
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Brahmmy's App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide the main menu (hamburger/sidebar menu)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Get the selected section from the query parameter
section = st.query_params.get("section", "architecture")

# Set the chatbot system prompt based on the section
if section == "architecture":
    system_prompt = """You are a chatbot for architecture students. Only answer questions relevant to architecture.
    If asked about computer engineering topics (like Arduino, programming, etc.), politely decline and explain that you can only answer architecture-related questions.
    Focus on architectural design, building structures, urban planning, and related topics."""
elif section == "computer_engineering":
    system_prompt = """You are a chatbot for computer engineering students. Only answer questions relevant to computer engineering.
    You can provide code examples, explain programming concepts, and discuss hardware topics like Arduino, microcontrollers, etc.
    If asked about other engineering fields, politely decline and explain that you can only answer computer engineering-related questions."""
elif section == "industrial_engineering":
    system_prompt = """You are a chatbot for industrial engineering students. Only answer questions relevant to industrial engineering.
    If asked about computer engineering topics (like Arduino, programming, etc.), politely decline and explain that you can only answer industrial engineering-related questions.
    Focus on manufacturing processes, operations research, supply chain management, and related topics."""
elif section == "information_technology":
    system_prompt = """You are a chatbot for information technology students. Only answer questions relevant to information technology.
    Important: When users ask for 'code', understand that they are likely referring to configuration or setup instructions, not programming code.
    Focus on system administration, network configuration, database management, and IT infrastructure.
    If asked about programming or development, clarify that you'll provide configuration instructions rather than code."""
else:
    system_prompt = "You are a helpful university chatbot."

# Initialize speech recognition and TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_lock = threading.Lock()  # Create a lock for TTS operations

# Function to convert speech to text
def speech_to_text():
    with sr.Microphone() as source:
        st.sidebar.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except Exception as e:
            st.sidebar.error(f"Error recognizing speech: {str(e)}")
            return None

# Function to convert text to speech
def text_to_speech(text):
    with tts_lock:  # Use lock to ensure only one thread can use the engine at a time
        tts_engine.say(text)
        tts_engine.runAndWait()

# Function to handle webcam capture and object detection
def process_webcam_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.sidebar.error("Could not open webcam")
        return None, None
    
    # Create placeholder for the webcam feed and captured image
    webcam_placeholder = st.sidebar.empty()
    
    # Create stop button
    stop_button = st.sidebar.button("Stop Camera", key="stop_camera")
    
    # Capture for 5 seconds
    start_time = datetime.now()
    while (datetime.now() - start_time).seconds < 5:
        ret, frame = cap.read()
        if not ret:
            st.sidebar.error("Failed to capture image")
            cap.release()
            webcam_placeholder.empty()
            return None, None
        
        # Convert frame to RGB for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        webcam_placeholder.image(frame_rgb, channels="RGB")
        
        if stop_button:
            break
    
    # Capture final frame
    ret, frame = cap.read()
    if not ret:
        st.sidebar.error("Failed to capture image")
        cap.release()
        webcam_placeholder.empty()
        return None, None
    
    # Release the webcam
    cap.release()
    
    # Save the captured frame
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(upload_directory, f"webcam_{timestamp}.jpg")
    cv2.imwrite(image_path, frame)
    
    # Display the captured image in the same placeholder
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    webcam_placeholder.image(frame_rgb, channels="RGB", caption="Captured Image")
    
    # Detect objects in the image
    obj_response = detect_image(image_path)
    
    return image_path, obj_response

#upload directory
upload_directory = "uploaded_images"
obj_response=""
#chain
chain =""
file_path = None  # Initialize file_path as None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "last_captured_image" not in st.session_state:
    st.session_state.last_captured_image = None
if "last_detected_objects" not in st.session_state:
    st.session_state.last_detected_objects = None
if "captured_images" not in st.session_state:
    st.session_state.captured_images = []
if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)

# Sidebar for New Chat, image upload, TTS, and webcam
with st.sidebar:
    # Add New Chat (+) button to the top of the sidebar
    if st.button("➕ New Chat", key="new_chat_button"):
        st.session_state.chat_history = []
        st.session_state.ai_response = None
        st.session_state.last_captured_image = None
        st.session_state.last_detected_objects = None
        st.session_state.captured_images = []  # Clear all captured images
        # Optionally, reset other state variables if needed

    st.title("Upload Image")
    uploaded_image = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg", "gif", "bmp"], key="image_uploader")
    if uploaded_image is not None:
        # Save the uploaded file to the local directory
        file_path = os.path.join(upload_directory, uploaded_image.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
    if uploaded_image is not None:
        # Open and display the image
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        obj_response = detect_image(file_path)
        # Print the image path (if you need to display it)
        st.write(f"Uploaded Image Path: {uploaded_image.name}")
        st.write(f"response: {obj_response}")
    else:
        st.write("No image uploaded yet.")

    # Show all captured webcam images in the sidebar
    if st.session_state.captured_images:
        st.sidebar.title("Captured Photos")
        st.sidebar.markdown(
            "<div style='position: relative; height: 100px; margin-top: -5px;'>",  # Container for overlapping images
            unsafe_allow_html=True
        )
        for i, img_path in enumerate(st.session_state.captured_images):
            try:
                img = Image.open(img_path)
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                st.sidebar.markdown(
                    f"""
                    <img src='data:image/jpeg;base64,{img_b64}'
                         style='
                            position: absolute;
                            top: {i*10}px;  # Small vertical offset for overlap
                            left: {i*10}px;  # Small horizontal offset for overlap
                            width: 100px;
                            height: 75px;
                            object-fit: cover;
                            margin-top: 10px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                            border-radius: 8px;
                            border: 2px solid #fff;
                            z-index: {i};  # Ensure proper stacking order
                         '>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.sidebar.error(f"Error displaying image: {str(e)}")
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

    st.title("Upload a Document")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf", key="pdf_uploader")
    if uploaded_file is not None:
        # Save uploaded file to a temporary directory
        temp_dir = "./temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        db_file = "vector_store"
        documents = load_pdf_documents(file_path)
        docs = split_documents(documents)
        vector_store = create_or_append_db(docs, db_file)
        vector_store = load_db(db_file)
        chain = create_chain(vector_store, file_path, system_prompt)
        st.success(f"Uploaded: {uploaded_file.name}")

    # Add TTS button in sidebar
    st.sidebar.title("Voice Input")
    tts_button = st.sidebar.button("🎤 Click to Speak", help="Click and speak your query", key="tts_button")
    
    if tts_button:
        user_query = speech_to_text()
        if user_query:
            st.session_state.chat_history.append(HumanMessage(user_query))
            with st.chat_message("Human"):
                st.markdown(user_query)
            with st.chat_message("AI"):
                if not chain:
                    if file_path is None:
                        st.error("Please upload a document first before using the chat.")
                    else:
                        db_file = "vector_store"
                        vector_store = load_db(db_file)
                        chain = create_chain(vector_store, file_path, system_prompt)
                        if obj_response:
                            user_query = user_query + str(obj_response.content)
                ai_response = process_chat(chain, user_query, st.session_state.chat_history)
                st.session_state.ai_response = ai_response
                st.markdown(ai_response)
                # Convert AI response to speech in a separate thread
                threading.Thread(target=text_to_speech, args=(ai_response,)).start()
            st.session_state.chat_history.append(AIMessage(ai_response))

    # Add webcam section
    st.sidebar.title("Live Webcam")
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    if 'last_webcam_image' not in st.session_state:
        st.session_state.last_webcam_image = None
    if 'captured_images' not in st.session_state:
        st.session_state.captured_images = []

    if st.sidebar.button("📸 Start Camera", help="Click to start webcam", key="webcam_button"):
        st.session_state.camera_active = True
        image_path, detected_objects = process_webcam_image()
        if image_path and detected_objects:
            # Store the current webcam image
            st.session_state.last_webcam_image = image_path
            st.session_state.last_detected_objects = detected_objects
            
            # Add the captured image to history
            if image_path not in st.session_state.captured_images:
                st.session_state.captured_images.append(image_path)
            
            # Add a user message about capturing the image
            st.session_state.chat_history.append(HumanMessage("I've captured an image with the webcam."))
            with st.chat_message("Human"):
                st.write("I've captured an image with the webcam.")
            
            # Add AI response about the detected objects
            detected_text = detected_objects.content if hasattr(detected_objects, 'content') else str(detected_objects)
            with st.chat_message("AI"):
                st.write("I can see the following objects in the image:", detected_text)
            st.session_state.chat_history.append(AIMessage(f"I can see the following objects in the image: {detected_text}"))

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

# Text input for chat
user_query = st.chat_input("Your Message", key="chat_input")

if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
    with st.chat_message("AI"):
        if not chain:
            if file_path is None:
                st.error("Please upload a document first before using the chat.")
            else:
                db_file = "vector_store"
                vector_store = load_db(db_file)
                chain = create_chain(vector_store, file_path, system_prompt)
                if obj_response:
                    user_query = user_query + str(obj_response.content)
        # Include last captured image context if available
        if st.session_state.last_detected_objects:
            user_query = f"{user_query} (Context: Last captured image shows {st.session_state.last_detected_objects})"
        ai_response = process_chat(chain, user_query, st.session_state.chat_history)
        st.session_state.ai_response = ai_response
        st.markdown(ai_response)
        # Convert AI response to speech in a separate thread
        threading.Thread(target=text_to_speech, args=(ai_response,)).start()
    st.session_state.chat_history.append(AIMessage(ai_response))


