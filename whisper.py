import whisperx
import gc 
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
device = "cpu"
batch_size = 32
compute_type = "float32"
model = whisperx.load_model("medium", device, compute_type=compute_type, language='ru')
def translate_audio(audio_file):
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size, language='ru')
    if result:
        soob = str(result['segments'][0]['text'])
        return soob.strip() + "?" if soob.strip()[-1] not in ".!?" else soob.strip()[:-1]+"?"
    else:
        return ""
