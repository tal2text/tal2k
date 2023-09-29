# from transformers import WhisperProcessor, WhisperForConditionalGeneration
# import soundfile as sf


# # load model and processor
# processor = WhisperProcessor.from_pretrained("openai/whisper-large-v2")
# model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v2")
# model.config.forced_decoder_ids = None

# import os
# import librosa
# import soundfile as sf
# from pathlib import Path
# import os
# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
# # folder_path = 'audio'
# folder_path = os.path.join(BASE_DIR, 'static/images/audio/')

# # Get all .wav files in the directory
# wav_files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]

# # for wav_file in wav_files:
# #     # Construct full file path
# #     full_file_path = os.path.join(folder_path, wav_file)

# #     # load audio file
# #     audio, original_sampling_rate = sf.read(full_file_path)

# #     # resample audio to 16000 Hz
# #     audio_resampled = librosa.resample(audio, orig_sr=original_sampling_rate, target_sr=16000)

# #     # convert audio to input features
# #     input_features = processor(audio_resampled, sampling_rate=16000, return_tensors="pt").input_features

# #     # generate token ids
# #     predicted_ids = model.generate(input_features)

# #     # decode token ids to text
# #     transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

# #     print(f"Transcription for {wav_file}: {transcription[0]}")

# # import librosa

# # # load audio file
# # audio, original_sampling_rate = sf.read('sample_audio.wav')

# # # resample audio to 16000 Hz
# # audio_resampled = librosa.resample(audio, orig_sr=original_sampling_rate, target_sr=16000)

# # # convert audio to input features
# # input_features = processor(audio_resampled, sampling_rate=16000, return_tensors="pt").input_features

# # # generate token ids
# # predicted_ids = model.generate(input_features)

# # # decode token ids to text
# # transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
# # print(transcription[0])

# # # generate token ids
# # predicted_ids = model.generate(input_features)
# # # decode token ids to text
# # transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
# # print(transcription[0])

# def transcribe_audio_file(audio_file_path):
#     audio, original_sampling_rate = sf.read(audio_file_path)
#     audio_resampled = librosa.resample(audio, orig_sr=original_sampling_rate, target_sr=16000)
#     input_features = processor(audio_resampled, sampling_rate=16000, return_tensors="pt").input_features
#     predicted_ids = model.generate(input_features)
#     transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
#     return transcription[0]