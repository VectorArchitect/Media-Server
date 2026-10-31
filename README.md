# Media Server

A lightweight, self-hosted media server built with Python. Browse and stream local images, GIFs, and videos through a responsive web gallery on your laptop or other devices on the same trusted network.

## Features

- Responsive media gallery with search and type filters
- Recursive media scanning, including nested folders
- Folder browser for navigating the collection
- Image and GIF viewer
- Browser-based video player with byte-range streaming for seeking
- Temporary playback queue and recommendations
- Hover zoom interactions and mobile-friendly layout
- No third-party Python dependencies

## Supported formats

**Video:** MP4, MKV, AVI, MOV, WEBM, M4V, MPG, MPEG, 3GP

**Images:** JPG, JPEG, PNG, GIF, WEBP, BMP, AVIF, TIFF, TIF

Browser playback support varies by browser and codec. A file extension being listed does not guarantee every browser can decode that file.

## Requirements

- Python 3.8 or later (standard library only)
- A folder containing the media you want to serve
- A modern web browser

## Setup

1. Download or clone this repository.
2. Open `media_server.py`.
3. Set `MEDIA_DIR` to the folder containing your media:

   ```python
   MEDIA_DIR = r"C:\Users\YourName\Videos"
   ```

   Replace the example with your actual folder path. Keep the `r` prefix for Windows paths.
4. Optionally change `HOST` or `PORT`. The default port is `6789`.
5. Start the server:

   ```powershell
   python media_server.py
   ```

6. Open [http://127.0.0.1:6789](http://127.0.0.1:6789) on the same computer.

The server exits with an error if the configured media folder does not exist.

## Access from another device on your local network

1. Connect the computer running the server and the other device to the same trusted Wi-Fi/LAN.
2. On Windows, run `ipconfig` and find the computer's IPv4 address.
3. On the other device, open `http://YOUR-LAPTOP-IP:6789`, replacing the placeholder with that IPv4 address.
4. Allow Python through Windows Firewall on private networks if Windows asks.

The server binds to `0.0.0.0` by default so it can accept LAN connections.

## Stop the server

Press `Ctrl+C` in the terminal where the server is running.

## Project files

- `media_server.py` — Python server and embedded web interface
- `Server.txt` — quick start and LAN access notes

## Security and privacy

This project is intended for use on a trusted local network. It does **not** implement user authentication, HTTPS, or access controls. Anyone who can reach the server may be able to browse and retrieve files from the configured media directory. Do not expose it directly to the public internet or forward its port on your router.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
