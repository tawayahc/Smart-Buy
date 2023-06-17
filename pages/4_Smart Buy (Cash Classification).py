from roboflow import Roboflow
from PIL import Image
from gtts import gTTS
from io import BytesIO
import streamlit as st
import numpy as np

def format_changer(selected_output):
    match selected_output:
        case "1000B":
            return "ธนบัตร 1,000 บาท"
        case "100B":
            return "ธนบัตร 100 บาท"
        case "100B":
            return "เหรียญ 10 บาท"
        case "1B":
            return "เหรียญ 1 บาท"
        case "20B":
            return "ธนบัตร 20 บาท"
        case "25S":
            return "เหรียญ 25 สตางค์"
        case "2B":
            return "เหรียญ 2 บาท"
        case "500B":
            return "ธนบัตร 500 บาท"
        case "50B":
            return "ธนบัตร 50 บาท"
        case "50S":
            return "เหรียญ 50 สตางค์"
        case "5B":
            return "เหรียญ 5 บาท"
        case default:
            return "ไม่มีเงินสด"
        
def result_changer(selected_output):
    match selected_output:
        case "1000B":
            return 1000
        case "100B":
            return 100
        case "100B":
            return 10
        case "1B":
            return 1
        case "20B":
            return 20
        case "25S":
            return 0.25
        case "2B":
            return 2
        case "500B":
            return 500
        case "50B":
            return 50
        case "50S":
            return 0.50
        case "5B":
            return 5
        case default:
            return 0

def convert_str_to_audio_data(audio_text):
    audio_data = BytesIO()
    tts = gTTS(audio_text, lang = "th")
    tts.write_to_fp(audio_data)

    return audio_data

st.title("Smart Buy💵")

rf = Roboflow(api_key = "jZMsFfsrIiiMCfpYKlLa")
project = rf.workspace().project("thai-baht-detection")
model = project.version(3).model

st.header("โปรแกรมช่วยตรวจจับและจำแนกเงินสด🪙 (Cash Classification)")
st.divider()
input_image_BC = st.camera_input("📸กดถ่ายรูปเพื่อประมวลผล...", key = "firstCamera")

if input_image_BC is not None:
    amount = 0
    audio_text = "นี่เป็นการตรวจสอบเบื้องต้น ถ้าเป็นไปได้กรุณาตรวจสอบให้แน่ใจอีกครั้ง มีเงินสดดังนี้: "

    img = Image.open(input_image_BC)
    img_array = np.array(img)
    predicted_output = model.predict(img_array, confidence = 40, overlap = 30).json().get("predictions")

    number_of_cash = len(predicted_output)
    st.divider()
    st.subheader("ผลลัพธ์📑")
    st.write("มีเงินสดดังนี้:")
    if number_of_cash != 0:
        for i in range(number_of_cash):
            selected_output = (predicted_output)[i].get("class")
            confidence = (predicted_output)[i].get("confidence")
            result = format_changer(selected_output)
            money = result_changer(selected_output)
            amount = amount + money
            st.write(str(i + 1) + ". " + result + " (ค่าความมั่นใจ: " + str((format(confidence * 100, ".2f"))) + "%)")
            audio_text = audio_text + str(i + 1) + ". " + result + " (ค่าความมั่นใจ: " + str((format(confidence * 100, ".2f"))) + "%) "
    
    else:
        st.write("❌ตรวจไม่พบเงินสด กรุณาถ่ายรูปอีกครั้งเพื่อประมวลผลใหม่")
        audio_text = "ตรวจไม่พบเงินสด กรุณาถ่ายรูปอีกครั้ง เพื่อประมวลผลใหม่"

    if audio_text != "ตรวจไม่พบเงินสด กรุณาถ่ายรูปอีกครั้ง เพื่อประมวลผลใหม่":
        audio_text = audio_text + "มีเงินสดรวมกันทั้งหมด " + str(format(amount, ",.2f")) + " บาท"
        st.write("มีเงินสดรวมกันทั้งหมด " + str(format(amount, ",.2f")) + " บาท 💸")

    audio_data = convert_str_to_audio_data(audio_text)

    st.subheader("เสียง🔊")
    st.audio(audio_data)