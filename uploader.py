import logging
from instagrapi import Client

logger = logging.getLogger(__name__)


class InstagramUploader:
    """Uploads media to Instagram using Instagrapi."""

    def __init__(self, username: str, password: str):
        self.client = Client()
        if username and password:
            try:
                self.client.login(username, password)
                logger.info("Uploader logged in as %s", username)
            except Exception as exc:
                logger.error("Uploader login failed for %s: %s", username, exc)
                raise

    def upload(self, post: dict) -> None:
        """Upload a scraped *post* dict to the target Instagram account.

        Args:
            post: dict with keys shortcode, caption, media_paths, is_video
        """
        media_paths = post.get("media_paths", [])
        caption = post.get("caption", "")

        if not media_paths:
            raise ValueError(f"No media files found for post {post.get('shortcode')}")

        if len(media_paths) > 1:
            self._upload_album(media_paths, caption)
        elif post.get("is_video"):
            self._upload_video(media_paths[0], caption)
        else:
            self._upload_photo(media_paths[0], caption)

    def _upload_photo(self, path: str, caption: str) -> None:
        logger.info("Uploading photo: %s", path)
        self.client.photo_upload(path, caption=caption)

    def _upload_video(self, path: str, caption: str) -> None:
        logger.info("Uploading video: %s", path)
        self.client.video_upload(path, caption=caption)

    def _upload_album(self, paths: list, caption: str) -> None:
        logger.info("Uploading album (%d items)", len(paths))
        self.client.album_upload(paths, caption=caption)
