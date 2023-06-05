from playsound import playsound
from google.cloud import texttospeech

class TTS:
    def __init__(self, auth_filepath, language_code):
        self.client = texttospeech.TextToSpeechClient.from_service_account_file(auth_filepath)
        self.voice = texttospeech.VoiceSelectionParams(language_code=language_code,
                                                       ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)

        self.audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    def run(self, input_text: str) -> bool:
        synthesis_input = texttospeech.SynthesisInput(text=input_text)
        response = self.client.synthesize_speech(input=synthesis_input,
                                                 voice=self.voice,
                                                 audio_config=self.audio_config)

        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            playsound("./output.mp3")

        return True

if __name__ == "__main__":
    tts = TTS("./gcp.json", "ko-KR")
    tts.run("hello world!")