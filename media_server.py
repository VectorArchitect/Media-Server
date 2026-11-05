
import os
import json
import re
import mimetypes
from urllib.parse import unquote, urlsplit
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ==================================================
# CONFIGURATION
# ==================================================

MEDIA_DIR = r"MediaPath"
HOST = "0.0.0.0"
PORT = 6789
# portNumbers Can be:
# - 5000
# - 6789
# - 8000
# - 8080
# - 9000
# - 50000

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov",
    ".webm", ".m4v", ".mpg", ".mpeg", ".3gp"
}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".webp", ".bmp", ".avif", ".tiff", ".tif"
}


# ==================================================
# WEB PAGE
# ==================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Media</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #101010;
    color: white;
    font-family: Arial, sans-serif;
}

/* HEADER */

header {
    padding: 18px 22px;
    background: #181818;
    position: sticky;
    top: 0;
    z-index: 5;
    border-bottom: 1px solid #303030;
}

header h2 {
    margin: 0 0 14px;
}

#search {
    width: 100%;
    max-width: 500px;
    padding: 12px 15px;
    border: 1px solid #444;
    border-radius: 25px;
    background: #252525;
    color: white;
    font-size: 15px;
    outline: none;
}

nav {
    display: flex;
    gap: 10px;
    padding-top: 14px;
    flex-wrap: wrap;
}

nav button {
    border: none;
    padding: 9px 17px;
    border-radius: 20px;
    background: #303030;
    color: white;
    cursor: pointer;
}

nav button.active {
    background: white;
    color: black;
}

/* GALLERY */

main {
    padding: 20px;
}

.section-title {
    margin: 10px 0 18px;
    font-size: 21px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fill,
        minmax(155px, 1fr)
    );
    gap: 17px;
    margin-bottom: 35px;
}

.card {
    min-width: 0;
    cursor: pointer;
}

/* GALLERY VIEW */
.card {
    overflow: hidden;
    border-radius: 10px;
}

.card img,
.card video {
    display: block;
    width: 100%;
    height: 218px;
    box-sizing: border-box;
    object-fit: contain;
    padding: 0;
    background: #181818;
    border-radius: 10px;
    transition: transform 0.3s ease;
    transform-origin: center;
}

.card img:hover,
.card video:hover {
    transform: scale(1.08);
}

.card p {
    margin: 9px 2px;
    font-size: 13px;
    color: #ddd;
    overflow-wrap: anywhere;
    line-height: 1.4;
}

.empty {
    color: #999;
    padding: 15px 0;
}

/* FOLDER BROWSER */
.folder-path {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 7px;
    margin: 0 0 14px;
    color: #bbb;
    font-size: 13px;
}
.folder-path button {
    border: 1px solid #444;
    border-radius: 16px;
    padding: 6px 11px;
    background: #242424;
    color: #eee;
}
.folder-card {
    min-height: 112px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    gap: 8px;
    padding: 15px;
    border: 1px solid #333;
    border-radius: 12px;
    background: #1b1b1b;
    cursor: pointer;
}
.folder-card .folder-icon { font-size: 30px; }
.folder-card strong { overflow-wrap: anywhere; }
.folder-card small { color: #999; }

/* CINEMATIC VIEWER */

#viewer {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 20;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    padding: 25px;
    background:
        radial-gradient(
            ellipse at top,
            #252b3d 0%,
            #101116 50%,
            #050506 100%
        );
    backdrop-filter: blur(18px);
}

#viewerContent {
    width: min(1100px, 100%);
    max-height: 82vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 18px;
    background: #080808;
    box-shadow:
        0 25px 90px rgba(0,0,0,.8),
        0 0 35px rgba(100,130,255,.12);
}

#viewerContent > img {
    display: block;
    max-width: 100%;
    max-height: 82vh;
    object-fit: contain;
}

