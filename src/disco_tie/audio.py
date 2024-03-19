import math

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time


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


def read_microphone(sample_rate=44100, chunk_size=1024):
    # Initialize PyAudio object
    audio = pyaudio.PyAudio()

    # Open audio stream for microphone input
    stream = audio.open(
            format=pyaudio.paInt16,  # Format of the audio data (16-bit integer)
            channels=1,  # Number of audio channels (1 for mono, 2 for stereo)
            rate=sample_rate,  # Sampling rate in Hz
            input=True,  # Open stream for input
            frames_per_buffer=chunk_size,  # Number of frames per buffer (chunk size)
            input_device_index=3
    )

    while True:
        try:
            # Read audio data from the stream
            data = stream.read(chunk_size)
            # Convert binary data to numpy array of int16 data type
            yield np.frombuffer(data, dtype=np.int16)
            time.sleep(0.02)
        except KeyboardInterrupt:
            break

    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    # Terminate PyAudio object
    audio.terminate()


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

def get_frequency_buckets(fft_data, num_buckets, lower_freq=20, upper_freq=20000):
    buckets = [[] for _ in range(num_buckets)]
    for i, data in enumerate(fft_data):
        position = math.log(i+1, len(fft_data))
        bucket_n = int(min(num_buckets-1, position * num_buckets))
        buckets[bucket_n].append(data)

    average_buckets = []
    for bucket in buckets:
        if not bucket:
            continue
        average_buckets.append(sum(bucket) / len(bucket))
    #average_buckets = [sum(b) / len(b) for b in buckets if b]
    return average_buckets


def plot_bar_graph(magnitude_spectrum, sample_rate, lower_freq=20, upper_freq=20000):
    # Calculate frequency bins
    freq_bins = np.linspace(lower_freq, upper_freq, len(magnitude_spectrum))

    # Clear the current figure to update it with new data
    plt.clf()

    # Plot bar graph
    plt.bar(freq_bins, magnitude_spectrum, width=(upper_freq - lower_freq) / len(magnitude_spectrum), align='edge')
    plt.title('FFT Magnitude Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.ylim(0, 100000)

    # Pause briefly to update the plot
    plt.pause(0.01)

# Example usage:
if __name__ == "__main__":
    # Create a generator for reading microphone data
    mic_reader = read_microphone()
    # Loop indefinitely to read microphone data and perform FFT
    last_time = time.time()
    for audio_data in mic_reader:
        #print(f"get_time = {time.time() - last_time}")
        # Calculate FFT for the current chunk of audio data
        fft_data = calculate_fft(audio_data, 44100, 50, 6000)
        bucket_data = get_frequency_buckets(fft_data, 10)
        #bucket_data = [i ** 5.5 for i in range(10)]
        print(max(bucket_data))
        print("\n\n")
        scaled = [(b**0.7/ 100) for b in bucket_data]
        print("\n".join(["|" * int(s) for s in scaled]))
        print(max(scaled))
        #time.sleep(0.001)
        # Plot summarized FFT data
        #plot_bar_graph(bucket_data, 44100, 50, 6000)
        last_time = time.time()
