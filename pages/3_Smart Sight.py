from ultralytics import YOLO
from PIL import Image
from gtts import gTTS
from io import BytesIO
import streamlit as st
import easyocr
import numpy as np
import cv2

def convert_str_to_audio_data(audio_text):
    audio_data = BytesIO()
    tts = gTTS(audio_text, lang = "th")
    tts.write_to_fp(audio_data)

    return audio_data

def show_audio():
    audio_data = convert_str_to_audio_data(audio_text)
    st.subheader("เสียง🔊")
    st.audio(audio_data)

st.title("Smart Sight👀")
st.header("โปรแกรมช่วยการรับรู้ข้อมูลของผลิตภัณฑ์📃")
st.divider()
input_image = st.camera_input("📸กดถ่ายรูปเพื่อประมวลผล...", key = "firstCamera")

if input_image is not None:
    audio_text = "นี่เป็นการตรวจสอบเบื้องต้น ถ้าเป็นไปได้กรุณาตรวจสอบให้แน่ใจอีกครั้ง รายละเอียดของสินค้ามีดังนี้: "

    img = Image.open(input_image)
    img_array = np.array(img)
    processed_image = img_array
    
    num_class = [1,2,7,5,3]
    information_list = ['Detail มีรายละเอียดดังนี้: ',
                        'EXP มีรายละเอียดดังนี้: ',
                        'Text มีรายละเอียดดังนี้: ',
                        'Nutrition Fact มีรายละเอียดดังนี้: ',
                        'FDA มีรายละเอียดดังนี้: ']
    information_checker = ['Detail มีรายละเอียดดังนี้: ',
                           'EXP มีรายละเอียดดังนี้: ',
                           'Text มีรายละเอียดดังนี้: ',
                           'Nutrition Fact มีรายละเอียดดังนี้: ',
                           'FDA มีรายละเอียดดังนี้: ']
    reader = easyocr.Reader(lang_list = ["th", "en"])

    model = YOLO("best.pt")
    results = model(img_array)
    for i in range(len(results[0])):
        boxes = results[0].boxes
        box = boxes[i].xyxy
        NClass = boxes[i].cls
        x = int(box[0][0])
        y = int(box[0][1])
        w = int(box[0][2])
        h = int(box[0][3])

        cv2.rectangle(processed_image, (x, y), (w, h), (255,0,0), 4)

        roi = img_array[y:h, x:w]
        if NClass in num_class:
            index = num_class.index(NClass)
            result = reader.readtext(roi)
            for text in result:
                information_list[index] = information_list[index] + text[1]
    
    st.divider()
    st.subheader("ผลลัพธ์📑")

    if information_checker == information_list:
        st.write("❌ตรวจไม่พบฉลากของผลิตภัณฑ์ กรุณาถ่ายรูปอีกครั้งเพื่อประมวลผลใหม่")
        audio_text = "ตรวจไม่พบฉลากของผลิตภัณฑ์ กรุณาถ่ายรูปอีกครั้ง เพื่อประมวลผลใหม่"
        show_audio()
    else: 
        for item in information_list:
            if item not in information_checker:
                audio_text = audio_text + item
                st.write(item)
                show_audio()
                st.subheader("รูปจากการประมวลผล⚙️")
                st.image(processed_image)