#viewerTitle {
    margin-top: 18px;
    max-width: 90%;
    padding: 10px 20px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 30px;
    background: rgba(255,255,255,.07);
    color: #f3f3f3;
    font-size: 14px;
    text-align: center;
    overflow-wrap: anywhere;
}

#close {
    position: absolute;
    top: 22px;
    right: 25px;
    width: 46px;
    height: 46px;
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 50%;
    background: rgba(255,255,255,.09);
    color: white;
    font-size: 27px;
    cursor: pointer;
    transition: .2s ease;
}

#close:hover {
    background: #e63946;
    transform: rotate(90deg);
}

/* MOBILE */

@media (max-width: 600px) {
    main {
        padding: 13px;
    }

    .grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }

    .card img,
    .card video {
        height: 210px;
        padding: 0;
    }

    #viewer {
        padding: 10px;
    }

     /* MOBILE VIEWER */
    #viewerContent {
        border-radius: 12px;
    }

    #viewerContent > img {
        max-height: 75vh;
        padding: 30px 10px;
    }

    #close {
        top: 12px;
        right: 12px;
    }

    .player-controls {
        gap: 7px;
        padding: 10px;
    }

    .player-controls button {
        padding: 9px 10px;
    }

    #volumeBar {
        width: 55px;
    }

    #timeDisplay {
        font-size: 11px;
    }
}

/* PLAYER ANIMATION */

#viewer[style*="flex"] #viewerContent {
    animation: playerEnter .25s ease-out;
}

