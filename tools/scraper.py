import asyncio
from typing import List
from models import TrendData
try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
import random

class PlaywrightScraper:
    def __init__(self):
        self.headless = True # Set to False if you want to see the browser for debugging

    async def scrape_trends(self, keywords: List[str], max_count: int = 5) -> List[TrendData]:
        """
        Scrapes TikTok trends using Playwright in parallel for speed.
        """
        query = " ".join(keywords)
        tag = keywords[0].replace(" ", "").replace("#", "") if keywords else "viral"
        
        # Sources to try in parallel
        sources = [
            f"https://www.tiktok.com/tag/{tag}",
            f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"
        ]
        
        trends = []
        if not HAS_PLAYWRIGHT:
            print("--- Playwright not installed. Using Strategic Topic Fallback ---")
            trends.append(TrendData(
                video_id="strategic_fallback_no_playwright",
                description=f"Strategic hook based on latest {query} discussions (No Discovery Engine).",
                hashtags=["viral", query.split()[0]],
                author="StrategyBot",
                url=f"https://www.google.com/search?q={query.replace(' ', '+')}",
                transcript="System-generated strategic insight based on topic keyword."
            ))
            return trends

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            # Speed Hack: Block all non-essential resources
            async def block_resources(route):
                if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]:
                    await route.abort()
                else:
                    await route.continue_()
            
            async def try_url(url):
                page = await context.new_page()
                await page.route("**/*", block_resources)
                try:
                    print(f"--- Fast Discovery Attempt: {url} ---")
                    # Increased timeout and domcontentloaded for the parallel part
                    await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                    # Smart Wait: wait for a common video container
                    try:
                        await page.wait_for_selector('a[href*="/video/"]', timeout=7000)
                    except:
                        pass 
                        
                    results = []
                    video_links = await page.query_selector_all('a[href*="/video/"]')
                    for link in video_links:
                        if len(results) >= max_count: break
                        href = await link.get_attribute("href")
                        if not href: continue
                        
                        img = await link.query_selector("img")
                        desc = (await img.get_attribute("alt") if img else "Viral content") or "No description"
                        
                        parts = href.split("/")
                        author = parts[3].replace("@", "") if len(parts) > 3 else "unknown"
                        
                        results.append(TrendData(
                            video_id=href.split("/")[-1],
                            description=desc,
                            hashtags=[tag, "trending"],
                            author=author,
                            url=href,
                            transcript=""
                        ))
                    return results
                except Exception as e:
                    print(f"Parallel Scrape Error ({url}): {e}")
                    return []
                finally:
                    await page.close()

            # Run TikTok attempts in parallel
            task_results = await asyncio.gather(*[try_url(u) for u in sources])
            for res in task_results:
                for trend in res:
                    if not any(t.url == trend.url for t in trends):
                        trends.append(trend)
            
            if not trends:
                print("--- TikTok blocked. Pivoting to Deep Web Discovery ---")
                temp_page = await context.new_page()
                await temp_page.route("**/*", block_resources)
                trends = await self.scrape_web_trends(temp_page, query, max_count)
                await temp_page.close()
            
            # LAST HOPE Fallback: If absolutely nothing found, create a "Topic-Based" trend record
            if not trends:
                print("--- External Discovery Failed. Using Strategic Topic Fallback ---")
                trends.append(TrendData(
                    video_id="strategic_fallback",
                    description=f"Strategic hook based on latest {query} discussions.",
                    hashtags=["viral", query.split()[0]],
                    author="StrategyBot",
                    url=f"https://www.google.com/search?q={query.replace(' ', '+')}",
                    transcript="System-generated strategic insight based on topic keyword."
                ))
                
            await browser.close()
            
        return trends

    async def scrape_web_trends(self, page, query: str, max_count: int) -> List[TrendData]:
        """
        Fallback: Scrapes current trends/news from the web using DuckDuckGo.
        """
        search_urls = [
            f"https://duckduckgo.com/?q={query.replace(' ', '+')}+trending+news&iar=news",
            f"https://duckduckgo.com/?q={query.replace(' ', '+')}+latest+trends",
            f"https://www.google.com/search?q={query.replace(' ', '+')}+news&tbm=nws"
        ]
        
        trends = []
        for search_url in search_urls:
            try:
                print(f"--- Deep Web Discovery Attempt: {search_url} ---")
                try:
                    # Longer timeout for the fallback, and allow partial load
                    await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                except Exception as goto_error:
                    print(f"Navigation Warning: {goto_error}")
                    # Continue anyway, results might have started loading
                
                await asyncio.sleep(3) # Wait for JS rendering
                
                selectors = [
                    'a[data-testid="result-title-a"]', 
                    'a.result__a', 
                    '.result__title a',
                    'h3 a', # Google news selector
                    'h2 a'
                ]
                
                results = []
                for sel in selectors:
                    results = await page.query_selector_all(sel)
                    if results: break

                for res in results[:max_count]:
                    try:
                        title = await res.inner_text()
                        link = await res.get_attribute("href")
                        if not title or not link or link.startswith("/") or "http" not in link: continue
                        
                        trends.append(TrendData(
                            video_id=str(random.randint(1000, 9999)),
                            description=f"TRENDING: {title}",
                            hashtags=["viral", "news", query.split()[0]],
                            author="WebSearch",
                            url=link,
                            transcript="Real-time trend discovered via deep web search."
                        ))
                    except:
                        continue
                if trends: break 
            except Exception as e:
                print(f"Web Search Discovery Error ({search_url}): {e}")
            
        return trends

scraper = PlaywrightScraper()

async def fetch_trends(topic: str) -> List[TrendData]:
    """
    Native async wrapper for the discovery engine.
    """
    print(f"--- Fetching Trends Async: {topic} ---")
    return await scraper.scrape_trends(topic.split(" "))
