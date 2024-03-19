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

def read_microphone(sample_rate=44100, chunk_size=2048):
    # Initialize PyAudio object
    audio = pyaudio.PyAudio()

    # Open audio stream for microphone input
    stream = audio.open(
        format=pyaudio.paInt16,    # Format of the audio data (16-bit integer)
        channels=1,                 # Number of audio channels (1 for mono, 2 for stereo)
        rate=sample_rate,           # Sampling rate in Hz
        input=True,                 # Open stream for input
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
    # Calculate the number of samples
    n_samples = len(data)

    # Calculate the frequency resolution
    freq_resolution = sample_rate / n_samples

    # Calculate the lower and upper bin indices based on the specified frequencies
    lower_bin = int(lower_freq / freq_resolution)
    upper_bin = int(upper_freq / freq_resolution)

    # Perform FFT
    fft_result = np.fft.fft(data)

    # Extract the frequency components within the specified range
    fft_result = fft_result[lower_bin:upper_bin]
    # Only keep positive frequencies
    fft_result = fft_result[:len(fft_result) // 2]
    return fft_result

# Example usage:
if __name__ == "__main__":
    # Create a generator for reading microphone data
    mic_reader = read_microphone()
    # Loop indefinitely to read microphone data and perform FFT
    for audio_data in mic_reader:
        # Calculate FFT for the current chunk of audio data
        fft_data = calculate_fft(audio_data, 44100, 50, 6000)
        # Process FFT data as needed
        buckets = 10
        bucket_size = len(fft_data) / buckets
        bucket_data = []
        for i in range(buckets):
            bucket_range = range(int(i * bucket_size), int((i+1) * bucket_size))
            bucket_total = 0
            for j in bucket_range:
                if j < len(fft_data):
                    bucket_total += fft_data[j]
            bucket_data.append(bucket_total)
        print("\n\n")
        print("\n".join([str(total* 0.01) for total in bucket_data]))
