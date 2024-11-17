import os
from pathlib import Path
import tempfile
import argparse
from pysubparser import parser
from pydub import AudioSegment
from TransformersProcessor import TransformersProcessor as tts

def time_to_ms(time):
  return ((time.hour * 60 + time.minute) * 60 + time.second) * 1000 + time.microsecond / 1000


def generate_audio(engine:tts, speakerIds:list[int] = [7]):
  tts_engine = engine
  
  if( not speakerIds):
    speakerIds = [7]
  
  outputDir = "output"
  inputDir = 'test'
  if not os.path.isdir(inputDir):
    os.mkdir(inputDir)
  
  srtFiles = [os.path.join(inputDir, name) for name in os.listdir(inputDir) if name.endswith('.srt')]
  print(srtFiles)

  if not os.path.isdir(outputDir):
    os.mkdir(outputDir)
  
  for path in srtFiles:

    fileName = Path(path).name.split('.')[0]

    for speakerId in speakerIds:

      print("Generating audio file for {} with {} for speaker {}".format(path, "transformers", speakerId))      
      currentSpeaker = f"speaker_{speakerId}"
      
      subtitles = parser.parse(path)      
      audio_sum = AudioSegment.empty()

      with tempfile.TemporaryDirectory() as tempDir:
        print('Created temporary directory', tempDir)            
        temp_file_path = os.path.join(tempDir, "temp.wav")
        prev_subtitle = None
        prev_audio_duration_ms = 0
        for subtitle in subtitles:
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

def check_Ids(value:str):
  values = value.split(",")
  ivalues = list(map(int,values))

  for ivalue in ivalues:
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
  return ivalues

if __name__ == "__main__":      
  arg_parser = argparse.ArgumentParser()
  # arg_parser.add_argument("-p", "--path", help="subtitle file path", required=True,dest='path')
  arg_parser.add_argument("-s", "--speakers", help="speaker ids numbers comma seperated", required=False, type=check_Ids, dest='speakers')
  # arg_parser.add_argument("-o", "--output", help="speaker id", required=False, type=str, dest='output')
  
  args = arg_parser.parse_args()
  engine = tts()

  generate_audio(speakerIds=args.speakers,engine=engine)

