# Automated Speech-to-Text Transcription with Azure Speech Services

## 📌 Overview
This Python script automates the transcription of **audio and video files** into text using **Azure Cognitive Services' Speech-to-Text API**. It is designed to work seamlessly on **Linux Ubuntu** and can also be deployed on an **Azure Virtual Machine (VM)**.

## 🚀 Features
- Extracts audio from video files automatically 🎥🎵
- Converts audio to the required format for transcription
- Uses **Azure Speech Services** for accurate speech-to-text conversion 🗣️➡️📜
- Supports batch processing of multiple media files
- Runs on **Ubuntu** or **Azure VM**

## 🛠️ Prerequisites
Before running the script, ensure you have the following:
- **Microsoft Azure account** with Speech Services enabled
- **Python 3** installed
- **FFmpeg** installed (for handling media conversions):
  ```bash
  sudo apt update && sudo apt install ffmpeg -y
  ```
- Required Python dependencies:
  ```bash
  pip install azure-cognitiveservices-speech moviepy argparse
  ```

## 🔧 Setup: Azure Speech Services
1. **Create an Azure Account**
   - Sign up at [Azure Portal](https://portal.azure.com)

2. **Set Up Speech Services**
   - Create a Speech resource in Azure
   - Copy the **Key** and **Region** from the **Keys and Endpoint** tab

3. **Configure API Keys in the Script**
   ```python
   import azure.cognitiveservices.speech as speechsdk

   speech_config = speechsdk.SpeechConfig(
       subscription="YOUR_AZURE_SPEECH_KEY", 
       region="YOUR_AZURE_REGION"
   )
   ```

## 🔄 Workflow
1. **Extract audio** from a video file (if applicable)
2. **Convert audio** to 16kHz WAV format (required by Azure Speech Services)
3. **Send audio** to Azure Speech-to-Text API
4. **Save transcription** as a text file

### **Process Flow Diagram**
![Workflow](diagram-export-28-02-2025-13_10_43.png)

## ▶️ Running the Script
To transcribe an audio or video file, run:
```bash
python transcribe.py video1.mp4 audio1.wav
```

This will:
✅ Extract audio (if needed)  
✅ Convert it to the required format  
✅ Transcribe it using Azure Speech-to-Text  
✅ Save the text output in the **transcriptions/** folder  

## 🌍 Running on an Azure VM
This script can also be executed on an **Azure Virtual Machine (VM)** for cloud-based processing.

## 📌 Future Enhancements
- **Live speech transcription**
- **Multi-speaker recognition**
- **Integration with AI-driven content indexing**

## 📢 Contribute
Have suggestions? Feel free to open an issue or submit a PR!
