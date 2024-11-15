import os
from pathlib import Path
import tempfile
import argparse
from pysubparser import parser
from pydub import AudioSegment
from TransformersProcessor import TransformersProcessor as tts

def time_to_ms(time):
  return ((time.hour * 60 + time.minute) * 60 + time.second) * 1000 + time.microsecond / 1000


def generate_audio(path:str, speakerId:int = 10):
  outputDir = "output"
  if not os.path.isdir(outputDir):
    os.mkdir(outputDir)
  fileName = Path(path).name.split('.')[0]

  print("Generating audio file for {} with {}".format(path, "transformers"))      
  currentSpeaker = f"speaker_{speakerId}"
  subtitles = parser.parse(path)


  tts_engine = tts()
  
  audio_sum = AudioSegment.empty()

  with tempfile.TemporaryDirectory() as tempDir:
    print('Created temporary directory', tempDir)            
    iterNum = 0
    temp_file_path = os.path.join(tempDir, "temp.wav")
    prev_subtitle = None
    prev_audio_duration_ms = 0
    for subtitle in subtitles:
      iterNum = iterNum +1   
      tts_engine.ProcessAndWriteFile(subtitle.text, temp_file_path, speakerId=speakerId)

      audio_segment = AudioSegment.from_wav(temp_file_path)         

      print(subtitle.start, subtitle.text)
        
      if prev_subtitle is None:
          silence_duration_ms = time_to_ms(subtitle.start)
      else:
        silence_duration_ms = time_to_ms(subtitle.start) - time_to_ms(prev_subtitle.start) - prev_audio_duration_ms

      audio_sum = audio_sum + AudioSegment.silent(duration=silence_duration_ms) + audio_segment                   
        
      prev_subtitle = subtitle
      prev_audio_duration_ms = len(audio_segment)


    outputFIle:str = os.path.join(outputDir, fileName) + f"_{currentSpeaker}.wav"
    with open(outputFIle, 'wb') as out_f:
      audio_sum.export(out_f, format='wav')      

if __name__ == "__main__":      
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("-p", "--path", help="subtitle file path", required=True)
  
  args = arg_parser.parse_args()
  generate_audio(path=args.path)

