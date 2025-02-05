import os
from faster_whisper import WhisperModel
from app import Config
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class WhisperService:
    def __init__(self):
        try:
            print("Initializing Whisper model...")
            model_path = os.path.join(Config.MODEL_PATH, "faster-whisper-medium")
            print(f"Looking for model in: {model_path}")
            
            if not os.path.exists(model_path):
                print(f"Model directory not found at {model_path}")
                print("Please download the model files manually and place them in this directory")
                raise Exception("模型文件不存在，请先下载模型")
            
            try:
                # 首先尝试使用 CUDA，并配置多线程参数
                print("Trying CUDA model with multi-threading...")
                self.model = WhisperModel(
                    model_path,
                    device="cuda",
                    compute_type="float16",
                    local_files_only=True,
                    cpu_threads=8,           # CPU 线程数
                    num_workers=4            # 并行工作进程数
                )
                print("CUDA model initialized successfully")
            except Exception as cuda_e:
                print(f"CUDA initialization failed: {str(cuda_e)}")
                print("Falling back to CPU model...")
                # 如果 CUDA 失败，回退到 CPU 多线程模式
                self.model = WhisperModel(
                    model_path,
                    device="cpu",
                    compute_type="int8",
                    local_files_only=True,
                    cpu_threads=8,           # CPU 线程数
                    num_workers=4            # 并行工作进程数
                )
                print("CPU model initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Whisper model: {str(e)}")
            raise
        
    def process_segment(self, segment):
        """处理单个语音片段"""
        text = segment.text.strip()
        if text:
            return {
                'text': text,
                'start': segment.start,
                'end': segment.end
            }
        return None

    def transcribe_video(self, video_path):
        """从视频中提取语音文本，使用多线程处理"""
        try:
            print(f"Starting transcription of file: {video_path}")
            if not os.path.exists(video_path):
                raise Exception(f"文件不存在: {video_path}")
                
            print("Running whisper transcription with parallel processing...")
            segments, info = self.model.transcribe(
                video_path,
                language="zh",
                task="transcribe",
                beam_size=5,
                best_of=5,              # 增加候选数量
                temperature=0.0,         # 降低随机性
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    threshold=0.3
                ),
                word_timestamps=True     # 启用词级时间戳
            )
            print(f"Transcription info: {info}")
            
            # 使用线程池并行处理结果
            transcriptions = []
            with ThreadPoolExecutor(max_workers=8) as executor:  # 增加工作线程数
                # 提交所有片段处理任务
                future_to_segment = {
                    executor.submit(self.process_segment, segment): segment 
                    for segment in segments
                }
                
                # 并行收集处理结果
                for future in as_completed(future_to_segment):
                    result = future.result()
                    if result:
                        transcriptions.append(result)
            
            # 按时间顺序排序
            transcriptions.sort(key=lambda x: x['start'])
            
            print(f"Transcription completed, found {len(transcriptions)} segments")
            return transcriptions
            
        except Exception as e:
            print(f"Error in transcribe_video: {str(e)}")
            print(f"File path: {video_path}")
            raise Exception(f"语音识别失败: {str(e)}") 