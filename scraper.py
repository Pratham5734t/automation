import os
import logging
import instaloader

logger = logging.getLogger(__name__)


class InstagramScraper:
    """Scrapes posts from Instagram accounts using Instaloader."""

    def __init__(self, username: str, password: str, downloads_dir: str = "downloads"):
        self.downloads_dir = downloads_dir
        os.makedirs(downloads_dir, exist_ok=True)
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            post_metadata_txt_pattern="",
            dirname_pattern=downloads_dir + "/{target}",
            filename_pattern="{shortcode}",
            quiet=True,
        )
        if username and password:
            try:
                self.loader.login(username, password)
                logger.info("Logged in to Instagram as %s", username)
            except Exception as exc:
                logger.warning("Could not log in as %s: %s", username, exc)

    def fetch_posts(self, account: str, max_posts: int = 5) -> list:
        """Fetch up to *max_posts* recent posts from *account*.

        Returns a list of dicts with keys:
          - shortcode (str)
          - caption (str)
          - media_paths (list of str)
          - is_video (bool)
        """
        profile = instaloader.Profile.from_username(self.loader.context, account)
        posts = []
        for post in profile.get_posts():
            if len(posts) >= max_posts:
                break
            media_paths = self._download_post(post)
            posts.append(
                {
                    "shortcode": post.shortcode,
                    "caption": post.caption or "",
                    "media_paths": media_paths,
                    "is_video": post.is_video,
                }
            )
        return posts

    def _download_post(self, post) -> list:
        """Download all media for *post* and return a list of local file paths."""
        self.loader.download_post(post, target=post.owner_username)
        post_dir = os.path.join(self.downloads_dir, post.owner_username)
        paths = []
        if post.typename == "GraphSidecar":
            for index, node in enumerate(post.get_sidecar_nodes()):
                ext = ".mp4" if node.is_video else ".jpg"
                path = os.path.join(post_dir, f"{post.shortcode}_{index + 1}{ext}")
                if os.path.exists(path):
                    paths.append(path)
        else:
            ext = ".mp4" if post.is_video else ".jpg"
            path = os.path.join(post_dir, f"{post.shortcode}{ext}")
            if os.path.exists(path):
                paths.append(path)
        return paths
