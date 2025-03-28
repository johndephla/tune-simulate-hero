
# Suno.ai Automation Bot

This application automates the process of generating music on Suno.ai by simulating human-like interactions with the website. It provides a FastAPI endpoint to generate songs programmatically.

## Features

- Automated login to Suno.ai
- Human-like browser interaction (realistic mouse movements and typing)
- Song generation from text prompts
- Song download capability
- RESTful API for integration with other applications

## Requirements

- Windows 10 or newer
- Python 3.7+
- Google Chrome browser
- Suno.ai account

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

4. Edit the `.env` file with your Suno.ai credentials:

```
EMAIL=your-email@example.com
PASSWORD=your-password
```

## Usage

### Running the application

```bash
python main.py
```

This will start the automation bot and the FastAPI server on http://127.0.0.1:8000

### Using the API

To generate a song, send a POST request to the `/generate` endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/generate" -H "Content-Type: application/json" -d '{"prompt": "happy techno song about robots", "download": true}'
```

The response will include the URL of the generated song and the file path if download was requested:

```json
{
  "success": true,
  "url": "https://suno.ai/song/abc123",
  "prompt": "happy techno song about robots",
  "file_path": "C:\\Users\\YourName\\Downloads\\suno_song_123.mp3"
}
```

## API Endpoints

- `GET /` - Check if the API is running
- `POST /generate` - Generate a new song
  - Request body:
    - `prompt` (string, required) - The text prompt for song generation
    - `download` (boolean, optional) - Whether to download the generated song
- `GET /status` - Check the current status of the automation

## Notes

- The application simulates human-like behavior to avoid detection as a bot
- Suno.ai may have usage limits or anti-automation measures that could affect performance
- This tool should be used responsibly and in accordance with Suno.ai's terms of service

## Troubleshooting

- If the browser fails to start, ensure Chrome is installed and updated
- If login fails, verify your credentials in the `.env` file
- Check the `suno_automation.log` file for detailed logs

## License

This project is for educational purposes only. Use responsibly.
