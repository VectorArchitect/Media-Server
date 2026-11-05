import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import media_server


class MediaServerPathTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "media"
        self.root.mkdir()
        self.handler = object.__new__(media_server.MediaHandler)
        self.media_dir_patch = patch.object(media_server, "MEDIA_DIR", str(self.root))
        self.media_dir_patch.start()

    def tearDown(self):
        self.media_dir_patch.stop()
        self.temp_dir.cleanup()

    def test_resolves_a_file_inside_media_directory(self):
        media_file = self.root / "movies" / "clip.mp4"
        media_file.parent.mkdir()
        media_file.write_bytes(b"video")

        self.assertEqual(
            self.handler.safe_path("movies/clip.mp4"),
            os.path.realpath(media_file),
        )

    def test_rejects_parent_directory_traversal(self):
        outside_file = Path(self.temp_dir.name) / "private.txt"
        outside_file.write_text("not media", encoding="utf-8")

        self.assertIsNone(self.handler.safe_path("../private.txt"))

    def test_rejects_absolute_paths_outside_media_directory(self):
        outside_file = Path(self.temp_dir.name) / "private.txt"

        self.assertIsNone(self.handler.safe_path(str(outside_file)))

    def test_rejects_symlink_that_escapes_media_directory(self):
        outside_dir = Path(self.temp_dir.name) / "outside"
        outside_dir.mkdir()
        link = self.root / "escape"

        try:
            link.symlink_to(outside_dir, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"Directory symlinks are unavailable: {error}")

        self.assertIsNone(self.handler.safe_path("escape/private.mp4"))

    def test_scan_media_includes_supported_files_only(self):
        (self.root / "movie.mp4").write_bytes(b"video")
        (self.root / "poster.png").write_bytes(b"image")
        (self.root / "animation.gif").write_bytes(b"gif")
        (self.root / "notes.txt").write_text("ignore", encoding="utf-8")

        media = self.handler.scan_media()
        by_name = {item["name"]: item for item in media}

        self.assertEqual(set(by_name), {"movie.mp4", "poster.png", "animation.gif"})
        self.assertEqual(by_name["movie.mp4"]["type"], "video")
        self.assertEqual(by_name["poster.png"]["type"], "image")
        self.assertTrue(by_name["animation.gif"]["isGif"])


if __name__ == "__main__":
    unittest.main()
