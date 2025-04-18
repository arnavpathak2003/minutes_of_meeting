# Minutes of Meeting Generator

This project is designed to automate the process of generating minutes of meetings from audio files. It provides a comprehensive solution that includes sentiment analysis, action item extraction, and email delivery of the meeting minutes.

## Features

- **Audio to Text Conversion**: Convert meeting audio files (e.g., `EarningsCall.wav`) into text.
- **Minutes Generation**: Summarize the meeting transcript into a concise summary, extract action items, and analyze sentiment.
- **Email Delivery**: Send the generated minutes via email to specified recipients.
- **Environment Reproducibility**: Utilizes `uv` for environment setup, combining the reliability of `conda` and the speed of `pip`.

## Setup Instructions

### Environment Setup

1. **Install UV**: Ensure you have `uv` installed on your system. You can find installation instructions on the [UV official website](https://example.com).

2. **Create Environment**: Use the following command to create the environment:

   ```bash
   uv create
   ```

3. **Activate Environment**: Activate the environment using:

   ```bash
   uv activate
   ```

4. **Install Dependencies**: Install the necessary dependencies:
   ```bash
   uv install
   ```

### Configuration

- **Email Configuration**: Update the `.env` file with your email credentials. You need to specify the sender and receiver Gmail IDs.

- **API Key**: If you wish to use Google's Gemini for better results, enter the API key in the `.env` file. Alternatively, if you prefer using Phi4, ensure it is run using Ollama.

### Running the Project

1. **Process Audio File**: Place your audio file (e.g., `EarningsCall.wav`) in the root directory.

2. **Generate Minutes**: Run the script to process the audio and generate the minutes:

   ```bash
   python src/main.py
   ```

3. **Send Email**: The script will automatically send the generated minutes to the specified email addresses.

## Caveats

- **Qwen2.5 Limitation**: Initially, Qwen2.5 was considered, but it faced issues with file creation. Therefore, Google's Gemini is recommended for better performance.
- **Environment Management**: `uv` is preferred over `conda` and `pip` for its balance of speed and reliability.

## Sample Files

- `EarningsCall.wav`: A sample audio file included for testing purposes.
