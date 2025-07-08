from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
import asyncio
import logging
import sys
import os
from base64 import b64decode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Output directory setup
CRAWL_OUTPUT_FOLDER = "simple_crawl_output"
output_path = os.path.join(os.getcwd(), CRAWL_OUTPUT_FOLDER)
os.makedirs(output_path, exist_ok=True)

# Target URL
target_url = "https://en.wikipedia.org/wiki/Giant_anteater"

# Define crawler run configuration
crawler_config = CrawlerRunConfig(
    screenshot=True,         # Capture screenshot
    verbose=True,            # Verbose logging
    cache_mode=CacheMode.BYPASS,
    scan_full_page=True,
    wait_for_images=True,
    pdf=True                 # Export as PDF
)

async def simple_crawl():
    async with AsyncWebCrawler() as crawler:
        logging.info(f"Crawling: {target_url}")
        result = await crawler.arun(
            url=target_url,
            config=crawler_config
        )

        logging.info(f"Page loaded with status: {result.status_code}")

        # Save HTML
        if result.html:
            html_path = os.path.join(output_path, "page.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(result.html)
            logging.info(f"HTML saved to: {html_path}")
        else:
            logging.warning("No HTML content retrieved.")

        # Save Markdown
        if result.markdown:
            md_path = os.path.join(output_path, "page.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)
            logging.info(f"Markdown saved to: {md_path}")
        else:
            logging.warning("No Markdown content available.")

        # Save Screenshot
        if result.screenshot:
            screenshot_path = os.path.join(output_path, "page.png")
            with open(screenshot_path, "wb") as f:
                screenshotbase64 = result.screenshot
                #f.write(result.screenshot)
                f.write(b64decode(screenshotbase64))

            logging.info(f"Screenshot saved to: {screenshot_path}")
        else:
            logging.warning("No screenshot captured.")

        # Save PDF
        if result.pdf:
            pdf_path = os.path.join(output_path, "page.pdf")
            with open(pdf_path, "wb") as f:
                f.write(result.pdf)
            logging.info(f"PDF saved to: {pdf_path}")
        else:
            logging.warning("No PDF content available.")

if __name__ == "__main__":
    asyncio.run(simple_crawl())
