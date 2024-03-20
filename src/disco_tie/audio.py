import math
import threading
import traceback
import time

import pyaudio
import numpy as np


class AudioSampler:
    def __init__(self, device_index, sample_rate=44100, chunk_size=1024):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._current_sample = np.ndarray(0)
        self._last_sample = None
        self.thread_lock = threading.Lock()

        self._running = True
        self.pya = pyaudio.PyAudio()
        try:
            self.audio_stream = self.pya.open(
                    format=pyaudio.paInt16,  # Format of the audio data (16-bit integer)
                    channels=1,  # Number of audio channels (1 for mono, 2 for stereo)
                    rate=self.sample_rate,  # Sampling rate in Hz
                    input=True,  # Open stream for input
                    frames_per_buffer=self.chunk_size,  # Number of frames per buffer (chunk size)
                    input_device_index=self.device_index,
            )
        except Exception as e:
            print(traceback.print_tb(e))
        self.audio_thread = threading.Thread(target=self._audio_thread)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def stop(self):
        self._running = False
        self.audio_thread.join()
        # Stop and close the audio stream
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        # Terminate PyAudio object
        self.pya.terminate()

    def _read_audio_stream(self):
        try:
            return self.audio_stream.read(self.chunk_size)
        except OSError as e:
            return
    def _audio_thread(self):
        while self._running:
            data = self._read_audio_stream()
            if data is None:
                return
            # Convert binary data to numpy array of int16 data type
            output_data = np.frombuffer(data, dtype=np.int16)
            with self.thread_lock:
                self._current_sample = output_data

    def read(self):
        with self.thread_lock:
            output = self._current_sample[:]
        if output.size == 0:
            return None

        if output is not None:
            self._last_sample = output
        return self._last_sample


def plot_audio_data(data, sample_rate):
    # Calculate the time axis
    time_axis = np.arange(len(data)) / sample_rate

    # Plot the audio data
    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, data)
    plt.title('Audio Data from Microphone')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()


def calculate_fft(data, sample_rate, lower_freq=20, upper_freq=20000):
    # Perform FFT
    fft_result = np.fft.fft(data)

    # Calculate the number of samples
    n_samples = len(data)

    # Calculate the frequency resolution
    freq_resolution = sample_rate / n_samples

    # Calculate the lower and upper bin indices based on the specified frequencies
    lower_bin = int(lower_freq / freq_resolution)
    upper_bin = int(upper_freq / freq_resolution)

    # Extract the frequency components within the specified range
    fft_result = fft_result[lower_bin:upper_bin]

    # Calculate the magnitude spectrum (absolute values)
    magnitude_spectrum = np.abs(fft_result)

    return magnitude_spectrum


def get_frequency_buckets(fft_data, num_buckets):
    buckets = [[] for _ in range(num_buckets)]
    for i, data in enumerate(fft_data):
        position = math.log(i + 1, len(fft_data))
        bucket_n = int(min(num_buckets - 1, position * num_buckets))
        buckets[bucket_n].append(data)

    average_buckets = []
    for bucket in buckets:
        if not bucket:
            continue
        average_buckets.append(sum(bucket) / len(bucket))
    # average_buckets = [sum(b) / len(b) for b in buckets if b]
    return average_buckets


# Example usage:
if __name__ == "__main__":
    def ascii_graph(data, display_values=True, multiplier=1, min_height=10):
        max_value = int(max(max(data) * multiplier, min_height))
        num_bars = len(data)

        # Iterate through each row from the top to bottom
        for row in range(max_value, 0, -1):
            # Print each column for the current row
            for col in range(num_bars):
                value = int(data[col] * multiplier)
                if value >= row:
                    print("#", end="")  # Print '#' if the value at this index is greater or equal to the current row
                else:
                    print(" ", end="")  # Print a space if the value at this index is less than the current row
            print()  # Move to the next row after printing all columns

        # Print the horizontal axis (index)
        print("")
        print("-" * num_bars)
        if display_values:
            for i in range(num_bars):
                print(i, end=" ")
        print()  # Move to the next line after printing the horizontal axis


    current_max = 0
    # Create a generator for reading microphone data
    sampler = AudioSampler(3, 44100, 1024)
    # Loop indefinitely to read microphone data and perform FFT
    last_time = time.time()
    while True:
        audio_data = sampler.read()
        if audio_data is None:
            continue
        current_max -= 10
        # Calculate FFT for the current chunk of audio data
        fft_data = calculate_fft(audio_data, 44100, 50, 6000)
        bucket_data = get_frequency_buckets(fft_data, 20)
        scaled = [(math.log(b, 1.1)) for b in bucket_data]
        # Plot summarized FFT data
        modified_spec = [max(0, m - 1000) ** 0.5 for m in bucket_data]
        current_max = max(current_max, max(modified_spec))
        # plot_bar_graph(modified_spec, 44100, 50, 6000, current_max)
        ascii_graph(modified_spec, display_values=False, multiplier=0.02, min_height=max(10, current_max * 0.01))
        print(f"time: {time.time() - last_time:.4f}")
        last_time = time.time()

    print("stopping sampler")
    sampler.stop()
