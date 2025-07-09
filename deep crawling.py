#give the url of you choice of line no:62
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig,CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from base64 import b64decode
import logging
import os
import sys
from PIL import Image # Import Pillow for image manipulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),     # Log to file
        logging.StreamHandler(sys.stdout)       # Also show in console
    ]
)

# Define output folders and filenames
CRAWL_OUTPUT_FOLDER = "deep_crawling_output_folder"
output_path = os.path.join(os.getcwd(), CRAWL_OUTPUT_FOLDER)
PDF_OUTPUT_FILENAME = "crawled_pages_screenshots.pdf"

# Create the output directory if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)
    logging.info(f"Created output directory: {output_path}")
else:
    logging.info(f"Output directory already exists: {output_path}")

async def main():
    """
    Main function to perform deep crawling, save screenshots, and combine them into a PDF.
    """
    # Configure a 2-level deep crawl and enable screenshot capture
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2,          # Crawl up to 2 levels deep from the starting URL
            include_external=False # Do not crawl external links
        ),
        scraping_strategy=LXMLWebScrapingStrategy(), # Use LXML for content scraping
        screenshot=True,  # Crucially, enable screenshot capture for each page
        verbose=True,              # Enable verbose logging for the crawler
        cache_mode=CacheMode.BYPASS,
        scan_full_page=True,
        wait_for_images=True,
        pdf=True
        # --- NEW: Added timeouts to allow more time for page and image loading ---
        #wait_for_images_timeout=15000, # Increased timeout to 15 seconds (default is usually 5s)
        #page_load_timeout=30000        # Increased page load timeout to 30 seconds (default is usually 15s)

    )

    screenshot_files = [] # List to store paths of saved screenshots for PDF creation

    logging.info("Starting web crawling process...")
    async with AsyncWebCrawler() as crawler:
        # Start the deep crawl from the specified URL
        results = await crawler.arun("https://endeavourtechnology.com/", config=config)

        logging.info(f"Crawled {len(results)} pages in total.")

        # Process each crawled result
        for i, result in enumerate(results):
            if result.screenshot:
                screenshot_base64_data = result.screenshot
                # Sanitize URL to create a valid and somewhat descriptive filename
                # Replace non-alphanumeric characters with underscores
                page_url_safe = "".join([c if c.isalnum() else "_" for c in result.url])
                # Create a unique filename for each screenshot
                screenshot_filename = f"page_{i+1}_{page_url_safe[:100]}.png" # Limit URL segment to 100 chars
                screenshot_file_path = os.path.join(output_path, screenshot_filename)

                try:
                    # Decode the base64 screenshot data and save it as a PNG file
                    with open(screenshot_file_path, "wb") as f:
                        f.write(b64decode(screenshot_base64_data))
                    logging.info(f"Screenshot saved for {result.url} to: {screenshot_file_path}")
                    screenshot_files.append(screenshot_file_path) # Add to list for PDF creation
                except Exception as e:
                    logging.error(f"Error saving screenshot file for {result.url}: {e}")
            else:
                logging.warning(f"No screenshot captured for URL: {result.url}")

    # --- Combine screenshots into a single PDF ---
    logging.info("Attempting to combine captured screenshots into a PDF...")
    if screenshot_files:
        try:
            images = []
            for img_path in screenshot_files:
                img = Image.open(img_path)
                # Convert image to 'RGB' mode if it's 'RGBA' (with alpha channel),
                # as PDF saving generally prefers 'RGB'.
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                images.append(img)

            pdf_output_path = os.path.join(output_path, PDF_OUTPUT_FILENAME)

            if images: # Ensure there's at least one image to save
                if len(images) == 1:
                    # If only one image, save it directly as a PDF
                    images[0].save(pdf_output_path)
                    logging.info(f"Saved single screenshot as PDF: {pdf_output_path}")
                else:
                    # Save the first image, appending all subsequent images to create a multi-page PDF
                    images[0].save(pdf_output_path, save_all=True, append_images=images[1:])
                    logging.info(f"Combined {len(images)} screenshots into PDF: {pdf_output_path}")
            else:
                logging.warning("No images were loaded to create the PDF. This might happen if screenshot files were empty or corrupted.")

        except Exception as e:
            logging.error(f"Error combining screenshots into PDF: {e}")
    else:
        logging.warning("No screenshots were captured during the crawl. Skipping PDF creation.")

    logging.info("Web crawling and PDF generation process completed.")

if __name__ == "__main__":
    asyncio.run(main())
