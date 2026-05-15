import wave
import os
import numpy

def pcm_to_wav(pcm_file_path, wav_file_path, sample_rate=16000, channels=1, sample_width=2):
    """
    将 PCM 文件转换为 WAV 文件
    
    参数:
    pcm_file_path (str): 输入的 PCM 文件路径
    wav_file_path (str): 输出的 WAV 文件路径
    sample_rate (int): 采样率 (如 8000, 16000, 44100)，默认 16000
    channels (int): 声道数 (1: 单声道, 2: 立体声)，默认 1
    sample_width (int): 采样位宽 (字节)，16位=2字节，8位=1字节，默认 2
    """
    
    # 1. 打开 PCM 文件（二进制只读模式）
    with open(pcm_file_path, 'rb') as pcm_file:
        pcm_data = pcm_file.read()
    
    # # 2. 创建 WAV 文件
    print(wav_file_path)
    print("\n")
    with wave.open(wav_file_path, 'wb') as wav_file:
        # 3. 设置 WAV 文件参数
        # nchannels: 声道数
        wav_file.setnchannels(channels)
        
        # sampwidth: 采样宽度（字节），16位量化就是 2 字节
        wav_file.setsampwidth(sample_width)
        
        # framerate: 采样率
        wav_file.setframerate(sample_rate)
        
        # nframes: 帧数，通常设为数据长度，或者直接写数据让库自动计算
        # wav_file.setnframes(len(pcm_data) // (channels * sample_width))
        
        # 4. 写入音频数据
        wav_file.writeframes(pcm_data)
    print("========")
# --- 使用示例 ---
if __name__ == "__main__":

    # print(numpy.__file__)
    
    # 请根据你的 PCM 文件实际参数修改下面的值
    name = "1767963195058"
    input_pcm = "/tmp/" + name + ".pcm"  # 你的输入文件名
    output_wav = "/tmp/" + name + ".wav"     # 输出文件名
    
    # 常见语音识别参数：16kHz, 单声道, 16位


    pcm_to_wav(
        pcm_file_path=input_pcm,
        wav_file_path=output_wav,
        sample_rate=16000,   # 采样率
        channels=1,          # 声道
        sample_width=2       # 16位采样对应 2 字节
    )
    print(f"转换完成！已保存为 {output_wav}")


