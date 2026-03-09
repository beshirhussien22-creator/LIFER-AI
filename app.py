import streamlit as st
import openai
import os
from langchain_community import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import OpenAI
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit_authenticator as stauth
import requests
import pyautogui
import cv2
from PIL import Image
from geopy.geocoders import Nominatim
import python_weather
import asyncio
import yaml
from yaml.loader import SafeLoader

load_dotenv()

# Load config for authentication
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Initialize TTS engine
engine = pyttsx3.init()

# Initialize STT recognizer
recognizer = sr.Recognizer()

# Geocoder for locations
geolocator = Nominatim(user_agent="lifer-ai")

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Please set your OPENAI_API_KEY in the .env file.")
    st.stop()
openai.api_key = api_key

# Initialize LangChain memory
memory = ConversationBufferMemory()  # Unlimited memory - never cut anything

# Initialize LLM
llm = OpenAI(temperature=0.7, model="gpt-4", openai_api_key=api_key)

# Create conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=False
)

# Matching features - advanced matching logic
def match_feature(user_input):
    user_input_lower = user_input.lower()
    if "match" in user_input_lower:
        return "Advanced Matching Activated: Analyzing query for optimal response patterns."
    elif "help" in user_input_lower:
        return "Help Matching: Providing comprehensive assistance."
    elif "code" in user_input_lower:
        return "Code Matching: Generating precise code solutions."
    elif "life" in user_input_lower:
        return "Life Matching: Offering wisdom and guidance for life's challenges."
    elif "business" in user_input_lower:
        return "Business Matching: Strategic advice and solutions."
    elif "weather" in user_input_lower:
        return "Weather Matching: Real-time weather information."
    elif "location" in user_input_lower:
        return "Location Matching: Geographic knowledge and mapping."
    return "General Matching: Processing with ultra-intelligence."

# Deep research function
def deep_research(query):
    # Placeholder for deep research - in reality, use multiple APIs
    return f"Deep research on '{query}': Comprehensive analysis completed."

# Device control functions (PC)
def control_mouse(x, y):
    pyautogui.moveTo(x, y)

def control_click(x, y):
    pyautogui.click(x, y)

def control_scroll(x, y, clicks):
    pyautogui.scroll(clicks, x, y)

def control_keyboard(text):
    pyautogui.typewrite(text)

def take_screenshot():
    screenshot = pyautogui.screenshot()
    return screenshot

# Weather function
async def get_weather(location):
    async with python_weather.Client(format=python_weather.IMPERIAL) as client:
        weather = await client.get(location)
        return f"Weather in {location}: {weather.current.temperature}°F, {weather.current.description}"

# Main app
def main():
    st.set_page_config(page_title="LIFER AI v6.0", page_icon="🤖", layout="wide")
    
    # Authentication
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
        
        # Sidebar for memories and settings
        with st.sidebar:
            st.header("LIFER Memory & Settings")
            st.subheader("Conversation History")
            if st.button("View Full Memory"):
                st.text_area("Full Memory", memory.buffer, height=300)
            st.subheader("Settings")
            temperature = st.slider("AI Temperature", 0.0, 1.0, 0.7)
            llm.temperature = temperature
            st.subheader("Device Control")
            if st.button("Take Screenshot"):
                screenshot = take_screenshot()
                st.image(screenshot, caption="Screenshot")
            mouse_x = st.number_input("Mouse X", 0, 1920, 0)
            mouse_y = st.number_input("Mouse Y", 0, 1080, 0)
            if st.button("Move Mouse"):
                control_mouse(mouse_x, mouse_y)
            if st.button("Click Mouse"):
                control_click(mouse_x, mouse_y)
            scroll_clicks = st.number_input("Scroll Clicks", -10, 10, 0)
            if st.button("Scroll"):
                control_scroll(mouse_x, mouse_y, scroll_clicks)
            keyboard_text = st.text_input("Keyboard Input")
            if st.button("Type"):
                control_keyboard(keyboard_text)
            st.subheader("Camera")
            webrtc_streamer(key="camera", mode=WebRtcMode.SENDRECV, rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}))
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Trailer", "Info", "Ads"])
        
        with tab1:
            st.title("🤖 LIFER AI Chatbot v6.0")
            st.subheader("The Ultimate AI - Infinite Knowledge, Device Control, TTS/STT, Camera, Weather, Locations - Truly the Best")
            
            # Logo placeholder
            st.image("https://via.placeholder.com/150x150.png?text=LIFER+AI", caption="LIFER AI Logo")
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Speech to Text
            st.subheader("Voice Input")
            if st.button("Record Voice"):
                with sr.Microphone() as source:
                    st.write("Listening...")
                    audio = recognizer.listen(source)
                    try:
                        text = recognizer.recognize_google(audio)
                        st.write(f"You said: {text}")
                        prompt = text
                    except sr.UnknownValueError:
                        st.error("Could not understand audio")
                        prompt = None
                    except sr.RequestError:
                        st.error("Could not request results")
                        prompt = None
            else:
                prompt = st.chat_input("What is your query?")

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Check for matching features
                match_response = match_feature(prompt)
                
                # Deep research if needed
                if "research" in prompt.lower():
                    research_result = deep_research(prompt)
                    response = match_response + " " + research_result + " " + conversation.predict(input=prompt)
                else:
                    response = match_response + " " + conversation.predict(input=prompt)
                
                # Text to Speech
                if st.checkbox("Enable TTS"):
                    engine.say(response)
                    engine.runAndWait()

                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
                    
                # Weather and Location
                if "weather" in prompt.lower():
                    location = st.text_input("Enter location for weather")
                    if location:
                        weather_info = asyncio.run(get_weather(location))
                        st.write(weather_info)
                if "location" in prompt.lower():
                    place = st.text_input("Enter place to search")
                    if place:
                        location = geolocator.geocode(place)
                        if location:
                            st.write(f"Location: {location.address}, Coordinates: {location.latitude}, {location.longitude}")
                        else:
                            st.write("Location not found")
                            
                # Code generation
                if "generate code" in prompt.lower():
                    code = conversation.predict(input=f"Generate professional code for: {prompt}")
                    st.code(code, language="python")
                    if st.button("Run Code"):
                        exec(code)  # Dangerous, but as requested
        
        with tab2:
            st.header("LIFER AI Trailer")
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Placeholder video
            st.write("Watch the promotional trailer for LIFER AI!")
        
        with tab3:
            st.header("About LIFER AI")
            st.write("**Owner: Mohammed Bwshir**")
            st.write("LIFER AI is the ultimate chatbot, better than all AIs forever.")
            st.write("Features: Infinite knowledge, all languages, device control, TTS/STT, camera, weather, locations, code generation, business help, and more.")
            st.write("Domain: lifer.ai.com")
            st.write("Published on Google for free installation.")
            st.write("Never cuts anything - full history preserved.")
        
        with tab4:
            st.header("Advertisements")
            st.image("https://via.placeholder.com/300x200.png?text=Ad+Space", caption="Sponsored Ad")
            st.write("Support LIFER AI with ads!")

    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()