@keyframes playerEnter {
    from {
        opacity: 0;
        transform: scale(.96) translateY(10px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

/* MOBILE-FIRST PLAYER */
#viewer {
    padding: 0;
    justify-content: flex-start;
    overflow-y: auto;
    background: #050505;
}
#viewerContent {
    width: 100%;
    max-width: 1100px;
    max-height: none;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    overflow: visible;
    flex: 0 0 auto;
}
#viewerTitle {
    margin: 0;
    padding: 9px 12px;
    max-width: 100%;
    width: 100%;
    border: 0;
    border-radius: 0;
    background: #111;
    text-align: left;
    font-size: 13px;
}
#close {
    position: fixed;
    z-index: 30;
    top: 8px;
    right: 8px;
    width: 34px;
    height: 34px;
    font-size: 22px;
    background: rgba(0,0,0,.65);
    border: 0;
}
/* LAPTOP VIEWER */
#viewerContent > img {
    max-width: 100%;
    max-height: 88dvh;
    object-fit: contain;
    padding: 30px 10px;
}
.player-extra {
    width: 100%;
    max-width: 1100px;
    padding: 10px 12px 24px;
    background: #0b0b0b;
}
.player-extra h3 {
    margin: 12px 0 9px;
    font-size: 14px;
}
.queue-actions { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.queue-actions button, .mini-action {
    color:#eee; background:#242424; border:1px solid #393939;
    border-radius:7px; padding:7px 10px; font-size:12px;
}
.queue-list { display:flex; gap:8px; overflow-x:auto; padding:3px 0 10px; }
.queue-item {
    flex:0 0 145px; background:#191919; border-radius:8px;
    padding:8px; font-size:11px; overflow-wrap:anywhere;
}
.queue-item button { margin-top:6px; margin-right:4px; }
.recommendations {
    display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:9px;
}
.recommend-card { min-width:0; cursor:pointer; }
.recommend-card img, .recommend-card video {
    width:100%; height:72px; object-fit:cover; background:#222; border-radius:6px;
}
.recommend-card p { font-size:11px; color:#ddd; margin:5px 0; overflow-wrap:anywhere; }
@media (max-width:600px) {
    #viewer { justify-content:flex-start; }
    #viewerContent { width:100%; }
    .custom-player video {
        max-height: 56dvh;
        width:100%;
        object-fit:contain;
    }
    .player-controls { gap:3px; padding:4px 5px; flex-wrap:nowrap; }
    .player-controls button { padding:5px 5px; font-size:14px; flex:0 0 auto; }
    #seekBar { flex:1 1 60px; min-width:45px; height:30px; }
    #timeDisplay { flex:0 0 auto; }
    #timeDisplay { font-size:9px; }
    #speedSelect { max-width:78px; min-height:34px; font-size:11px; padding:5px 3px; }
    .custom-player:fullscreen .player-controls { gap:6px; flex-wrap:nowrap; }
    .custom-player:fullscreen #speedSelect { max-width:86px; min-height:40px; font-size:12px; }
    .custom-player:fullscreen #timeDisplay { font-size:10px; }
    .player-extra { padding:8px 10px 20px; }
    .recommendations { grid-template-columns:repeat(3,minmax(0,1fr)); }
}
@media (orientation:landscape) and (max-width:900px) {
    .custom-player video { max-height: calc(100dvh - 45px); }
    #viewerTitle, .player-extra { display:none; }
}


.queue-heading { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.queue-heading h3 { margin-bottom:8px; }
#queueStatus { color:#999; font-size:11px; }
.queue-now {
    display:flex; align-items:center; gap:9px; padding:9px;
    margin-bottom:8px; background:#202020; border-radius:8px;
    font-size:12px; overflow-wrap:anywhere;
}
.queue-now strong { color:#fff; }
.queue-item { flex:0 0 160px; }
.queue-item.current { outline:1px solid #777; background:#252525; }
.queue-item .queue-position { color:#999; font-size:10px; margin-bottom:4px; }
.queue-item button { margin-top:7px; margin-right:3px; }
#seekBar {
    position: relative;
    display: block;
    flex: 1 1 90px;
    width: 100%;
    min-width: 55px;
    height: 34px;
    margin: 0;
    padding: 0;
    cursor: pointer;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
    outline: none;
}

</style>
</head>

<body>

<header>
    <h2>▶ My Media</h2>

    <input
        id="search"
        type="search"
        placeholder="Search videos, images and GIFs..."
    >

    <nav>
        <button class="active" data-filter="all">All</button>
        <button data-filter="videos">Videos</button>
        <button data-filter="images">Images</button>
        <button data-filter="gifs">GIFs</button>
        <button id="foldersToggle" type="button">📁 View folders</button>
    </nav>
</header>

<main>
    <h3 class="section-title" id="heading">All Media</h3>

    <div id="folderBrowser" hidden>
        <div id="folderPath" class="folder-path"></div>
        <div id="folderGrid" class="grid"></div>
    </div>

    <div id="gallery" class="grid"></div>

    <p id="empty" class="empty" hidden>
        No media found.
    </p>
</main>

<div id="viewer">
    <button id="close" aria-label="Close">&times;</button>

    <div id="viewerContent"></div>

    <div id="viewerTitle"></div>
<div id="playerExtra" class="player-extra" hidden>
  <div class="queue-actions"><button id="addQueueBtn">＋ Start queue with this video</button>  <button id="clearQueueBtn">Clear queue</button></div>
  <div class="queue-heading"><h3>Up next</h3><span id="queueStatus"></span></div>
  <div id="queueNowPlaying" class="queue-now"></div>
  <div id="queueList" class="queue-list"></div>
  <h3>Recommended from your collection</h3><div id="recommendations" class="recommendations"></div>
</div>
</div>

<script>

/* ==================================================
   GLOBAL STATE
================================================== */

let allMedia = [];
let currentFilter = "all";
let folderMode = false;
let currentFolder = "";

const gallery = document.getElementById("gallery");
const folderBrowser = document.getElementById("folderBrowser");
const folderGrid = document.getElementById("folderGrid");
const folderPath = document.getElementById("folderPath");
const foldersToggle = document.getElementById("foldersToggle");
const search = document.getElementById("search");
const empty = document.getElementById("empty");


/* ==================================================
   MEDIA URL
================================================== */

function mediaURL(path, type) {
    const encoded = path.split("/")
        .map(part => encodeURIComponent(part))
        .join("/");

    return "/" + type + "/" + encoded;
}


/* ==================================================
   VIDEO PLAYER
================================================== */


let currentItem = null;
let temporaryQueue = [];
let queueIndex = -1;
let currentVideo = null;
let currentPlayer = null;
let savedPlaybackRate = 1;
let holdTimer = null;
let holdActive = false;
let holdPointer = null;

function openViewer(item) {
    currentItem = item;
    const viewer = document.getElementById("viewer");
    const content = document.getElementById("viewerContent");
    const title = document.getElementById("viewerTitle");
    const extra = document.getElementById("playerExtra");
    content.innerHTML = "";
    extra.hidden = item.type !== "video";

    if (item.type === "video") {
        buildVideoPlayer(item);
        renderRecommendations(item);
        renderQueue();
    } else {
        const img = document.createElement("img");
        img.src = mediaURL(item.path, "image");
        img.alt = item.name;
        content.appendChild(img);
    }
    title.textContent = item.name;
    viewer.style.display = "flex";
}

function buildVideoPlayer(item) {
    const content = document.getElementById("viewerContent");

    // Stop and dispose of the previous video before loading another queue item.
    const oldVideo = content.querySelector("video");
    if (oldVideo) {
        oldVideo.pause();
        oldVideo.removeAttribute("src");
        oldVideo.load();
    }

    const video = document.createElement("video");
    video.id = "mainVideo";
    video.src = mediaURL(item.path, "video");
    video.controls = true;       // Browser-native controls
    video.autoplay = true;
    video.playsInline = true;
    video.preload = "metadata";
    video.style.display = "block";
    video.style.width = "100%";
    video.style.maxHeight = "72vh";
    video.style.objectFit = "contain";
    video.style.background = "#000";

    content.replaceChildren(video);
    currentVideo = video;
    currentPlayer = video;

    // Preserve queue playback behaviour without custom playback controls.
    video.addEventListener("ended", () => {
        if (temporaryQueue.length && queueIndex >= 0 &&
            queueIndex < temporaryQueue.length - 1) {
            queueIndex++;
            playQueueItem();
        } else {
            // If there is no next queued item, replay the current video.
            video.currentTime = 0;
            video.play().catch(() => {});
        }
    });

    video.play().catch(() => {});
}

function addToQueue(item, playNext = false) {
    // Like a video-site queue: include the current video as the queue's
    // playing item the first time another video is queued.
    if (queueIndex < 0 && currentItem?.type === "video") {
        temporaryQueue = [currentItem];
        queueIndex = 0;
    }

    const existingIndex = temporaryQueue.findIndex(x => x.path === item.path);
    if (existingIndex !== -1) {
        renderQueue();
        return;
    }

    if (playNext && queueIndex >= 0) {
        temporaryQueue.splice(queueIndex + 1, 0, item);
    } else {
        temporaryQueue.push(item);
    }
    renderQueue();
}

function renderQueue() {
    const list = document.getElementById("queueList");
    const status = document.getElementById("queueStatus");
    const now = document.getElementById("queueNowPlaying");
    if (!list || !status || !now) return;

    list.innerHTML = "";
    const current = queueIndex >= 0 ? temporaryQueue[queueIndex] : currentItem;
    now.innerHTML = "";
    if (current) {
        const label = document.createElement("span");
        label.innerHTML = "<strong>▶ Now playing:</strong> ";
        const name = document.createElement("span");
        name.textContent = current.name;
        now.append(label, name);
    } else {
        now.textContent = "Nothing playing";
    }

    const upcoming = temporaryQueue
        .map((item, index) => ({item, index}))
        .filter(entry => entry.index > queueIndex);

    status.textContent = `${upcoming.length} up next`;
    if (!upcoming.length) {
        const note = document.createElement("div");
        note.className = "queue-item";
        note.textContent = "Your queue is empty. Add videos from recommendations.";
        list.appendChild(note);
        return;
    }

    upcoming.forEach(({item, index}, position) => {
        const card = document.createElement("div");
        card.className = "queue-item";
        const order = document.createElement("div");
        order.className = "queue-position";
        order.textContent = `UP NEXT · ${position + 1}`;
        const label = document.createElement("div");
        label.textContent = item.name;

        const play = document.createElement("button");
        play.className = "mini-action";
        play.textContent = "Play";
        play.onclick = () => {
            queueIndex = index;
            playQueueItem();
        };

        const up = document.createElement("button");
        up.className = "mini-action";
        up.textContent = "↑";
        up.title = "Move earlier";
        up.disabled = index <= queueIndex + 1;
        up.onclick = () => {
            [temporaryQueue[index - 1], temporaryQueue[index]] =
                [temporaryQueue[index], temporaryQueue[index - 1]];
            renderQueue();
        };

        const remove = document.createElement("button");
        remove.className = "mini-action";
        remove.textContent = "Remove";
        remove.onclick = () => {
            temporaryQueue.splice(index, 1);
            renderQueue();
        };

        card.append(order, label, play, up, remove);
        list.appendChild(card);
    });
}

function playQueueItem() {
    if (!temporaryQueue.length || queueIndex < 0 || queueIndex >= temporaryQueue.length) return;
    const item = temporaryQueue[queueIndex];
    currentItem = item;
    document.getElementById("viewerTitle").textContent = item.name;
    buildVideoPlayer(item);
    renderRecommendations(item);
    renderQueue();
}

function renderRecommendations(item) {
    const box = document.getElementById("recommendations");
    box.innerHTML = "";
    const videos = allMedia.filter(x => x.type === "video" && x.path !== item.path);
    const sameFolder = videos.filter(x => x.path.includes("/") &&
        x.path.substring(0, x.path.lastIndexOf("/")) ===
        (item.path.includes("/") ? item.path.substring(0, item.path.lastIndexOf("/")) : ""));
    const picks = [...sameFolder, ...videos.filter(x => !sameFolder.includes(x))].slice(0, 9);
    picks.forEach(rec => {
        const card = document.createElement("div");
        card.className = "recommend-card";
        const preview = document.createElement("video");
        preview.src = mediaURL(rec.path, "video");
        preview.preload = "metadata";
        preview.muted = true;
        preview.playsInline = true;
        const name = document.createElement("p");
        name.textContent = rec.name;
        const actions = document.createElement("div");
        const play = document.createElement("button");
        play.className = "mini-action";
        play.textContent = "Play";
        play.onclick = event => { event.stopPropagation(); openViewer(rec); };
        const add = document.createElement("button");
        add.className = "mini-action";
        add.textContent = "+ Queue";
        add.onclick = event => { event.stopPropagation(); addToQueue(rec); };
        actions.append(play, add);
        card.append(preview, name, actions);
        card.onclick = () => openViewer(rec);
        box.appendChild(card);
    });
    if (!picks.length) box.textContent = "No other videos found.";
}

document.getElementById("addQueueBtn").onclick = () => {
    if (currentItem?.type === "video") {
        if (queueIndex < 0) {
            temporaryQueue = [currentItem];
            queueIndex = 0;
            renderQueue();
        } else {
            renderQueue();
        }
    }
};
document.getElementById("clearQueueBtn").onclick = () => {
    temporaryQueue = [];
    queueIndex = -1;
    renderQueue();
};



/* ==================================================
   CLOSE VIEWER
================================================== */

function closeViewer() {

    const viewer = document.getElementById("viewer");
    const content = document.getElementById("viewerContent");

    const video = content.querySelector("video");

    if (video) {
        video.pause();
        video.removeAttribute("src");
        video.load();
    }

    if (document.fullscreenElement) {
        document.exitFullscreen?.().catch(() => {});
    }

    content.innerHTML = "";
    currentVideo = null;
    currentPlayer = null;
    viewer.style.display = "none";
}

document.getElementById("close").onclick = closeViewer;

document.getElementById("viewer").addEventListener("click", e => {
    if (e.target.id === "viewer") {
        closeViewer();
    }
});

document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
        closeViewer();
    }
});


/* ==================================================
   GALLERY
================================================== */

function folderName(path) {
    return path.split("/").filter(Boolean).pop() || "Root";
}

function renderFolderBrowser() {
    const prefix = currentFolder ? currentFolder + "/" : "";
    const directFolders = new Map();
    const directFiles = [];

    allMedia.forEach(item => {
        const path = item.path || "";
        if (!path.startsWith(prefix)) return;

        const remainder = path.slice(prefix.length);
        const slash = remainder.indexOf("/");

        if (slash >= 0) {
            // At the root, show folders only. Inside a folder, do not show nested folders.
            // This prevents media from other folders appearing in the current folder view.
            if (!currentFolder) {
                const name = remainder.slice(0, slash);
                const folderPathValue = prefix + name;
                if (!directFolders.has(folderPathValue)) {
                    directFolders.set(folderPathValue, 0);
                }
                directFolders.set(folderPathValue, directFolders.get(folderPathValue) + 1);
            }
        } else if (currentFolder) {
            // Only files directly inside the selected folder are displayed.
            directFiles.push(item);
        }
    });

    folderPath.innerHTML = "";
    const rootButton = document.createElement("button");
    rootButton.textContent = "All folders";
    rootButton.onclick = () => { currentFolder = ""; renderFolderBrowser(); };
    folderPath.appendChild(rootButton);

    if (currentFolder) {
        const crumb = document.createElement("button");
        crumb.textContent = folderName(currentFolder);
        crumb.disabled = true;
        folderPath.appendChild(crumb);
    }

    folderGrid.innerHTML = "";

    if (!currentFolder) {
        [...directFolders.entries()]
            .sort((a, b) => a[0].localeCompare(b[0]))
            .forEach(([path, count]) => {
                const card = document.createElement("div");
                card.className = "folder-card";

                const icon = document.createElement("span");
                icon.className = "folder-icon";
                icon.textContent = "📁";

                const name = document.createElement("strong");
                name.textContent = folderName(path);

                const detail = document.createElement("small");
                detail.textContent = `${count} media item${count === 1 ? "" : "s"} inside`;

                card.append(icon, name, detail);
                card.onclick = () => {
                    currentFolder = path;
                    renderFolderBrowser();
                };
                folderGrid.appendChild(card);
            });

        if (!directFolders.size) {
            const note = document.createElement("p");
            note.className = "empty";
            note.textContent = "No folders found.";
            folderGrid.appendChild(note);
        }
        return;
    }

    directFiles.forEach(item => {
        const card = document.createElement("div");
        card.className = "card";

        if (item.type === "video") {
            const video = document.createElement("video");
            video.src = mediaURL(item.path, "video");
            video.preload = "metadata";
            video.muted = true;
            video.playsInline = true;
            video.onclick = () => openViewer(item);
            card.appendChild(video);
        } else {
            const img = document.createElement("img");
            img.src = mediaURL(item.path, "image");
            img.alt = item.name;
            img.loading = "lazy";
            card.appendChild(img);
            card.onclick = () => openViewer(item);
        }

        const name = document.createElement("p");
        name.textContent = item.name;
        card.appendChild(name);
        folderGrid.appendChild(card);
    });

    if (!directFiles.length) {
        const note = document.createElement("p");
        note.className = "empty";
        note.textContent = "No media files directly inside this folder.";
        folderGrid.appendChild(note);
    }
}

function render() {

    if (folderMode) {
        gallery.hidden = true;
        folderBrowser.hidden = false;
        empty.hidden = true;
        renderFolderBrowser();
        return;
    }
    gallery.hidden = false;
    folderBrowser.hidden = true;

    const query = search.value.toLowerCase().trim();

    const filtered = allMedia.filter(item => {

        const matchesSearch =
            item.name.toLowerCase().includes(query);

        let matchesType = true;

        if (currentFilter === "videos") {
            matchesType = item.type === "video";
        } else if (currentFilter === "images") {
            matchesType =
                item.type === "image" && !item.isGif;
        } else if (currentFilter === "gifs") {
            matchesType = item.isGif;
        }

        return matchesSearch && matchesType;
    });

    gallery.innerHTML = "";

    filtered.forEach(item => {

        const card = document.createElement("div");
        card.className = "card";

        if (item.type === "video") {

            const video = document.createElement("video");
            video.src = mediaURL(item.path, "video");
            video.preload = "metadata";
            video.muted = true;
            video.playsInline = true;

            video.addEventListener("click", () => {
                openViewer(item);
            });

            card.appendChild(video);

        } else {

            const img = document.createElement("img");
            img.src = mediaURL(item.path, "image");
            img.alt = item.name;
            img.loading = "lazy";

            card.appendChild(img);

            card.onclick = () => openViewer(item);
        }

        const name = document.createElement("p");
        name.textContent = item.name;

        card.appendChild(name);
        gallery.appendChild(card);
    });

    empty.hidden = filtered.length !== 0;
}


/* ==================================================
   LOAD MEDIA
================================================== */

async function loadMedia() {

    try {

        const response = await fetch("/api/media");

        if (!response.ok) {
            throw new Error("Could not load media");
        }

        allMedia = await response.json();
        render();

    } catch (error) {

        gallery.innerHTML = "";
        empty.hidden = false;
        empty.textContent =
            "Unable to load media. Check the server.";
    }
}


/* ==================================================
   SEARCH AND FILTERS
================================================== */

search.addEventListener("input", () => {
    if (folderMode) {
        folderMode = false;
        currentFolder = "";
        foldersToggle.classList.remove("active");
        foldersToggle.textContent = "📁 View folders";
        document.getElementById("heading").textContent = "All Media";
    }
    render();
});

document.querySelectorAll("nav button").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelector("nav button.active")
            ?.classList.remove("active");

        button.classList.add("active");

        currentFilter = button.dataset.filter;
        folderMode = false;
        currentFolder = "";
        foldersToggle.classList.remove("active");
        foldersToggle.textContent = "📁 View folders";

        const headings = {
            all: "All Media",
            videos: "Videos",
            images: "Images",
            gifs: "GIFs"
        };

        document.getElementById("heading").textContent =
            headings[currentFilter];

        render();
    });
});


