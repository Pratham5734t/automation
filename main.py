import os
import logging
from dotenv import load_dotenv

from scraper import InstagramScraper
from uploader import InstagramUploader
from storage import PostStorage
from notifier import TelegramNotifier

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    accounts = [a.strip() for a in os.getenv("ACCOUNTS_TO_SCRAPE", "").split(",") if a.strip()]
    max_posts = int(os.getenv("MAX_POSTS_PER_ACCOUNT", 5))
    downloads_dir = "downloads"

    storage = PostStorage(os.getenv("HISTORY_FILE", "history.xlsx"))
    notifier = TelegramNotifier(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    )
    scraper = InstagramScraper(
        username=os.getenv("SOURCE_USERNAME"),
        password=os.getenv("SOURCE_PASSWORD"),
        downloads_dir=downloads_dir,
    )
    uploader = InstagramUploader(
        username=os.getenv("TARGET_USERNAME"),
        password=os.getenv("TARGET_PASSWORD"),
    )

    uploaded = 0
    failed = 0

    if not accounts:
        logger.warning("No accounts configured in ACCOUNTS_TO_SCRAPE – nothing to do")
        return

    for account in accounts:
        logger.info("Scraping posts from @%s", account)
        try:
            posts = scraper.fetch_posts(account, max_posts=max_posts)
        except Exception as exc:
            logger.error("Failed to scrape @%s: %s", account, exc)
            notifier.send(f"❌ Failed to scrape @{account}: {exc}")
            failed += 1
            continue

        for post in posts:
            shortcode = post["shortcode"]
            if storage.already_posted(shortcode):
                logger.info("Skipping already posted: %s", shortcode)
                continue

            logger.info("Uploading post %s from @%s", shortcode, account)
            try:
                uploader.upload(post)
                storage.mark_posted(shortcode, account)
                notifier.send(f"✅ Uploaded post {shortcode} from @{account}")
                uploaded += 1
            except Exception as exc:
                logger.error("Failed to upload %s: %s", shortcode, exc)
                notifier.send(f"❌ Failed to upload {shortcode} from @{account}: {exc}")
                failed += 1

    summary = f"Run complete. Uploaded: {uploaded}, Failed: {failed}"
    logger.info(summary)
    notifier.send(f"📊 {summary}")


if __name__ == "__main__":
    main()
