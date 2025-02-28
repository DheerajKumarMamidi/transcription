import os
import time
import argparse
import subprocess
import threading
import azure.cognitiveservices.speech as speechsdk
from moviepy.video.io.VideoFileClip import VideoFileClip
from azure.cognitiveservices.speech.audio import AudioConfig, PushAudioInputStream

# === Handle Command-Line Arguments ===
parser = argparse.ArgumentParser(description="Transcribe speech from multiple video and audio files.")
parser.add_argument("media_files", nargs="+", help="Paths to video/audio files (space-separated)")
args = parser.parse_args()

# Start total process timer
total_start_time = time.time()

# Lists to store successful and failed transcriptions
successful_transcriptions = []
failed_transcriptions = []

# Supported media file extensions
video_extensions = (".mp4", ".avi", ".mov", ".mkv")
audio_extensions = (".wav", ".mp3", ".m4a", ".ogg")

def get_audio_length(audio_file):
    """Get the length (duration) of an audio file using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return float(result.stdout.strip())  # Returns duration in seconds
    except Exception as e:
        print(f"❌ Error getting audio length for '{audio_file}': {e}")
        return None

def convert_audio_to_wav(input_audio):
    """Convert non-WAV audio files OR incorrect WAV format to correct WAV format (16kHz, mono)."""
    output_wav = os.path.splitext(input_audio)[0] + "_fixed.wav"

    print(f"🔄 Converting '{input_audio}' to 16kHz, mono WAV format...")
    subprocess.run([
        "ffmpeg", "-i", input_audio, "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", output_wav, "-y"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return output_wav

def extract_audio(video_file):
    """Extract audio from video and save as a WAV file."""
    audio_file = f"{os.path.splitext(os.path.basename(video_file))[0]}_audio.wav"

    try:
        print(f"🎬 Extracting audio from '{video_file}'...")
        subprocess.run([
            "ffmpeg", "-i", video_file, "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_file, "-y"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"✅ Audio extracted and saved as: {audio_file}")
        return audio_file
    except Exception as e:
        print(f"❌ Error extracting audio from '{video_file}': {e}")
        return None

def transcribe_audio(audio_file, speech_config):
    """Transcribe an audio file using Azure Speech-to-Text without stopping on silence."""
    if not os.path.exists(audio_file):
        print(f"❌ Skipping: Audio file '{audio_file}' not found!")
        return None

    print(f"🎧 Transcribing '{audio_file}'...")

    push_stream = PushAudioInputStream()
    audio_config = AudioConfig(stream=push_stream)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # 🔹 Prevents transcription from stopping due to silence
    speech_config.set_property(
        property_id=speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
        value="60000"  # 60 seconds silence tolerance
    )

    transcriptions = []
    done = threading.Event()  # Event to signal when recognition is complete

    def recognized_handler(evt):
        """Stores recognized text from Azure."""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcriptions.append(evt.result.text)

    def stop_handler(evt):
        """Stops recognition when session ends."""
        print("✅ Transcription session stopped.")
        done.set()

    # Attach event handlers
    speech_recognizer.recognized.connect(recognized_handler)
    speech_recognizer.session_stopped.connect(stop_handler)
    speech_recognizer.canceled.connect(stop_handler)

    speech_recognizer.start_continuous_recognition()

    # 🔹 Send audio data in a separate thread
    def stream_audio():
        with open(audio_file, "rb") as audio:
            while chunk := audio.read(4096):  # Read in 4KB chunks
                push_stream.write(chunk)
        push_stream.close()

    audio_thread = threading.Thread(target=stream_audio)
    audio_thread.start()
    
    done.wait()
    speech_recognizer.stop_continuous_recognition()

    return " ".join(transcriptions)

for media_file in args.media_files:
    print(f"\n🔹 Processing: {media_file}")
    file_start_time = time.time()

    original_filename = os.path.splitext(os.path.basename(media_file))[0]

    file_ext = os.path.splitext(media_file)[1].lower()
    audio_file = media_file

    if file_ext in video_extensions:
        # Convert video to audio
        audio_file = extract_audio(media_file)
        if not audio_file:
            failed_transcriptions.append(media_file)
            continue

    elif file_ext in audio_extensions:
        # Convert non-WAV audio files or incorrect WAV formats
        audio_file = convert_audio_to_wav(media_file)

    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SERVICE_REGION")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    transcription_text = transcribe_audio(audio_file, speech_config)

    if transcription_text:
        # Ensure 'transcriptions' folder exists
        output_folder = "transcriptions"
        os.makedirs(output_folder, exist_ok=True)

        # Save transcriptions in 'transcriptions' folder
        transcription_file = os.path.join(output_folder, f"{original_filename}_transcription.txt")

        with open(transcription_file, "w") as file:
            file.write(transcription_text)
    
        print(f"✅ Transcription saved to: {transcription_file}")
        successful_transcriptions.append(media_file)
    else:
        failed_transcriptions.append(media_file)

    file_end_time = time.time()
    minutes, seconds = divmod(int(file_end_time - file_start_time), 60)
    print(f"⏱️ Time taken: {minutes}m {seconds}s")

# Stop the total process timer
total_end_time = time.time()
total_time_taken = total_end_time - total_start_time
total_minutes, total_seconds = divmod(int(total_time_taken), 60)

# Summary Report
print("\n🚀 All media files processed!")
print(f"⏱️ Total time taken (start to finish): {total_minutes}m {total_seconds}s")

if successful_transcriptions:
    print("\n✅ Successfully transcribed files:")
    for file in successful_transcriptions:
        print(f"   - {file}")

if failed_transcriptions:
    print("\n❌ Failed transcriptions:")
    for file in failed_transcriptions:
        print(f"   - {file}")