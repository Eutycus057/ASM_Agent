import asyncio
from tools.scraper import scraper

async def main():
    print("Testing Scraper...")
    try:
        trends = await scraper.scrape_trends(["AI", "Knowledge"], max_count=2)
        print(f"Found {len(trends)} trends.")
        for t in trends:
            print(f"- {t.description} (URL: {t.url})")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
