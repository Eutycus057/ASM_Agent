import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Monitor console
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"BROWSER ERROR: {exc}"))
        
        print("Navigating to http://localhost:8000...")
        await page.goto("http://localhost:8000")
        await asyncio.sleep(5)  # Wait for posts to load
        
        # Check for post-visual and video
        video_exists = await page.evaluate('''() => {
            const video = document.querySelector('video');
            return video ? { 
                src: video.src, 
                visible: video.offsetParent !== null,
                hiddenClass: video.classList.contains('hidden')
            } : null;
        }''')
        print(f"Video state: {video_exists}")
        
        # Simulating hover
        print("Simulating hover...")
        await page.hover('.post-visual')
        await asyncio.sleep(2)
        
        # Check if playing
        is_playing = await page.evaluate('''() => {
            const video = document.querySelector('video');
            return video && !video.paused;
        }''')
        print(f"Is video playing after hover? {is_playing}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