foldersToggle.addEventListener("click", () => {
    folderMode = !folderMode;
    currentFolder = "";
    foldersToggle.classList.toggle("active", folderMode);
    foldersToggle.textContent = folderMode ? "✕ Close folders" : "📁 View folders";
    document.getElementById("heading").textContent = folderMode ? "Folders" : "All Media";
    render();
});


/* START */

loadMedia();

</script>

</body>
</html>
"""


# ==================================================
# PYTHON SERVER
# ==================================================

class MediaHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(
            f"[{self.client_address[0]}] {format % args}"
        )

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(body)

    def safe_path(self, relative_path):

        relative_path = relative_path.replace("/", os.sep)

        base = os.path.realpath(MEDIA_DIR)
        target = os.path.realpath(
            os.path.join(base, relative_path)
        )

        try:
            if os.path.commonpath([base, target]) != base:
                return None
        except ValueError:
            return None

        return target

    def scan_media(self):

        media = []

        for root, dirs, files in os.walk(MEDIA_DIR):

            dirs.sort(key=str.lower)

            for filename in files:

                ext = os.path.splitext(filename)[1].lower()

                if ext in VIDEO_EXTENSIONS:
                    media_type = "video"

                elif ext in IMAGE_EXTENSIONS:
                    media_type = "image"

                else:
                    continue

                full_path = os.path.join(root, filename)

                relative_path = os.path.relpath(
                    full_path,
                    MEDIA_DIR
                )

                media.append({
                    "name": filename,
                    "path": relative_path.replace("\\", "/"),
                    "type": media_type,
                    "isGif": ext == ".gif"
                })

        media.sort(key=lambda x: x["name"].lower())

        return media

    def send_file(self, file_path, content_type, use_range=False):

        file_size = os.path.getsize(file_path)

        start = 0
        end = file_size - 1
        status = 200

        range_header = (
            self.headers.get("Range")
            if use_range else None
        )

        if range_header:

            match = re.fullmatch(
                r"bytes=(\d*)-(\d*)",
                range_header.strip()
            )

            if not match:
                self.send_response(416)
                self.send_header(
                    "Content-Range",
                    f"bytes */{file_size}"
                )
                self.end_headers()
                return

            first, last = match.groups()

            if not first and not last:
                self.send_response(416)
                self.send_header(
                    "Content-Range",
                    f"bytes */{file_size}"
                )
                self.end_headers()
                return

            if not first:

                length = int(last)

                if length <= 0:
                    self.send_response(416)
                    self.send_header(
                        "Content-Range",
                        f"bytes */{file_size}"
                    )
                    self.end_headers()
                    return

                start = max(0, file_size - length)

            else:

                start = int(first)

                if last:
                    end = int(last)

            if start >= file_size or start > end:
                self.send_response(416)
                self.send_header(
                    "Content-Range",
                    f"bytes */{file_size}"
                )
                self.end_headers()
                return

            end = min(end, file_size - 1)
            status = 206

        length = max(0, end - start + 1)

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))

        if status == 206:
            self.send_header(
                "Content-Range",
                f"bytes {start}-{end}/{file_size}"
            )

        self.send_header("Content-Disposition", "inline")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        if self.command == "HEAD":
            return

        with open(file_path, "rb") as file:

            file.seek(start)
            remaining = length

            while remaining > 0:

                chunk = file.read(
                    min(64 * 1024, remaining)
                )

                if not chunk:
                    break

                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):

        parsed = urlsplit(self.path)
        path = unquote(parsed.path)

        # HOME PAGE

        if path == "/":

            body = HTML.encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(body))
            )
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(body)

            return

        # MEDIA API

        if path == "/api/media":
            self.send_json(self.scan_media())
            return

        # VIDEO ROUTE

        if path.startswith("/video/"):

            relative = path[len("/video/"):]
            file_path = self.safe_path(relative)

            if not file_path or not os.path.isfile(file_path):
                self.send_error(404, "Video not found")
                return

            ext = os.path.splitext(file_path)[1].lower()

            if ext not in VIDEO_EXTENSIONS:
                self.send_error(403)
                return

            mime_type = mimetypes.guess_type(file_path)[0]

            self.send_file(
                file_path,
                mime_type or "application/octet-stream",
                use_range=True
            )

            return

        # IMAGE AND GIF ROUTE

        if path.startswith("/image/"):

            relative = path[len("/image/"):]
            file_path = self.safe_path(relative)

            if not file_path or not os.path.isfile(file_path):
                self.send_error(404, "Image not found")
                return

            ext = os.path.splitext(file_path)[1].lower()

            if ext not in IMAGE_EXTENSIONS:
                self.send_error(403)
                return

            mime_type = mimetypes.guess_type(file_path)[0]

            self.send_file(
                file_path,
                mime_type or "application/octet-stream"
            )

            return

        self.send_error(404, "Not found")


# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":

    if not os.path.isdir(MEDIA_DIR):
        raise SystemExit(
            f"Media folder not found: {MEDIA_DIR}"
        )

    server = ThreadingHTTPServer(
        (HOST, PORT),
        MediaHandler
    )

    print("\n" + "=" * 48)
    print("             MY MEDIA SERVER")
    print("=" * 48)
    print(f"Media folder : {MEDIA_DIR}")
    print(f"Port         : {PORT}")
    print("Laptop       : http://127.0.0.1:6789")
    print("Phone        : http://YOUR-LAPTOP-IP:6789")
    print("=" * 48)
    print("Press CTRL+C to stop the server.\n")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server.server_close()